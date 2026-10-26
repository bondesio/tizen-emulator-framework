# Performance overlay (FPS counter)

A user setting that draws live performance text over the game. It is off by
default and costs nothing while off. Source: [perf_overlay.h](../snippets/perf_overlay.h)
(plain C, host-tested by `tests/test_perf_overlay.c`).

## Setting

| Item | Convention |
| --- | --- |
| Row | **Performance overlay** in Settings → SYSTEM (`S_PERF_OVERLAY` in [settings_rows.h](../snippets/settings_rows.h)) |
| Values | `Off` (0, default) / `FPS` (1) / `Detailed` (2); Left/Right cycle, OK also cycles |
| Persistence | Key `perf_overlay`, integer. Pass the loaded value through `perf_mode_sanitize()`; unknown values mean Off |
| Hint | "Shows emulation speed over the game. Takes effect immediately." |

It applies at once, including mid-game after returning from Settings. Do not
tie it to a game or ROM; it is one global value.

## Content

- **FPS**: `59.9 FPS`, the *emulated* frame rate over the last second, not the
  Evas redraw rate. A healthy core shows its native rate (e.g. 59.7 for GB/GBA,
  60.0 NTSC / 50.0 PAL for NES).
- **Detailed**: emulated vs. native FPS, average and worst per-frame work time
  (core step + convert + present), late frames, and the app's audio underrun
  count, e.g. `37.20 / 60.00 FPS  work 25.6 ms (max 31.0)  late 38  audio under 0`.
  Add a system-specific suffix (active filter, scale) via your own `snprintf`;
  keep it one line.

"Late" means the frame missed its pacing deadline. Pass whatever the app already
uses for its pacing stall counter. These are the same numbers the apps already
write to their runtime logs (`emu_fps_x100`, `stalls`, `late`).

## Wiring

1. Keep one `perf_stats` per running game. Call `perf_reset()` when a game
   starts, resumes from Settings/pause, or the core resets, so menu time never
   pollutes the window.
2. Time `work_ns` around the per-frame step/convert/present with the same
   monotonic clock the pacer uses, and call `perf_frame()` once per emulated
   frame. Skip it when the overlay is Off (the log-only counters can keep their
   own accounting).
3. `perf_frame()` returns 1 once per second. Only then call `perf_format()` and
   `evas_object_text_text_set()`; never rebuild text per frame.
4. Show/hide the text object with game visibility. Do not draw it on the
   library, Settings, picker or mapping screens.

## Drawing

- Top-right, inset 48 px (reference 1920×1080 design units) from each edge to
  stay clear of TV overscan; scale with the real canvas like menu layout.
- `Sans`, about 28 px, white `(255,255,255)` text on a `(0,0,0,160)` rectangle
  padded 10 px; the overlay must stay readable on both bright and dark games.
- Place it above the game image object in z-order and keep it out of the
  scaler: it must never be drawn into the emulated frame, so screenshots and
  filters are unaffected.
- Right-align by measuring the text each time it changes (once per second).

## Cost and honesty

The overlay must not alter pacing: the only per-frame work is two clock reads
and a few additions. Do not claim a measured cost for it until it has been
timed on the Q60A. Do not use the overlay value as proof of smooth gameplay;
pair it with the app's runtime log and a hands-on check, as TizPSX's 37 FPS
edge-smoothing case showed.

## Reference implementations (2026-10-26)

| App | Where frames are timed | Notes |
| --- | --- | --- |
| TizGB 1.2.0, TizNES 1.1.0, TizGBA 0.2.0 | Animator tick (`ran` frames per tick; work is the tick's time divided by `ran`; frames after the first in a tick count as late) | Native rate: GB 59.73, NES 60.10 / 50.01 by ROM region, GBA 59.73 |
| TizNeo 0.3.0, TizPSX 0.3.0 | Emulation worker thread; the worker publishes a `perf_stats` snapshot under the frame mutex once per second and the UI thread formats it | NeoGeo late = frame-skipped; PSX late = frame finished after its deadline. Hidden immediately when leaving the game |

TizGB, TizNES, TizNeo and TizGBA persist `perf_overlay` in their existing
settings file; TizNES also persists game speed and audio output, which used to
reset on every start, in the new `tiznes-prefs.conf`. TizGBA scales the text
width by the canvas size (its layout wrappers work in design units).

Host harnesses compile each real frontend unchanged against
[tests/fake_efl.h](../tests/fake_efl.h): each emulator's `harness/`,
`nes-emulator/harness`, `gba-emulator/harness`, `neogeo-emulator/harness`,
`psx-emulator/harness`. They check the Exit row, the setting, its persistence
and the overlay text, including the real worker threads for TizNeo and TizPSX.
