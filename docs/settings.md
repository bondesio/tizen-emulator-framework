# Settings, library and navigation conventions

Use one Settings screen with these groups in this order. Headers and rules are
decoration: the selection index addresses only actionable rows.

| Group | Rows, in order |
| --- | --- |
| CONTROLLERS | P1 device; P2 device/None; Exclusive capture On/Off; Map P1; Map P2; guided raw-input diagnostic |
| AUDIO | Volume; Mute; system-specific audio options, if useful |
| VIDEO | Screen size/integer scale; filtering; scanlines; system-specific palette/LCD/color options |
| SYSTEM | Core mode/region/timing where applicable; Performance overlay (Off / FPS / Detailed); Rescan library; Back to library; Exit app |

Omit unsupported rows, including P2 gameplay for a single-player core. A device
picker for an optional alternative controller must not imply two-player support
that the emulated hardware lacks. Keep the remaining order stable. Do not expose
developer-only internals as settings without an actual user decision to make.
Save changed values and validate them at startup; explain next-game-only options
in the selected row's hint. Distinguish a video option from a core timing option.

This order generalizes the existing sources: TizGB uses Controller / Audio /
Video / System; TizNES uses Controllers / Audio / Game and library / System
because it has no Video group. TizGBA's brief already requests the generalized
Controllers / Audio / Video / System order. This kit does not rewrite either app.

## Library screen

Every emulator's game list has the same fixed shape
([library_rows.h](../snippets/library_rows.h); reference: TizGBA):

| Row | Content |
| --- | --- |
| 0 | **Exit \<App\>**: always the first selectable row, closes the app completely |
| 1 … N | Games, sorted; game index = row − 1 |
| N + 1 | **Settings and controller setup**: always the last row |

Both fixed rows exist with zero games. Exit is a row, not only a Settings entry,
so the app can be closed from the remote or a gamepad without opening Settings or
relying on Home/Back, which Tizen can intercept. While a library scan message is
up, ignore OK on game rows and Settings but never on Exit. Keep the Settings →
System **Exit app** row as well.

**Starting selection:** the first game when there is one, otherwise the Settings
row; never Exit, so an accidental OK cannot close the app. After a rescan keep
the same game (match by path), keep Settings if it was selected, and otherwise
clamp. TizGB 1.2.0, TizNES 1.1.0, TizGBA 0.2.0, TizNeo 0.3.0 and TizPSX 0.3.0
all follow this layout (2026-10-26).

Row indices: keep one selection variable that is a *row* (0 = Exit, game =
row − 1, Settings = n + 1). A separate game-index variable (for example the
played ROM, to restore the cursor after leaving a game) must add 1 when it is
written back to the row variable.

## Input behavior

| Context | Remote | Either assigned gamepad in menus |
| --- | --- | --- |
| Library | Up/Down select; OK exits (row 0), opens a game, or opens the trailing Settings row | D-pad selects; A activates; Start opens Settings |
| Settings | Up/Down select rows; Left/Right adjust; OK activates; Back returns to library | D-pad selects/adjusts; A activates; B or Start returns to library |
| Device picker | Up/Down select; OK assigns; Back cancels | D-pad selects; A assigns; B cancels |
| Mapping | Back cancels | Release between prompts, then press the requested control |
| Guided diagnostic | OK skips a prompt; Back cancels | Press the prompted control; log raw events |
| Gameplay | Back stops game and returns to library | Emulated controls, plus documented app escape/menu gesture |

Keep gameplay/mapping tied to the intended player slot. The guided raw-input
diagnostic targets P1, as it does in TizNES. For simultaneous menu input, merge
the pads' action bits and neutralize opposing directions rather than treating
one physical press as two navigation steps.

Keep selection bounded at the first/last row, matching TizNES/TizGB; headers
never consume a D-pad step. Include the trailing **Settings** library row even
with zero ROMs: Menu/Home can be intercepted by Tizen. Do not rely on those keys
as the sole path to settings or to leaving gameplay. Keep the real TV remote
usable during capture. Clear held bits when changing screens so the activating
press cannot launch a game or advance multiple mapping steps.

TizNES maps controls as they are completed; cancelling does not imply a full
transaction rollback. Match that behavior honestly or stage and commit a full
mapping deliberately. Avoid promising cancellation semantics the code lacks.

## Evas implementation pattern

Copy/adapt [settings_rows.h](../snippets/settings_rows.h). Keep a row enum with
only selectable IDs and a separate `{ first_row, title }` table. During render:

1. Before each section's first row, draw its title and rule; add header height.
2. Render that row at the current y; compare its ID to the **settings** selection
   index for both the text color and cursor position.
3. Advance by row height. Compute the footer from the same selected row.

Do not reuse the library index for a Settings highlight. TizNeo previously had
that mismatch. Hide library objects on entry and hide settings objects on exit.
Preserve independent selections for nested pickers.

TizNES's proven 1920×1080 coordinates are a useful reference: content left
360 px, rows left 390 px, top 194 px, title/rule block 44 px, section gap 14 px,
row height 40 px, rule width 1200 px, cursor 8×30 px at row y+4. TizGB uses
`Sans` text, white selection, gray `(180,180,180)` inactive settings text,
cyan `(120,200,255)` cursor and muted `(60,90,120)` section rules on
`(12,14,20)` background.

With the Performance overlay row a full two-controller Settings page has 15
rows; at 40 px that overruns the footer (last row ends at y=1012), so TizGB and
TizNES use a 37 px row pitch (last row ends near y=970). TizGBA pages whole
sections and TizNeo/TizPSX already use 34 px rows.

These are **reference design units**, not an assumed physical canvas. Read the
actual canvas dimensions. The full two-controller template has more rows than
fit at 40 px plus four headings on 1080p; use a scroll viewport with a fixed
footer and keep the selected row visible. Scale design coordinates uniformly
for other resolutions; keep real game rendering/integer scale separate from
menu layout. Check long controller labels and localized strings in that viewport.
