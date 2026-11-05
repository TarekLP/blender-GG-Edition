# SPDX-License-Identifier: GPL-2.0-or-later
"""Sketch to blockout: freehand sketching in the 3D view.

Phase 1 (`bpy.ops.sketch.stroke`): modal freehand stroke with live preview,
confirming creates a poly curve object.
Phase 2 (`bpy.ops.sketch.blockout`): sweeps a rectangular cross-section along
the stroke to produce a blockout mesh.

Both operators only use Python, the viewport draw handlers and `mathutils`,
so no C API additions are needed.
"""

import bpy
import gpu
from bpy_extras.view3d_utils import region_2d_to_location_3d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

bl_info = {
    "name": "Sketch to Blockout",
    "author": "Gordon Greedman Edition",
    "version": (1, 0, 0),
    "blender": (5, 4, 0),
    "location": "3D Viewport > Sidebar > Sketch",
    "description": "Freehand sketch strokes that turn into blockout geometry",
    "category": "3D View",
}


# ---------------------------------------------------------------------------
# Geometry helpers (pure functions, usable and testable without a viewport).
# ---------------------------------------------------------------------------

def stroke_frames(points):
    """Per-point orthonormal frames: (position, side, normal)."""
    up = Vector((0.0, 0.0, 1.0))
    frames = []
    count = len(points)
    for i, point in enumerate(points):
        if i == 0:
            tangent = points[1] - points[0]
        elif i == count - 1:
            tangent = points[-1] - points[-2]
        else:
            tangent = points[i + 1] - points[i - 1]
        if tangent.length < 1e-8:
            tangent = Vector((1.0, 0.0, 0.0))
        tangent.normalize()

        side = tangent.cross(up)
        if side.length < 1e-6:
            # Stroke runs along world Z, fall back to world Y as reference.
            side = tangent.cross(Vector((0.0, 1.0, 0.0)))
        side.normalize()
        normal = side.cross(tangent).normalized()
        frames.append((point, side, normal))
    return frames


def build_blockout(points, width=0.2, height=0.2):
    """Sweep a rectangular cross-section along `points`.

    Returns (vertices, faces) suitable for `mesh.from_pydata`.
    """
    if len(points) < 2:
        return [], []

    half_w = width * 0.5
    half_h = height * 0.5
    corners = (
        Vector((-half_w, -half_h)),
        Vector((half_w, -half_h)),
        Vector((half_w, half_h)),
        Vector((-half_w, half_h)),
    )

    vertices = []
    for point, side, normal in stroke_frames(points):
        for corner in corners:
            vertices.append(point + side * corner.x + normal * corner.y)

    faces = []
    rings = len(points)
    for ring in range(rings - 1):
        base = ring * 4
        nxt = base + 4
        for corner in range(4):
            following = (corner + 1) % 4
            faces.append((
                base + corner,
                base + following,
                nxt + following,
                nxt + corner,
            ))
    # End caps.
    faces.append((3, 2, 1, 0))
    last = (rings - 1) * 4
    faces.append((last + 0, last + 1, last + 2, last + 3))
    return vertices, faces


def curve_points_to_3d(obj, depsgraph=None):
    """Extract the stroke points of a curve (or mesh) object as 3D vectors."""
    data = obj.data
    if isinstance(data, bpy.types.Curve):
        points = []
        for spline in data.splines:
            if spline.type != 'POLY':
                # Fall back to the evaluated curve so bezier strokes work too.
                evaluated = obj.evaluated_get(depsgraph) if depsgraph else obj
                data = evaluated.data
                for spline_eval in data.splines:
                    for point in spline_eval.points:
                        points.append(Vector(point.co[:3]))
                return points
            for point in spline.points:
                points.append(Vector(point.co[:3]))
        return points
    if isinstance(data, bpy.types.Mesh):
        return [Vector(vertex.co) for vertex in data.vertices]
    return []


# ---------------------------------------------------------------------------
# Phase 1: modal sketch stroke with live preview.
# ---------------------------------------------------------------------------

# Active stroke state, shared with the draw handler (which takes no arguments).
_active_stroke = None
_draw_handle = None


def _draw_callback():
    """Draw the stroke being sketched, in world space, every viewport redraw."""
    global _active_stroke
    if _active_stroke is None:
        return

    context = bpy.context
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return

    points = _active_stroke.points_3d(context)
    if len(points) < 2:
        return

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"position": [tuple(p) for p in points]})

    gpu.state.depth_test_set('NONE')
    gpu.state.line_width_set(3.0)
    shader.bind()
    shader.uniform_float("color", (1.0, 0.42, 0.08, 1.0))
    batch.draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.depth_test_set('LESS_EQUAL')


class SketchStroke:
    """Accumulated stroke: 2D region coordinates while drawing."""

    def __init__(self, min_distance=3):
        self.coords_2d = []
        self.min_distance = min_distance
        self.last_coord = None

    def add(self, coord):
        if self.last_coord is not None:
            dx = coord[0] - self.last_coord[0]
            dy = coord[1] - self.last_coord[1]
            if (dx * dx + dy * dy) < self.min_distance * self.min_distance:
                return False
        self.coords_2d.append(coord)
        self.last_coord = coord
        return True

    def points_3d(self, context):
        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return []
        depth = context.scene.cursor.location
        points = []
        for coord in self.coords_2d:
            point = region_2d_to_location_3d(region, rv3d, coord, depth)
            if point is not None:
                points.append(point)
        return points


class SKETCH_OT_stroke(bpy.types.Operator):
    """Sketch a freehand stroke in the 3D view, confirm with a click"""

    bl_idname = "sketch.stroke"
    bl_label = "Sketch Stroke"
    bl_options = {'REGISTER', 'UNDO'}

    min_distance: bpy.props.IntProperty(
        name="Min Distance",
        description="Minimum distance in pixels between stroke points",
        default=3,
        min=1,
        max=50,
    )

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        global _active_stroke, _draw_handle

        if context.region is None or context.region_data is None:
            self.report({'WARNING'}, "No 3D view region to sketch in")
            return {'CANCELLED'}

        _active_stroke = SketchStroke(min_distance=self.min_distance)
        _active_stroke.add((event.mouse_region_x, event.mouse_region_y))

        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (), 'WINDOW', 'POST_VIEW')
        context.area.tag_redraw()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global _active_stroke

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self.finish(context, confirm=True)
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            return self.finish(context, confirm=False)
        if event.type == 'MOUSEMOVE' and _active_stroke is not None:
            _active_stroke.add((event.mouse_region_x, event.mouse_region_y))
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def finish(self, context, confirm):
        global _active_stroke, _draw_handle

        points = _active_stroke.points_3d(context) if _active_stroke else []
        if _draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
            _draw_handle = None
        _active_stroke = None
        context.area.tag_redraw()

        if not confirm:
            return {'CANCELLED'}
        if len(points) < 2:
            self.report({'WARNING'}, "Stroke too short, nothing created")
            return {'CANCELLED'}

        obj = create_stroke_object(context, points)
        self.report({'INFO'}, f"Created {obj.name} with {len(points)} points")
        return {'FINISHED'}

    def cancel(self, context):
        self.finish(context, confirm=False)


def create_stroke_object(context, points, name="Sketch Stroke"):
    """Create a poly curve object through `points` in the active collection."""
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, position in zip(spline.points, points):
        point.co = (position.x, position.y, position.z, 1.0)

    obj = bpy.data.objects.new(name, curve)
    context.collection.objects.link(obj)
    return obj


# ---------------------------------------------------------------------------
# Phase 2: stroke -> blockout mesh.
# ---------------------------------------------------------------------------

class SKETCH_OT_blockout(bpy.types.Operator):
    """Sweep a rectangular cross-section along the stroke to build a blockout"""

    bl_idname = "sketch.blockout"
    bl_label = "Stroke to Blockout"
    bl_options = {'REGISTER', 'UNDO'}

    width: bpy.props.FloatProperty(
        name="Width", description="Cross-section width", default=0.2, min=0.0001)
    height: bpy.props.FloatProperty(
        name="Height", description="Cross-section height", default=0.2, min=0.0001)
    keep_source: bpy.props.BoolProperty(
        name="Keep Source", description="Keep the sketch curve after building",
        default=True)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and isinstance(obj.data, (bpy.types.Curve, bpy.types.Mesh))

    def execute(self, context):
        obj = context.active_object
        points = curve_points_to_3d(obj, context.evaluated_depsgraph_get())
        if len(points) < 2:
            self.report({'ERROR'}, "Stroke needs at least two points")
            return {'CANCELLED'}

        vertices, faces = build_blockout(points, width=self.width, height=self.height)
        mesh = bpy.data.meshes.new(f"{obj.name} Blockout")
        mesh.from_pydata([tuple(v) for v in vertices], [], faces)
        mesh.update()

        blockout = bpy.data.objects.new(f"{obj.name} Blockout", mesh)
        context.collection.objects.link(blockout)

        for polygon in mesh.polygons:
            polygon.use_smooth = False

        if not self.keep_source:
            bpy.data.objects.remove(obj, do_unlink=True)
            context.view_layer.objects.active = blockout

        self.report({'INFO'}, f"Built {blockout.name}: {len(vertices)} verts, {len(faces)} faces")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# UI.
# ---------------------------------------------------------------------------

class SKETCH_PT_sketch(bpy.types.Panel):
    bl_label = "Sketch to Blockout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Sketch"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("sketch.stroke")

        layout.separator()
        layout.operator("sketch.blockout")


_classes = (
    SKETCH_OT_stroke,
    SKETCH_OT_blockout,
    SKETCH_PT_sketch,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    global _draw_handle
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
