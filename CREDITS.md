# CREDITS

Every fix and feature in this fork that originates from the upstream Blender
tracker is listed here, with a link to the original pull request and its
author, plus the local commit(s) that carry it.

Upstream tracker: <https://projects.blender.org/blender/blender>
(GitHub's `blender/blender` is a read-only mirror — issues and PRs live on
projects.blender.org.)

**Conventions**

- Local commits are listed newest-last, short SHA.
- "Upstream status" is the PR state at the time it was ported; `merged` means
  upstream landed it themselves (our copy is then a local duplicate of that
  change).
- Changes made in this fork without an upstream PR (branding, menu restructures)
  are listed under [Original work](#original-work).

---

## Ported pull requests

### UI, menus and editors

| PR | Title | Author | Upstream | Local commits |
|---|---|---|---|---|
| [!165934](https://projects.blender.org/blender/blender/pulls/165934) | Fix #165908: Recent Files is not sorted by modified date | PratikPB2123 | open | `874a5b6389b` |
| [!165376](https://projects.blender.org/blender/blender/pulls/165376) | Fix: UI: logic for operator call context from menus | lichtwerk | open | `e3fb7b26821`, `8dea88d4a7b` |
| [!161011](https://projects.blender.org/blender/blender/pulls/161011) | UI: Polish pass for menus | nickberckley | open | `9faf588695f` |
| [!163120](https://projects.blender.org/blender/blender/pulls/163120) | UI: Remember file browser operator execution directory | guishe | open | `73b98cb6591` |
| [!162618](https://projects.blender.org/blender/blender/pulls/162618) | UI: Experiment: Preference for search menu items | PratikPB2123 | open | `f575029bc8a`, `097633e5874`, `0bea1520bbe`, `f28a66a4517` |
| [!163261](https://projects.blender.org/blender/blender/pulls/163261) | UI: Add Experimental data-block template menu | guishe | open | `b1b505c4626` |
| [!165209](https://projects.blender.org/blender/blender/pulls/165209) | UI: Include LoopTools in the editmesh context menu | Tariq-Sulley | open | `7741a2f4140` |
| [!164984](https://projects.blender.org/blender/blender/pulls/164984) | UI: Support dragging redo panel | PratikPB2123 | open | 17 commits, `383ebba815` … `1720783f490` |
| [!166033](https://projects.blender.org/blender/blender/pulls/166033) | Fix #164639: UI: Hide Grease Pencil primitive tool settings in Active Tool panel | Anvesh-Mishra | merged 2026-11-05 | `1aec8b3030` |
| [!166069](https://projects.blender.org/blender/blender/pulls/166069) | UI: pass bContext to `AbstractViewItem::set_selected()` | dr.sybren | merged 2026-11-05 | `0cdd998470a` |
| [!164079](https://projects.blender.org/blender/blender/pulls/164079) | Fix: Prevent changing space type of filebrowser and global regions | guishe | open | 5 commits, `09f00c840a` … `1aa13af3e9` |
| [!143310](https://projects.blender.org/blender/blender/pulls/143310) | File Browser: move location preferences into file browser | RedMser | open | 4 commits, `7c71f0c0c6c` … `82f647270c5` |
| [!165356](https://projects.blender.org/blender/blender/pulls/165356) | UI: Reorder workspace with dragdrop | PratikPB2123 | open | `abd3ccceefc`, `608e2cad238`, `169d15224e8` (conflicts resolved locally) |

### File I/O, import/export

| PR | Title | Author | Upstream | Local commits |
|---|---|---|---|---|
| [!162495](https://projects.blender.org/blender/blender/pulls/162495) | IO: Speed Up STL and PLY Exporters When Using Viewport Settings | Matej-Kotas | open | `bf5065c505` |
| [!166005](https://projects.blender.org/blender/blender/pulls/166005) | IO: Add new `collection_import_enabled` option to `FileHandlerType` | deadpin | merged 2026-11-04 | `ba80a27930f` |
| [!164709](https://projects.blender.org/blender/blender/pulls/164709) | Assets: import asset operator | RedMser | open | `42d7ee9675d` |
| [!163539](https://projects.blender.org/blender/blender/pulls/163539) | Fix: use-after-free when import handler deletes imported data | Dan-Oak | open | `39d7c6778dc` |
| [!163211](https://projects.blender.org/blender/blender/pulls/163211) | USD: Exporter: use a textbox for the Accessibility Description | kevindietrich | open | `4ccb8690c48` |
| [!165562](https://projects.blender.org/blender/blender/pulls/165562) | Alembic import more points attributes | Lars-Helge-Scheel | open | 12 commits, `12985e4117` … `d0f5d22291` |

### Performance, rendering and core

| PR | Title | Author | Upstream | Local commits |
|---|---|---|---|---|
| [!164791](https://projects.blender.org/blender/blender/pulls/164791) | VSE: Do not prefetch before the playhead during playback to improve performance | johnkiril | open | `4a3a7f9bbe`, `4808cda086e` |
| [!163554](https://projects.blender.org/blender/blender/pulls/163554) | Fix #163433: Image: Memory cache limit of 0 disables eviction | johnkiril | open | `e433f4999ea` |
| [!145192](https://projects.blender.org/blender/blender/pulls/145192) | Draw: 2D editors scene sync optimization | pragma37 | open | `1722f1d726b` |
| [!165350](https://projects.blender.org/blender/blender/pulls/165350) | Fix #165316: Movie clip editor timeline does not wrap mouse cursor | PratikPB2123 | open | `74b86927ae` |
| [!165962](https://projects.blender.org/blender/blender/pulls/165962) | Fix #163740: Make animated geometry node inputs show properly in graph editor | Matej-Kotas | open | `051e43e4f2` |
| [!165279](https://projects.blender.org/blender/blender/pulls/165279) | Fix #161014: Vulkan: Only assert on missing point size for internal shaders | rajaryan-2 | open | `84dbad2c989`, `77dbe82f2d` |
| [!162846](https://projects.blender.org/blender/blender/pulls/162846) | Shader Nodes: Move bundle and closure nodes to dedicated submenus | quackarooni | open | `82932dc8249` |

**Total: 26 ported pull requests.**

---

## Original work

Changes made in this fork that do not come from an upstream PR:

| Change | Local commit |
|---|---|
| Window title branding: "Blender - Gordon Greedman Version - \<version\>" (`wm_window.cc`) | `db93a5052fd` |
| File ▸ Export: less-used formats grouped under an **Other Formats** sub-menu | `e008d165e21` |
| File ▸ Import: less-used formats grouped under an **Other Formats** sub-menu | `3dc1586d805` |

---

## Skipped

| PR | Title | Why |
|---|---|---|
| [!164394](https://projects.blender.org/blender/blender/pulls/164394) | Sound: Improve audio animation cache handling | 54-file rework, too large to port safely |

---

## Known leftovers

- `!165356` was ported through a partially-applied patch; its first commit
  (`abd3ccceefc`) left a redundant global-scope declaration of
  `context_mouse_over_but_get_tab_ID` in `source/blender/editors/include/UI_interface_c.hh`
  (the implementation lives in `interface_template_id.cc`). Harmless — just a
  declaration — but it could be cleaned up.