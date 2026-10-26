# Emulator framework kit — current state

## Current state

- Local starter repository on `main`, initial commit `a94ace0`, no remote. Owns only this directory; it
  has no runtime library or installed TV service. TizNeo is the first consumer
  and integrates its contracts manually into its own native C app.
- `README.md` routes authors to the controller/settings/icon contracts and
  existing native C sources. `snippets/settings_rows.h` provides a copyable row
  enum with separate non-selectable section metadata.
- **Library Exit row and performance overlay: specified and adopted by all five emulators (2026-10-26, uncommitted here):**
  `docs/settings.md` specifies the library layout (row 0 Exit, games, last row
  Settings; `snippets/library_rows.h`) and the starting selection (first game,
  else Settings, never Exit). `docs/overlay.md` and `snippets/perf_overlay.h`
  define the Off / FPS / Detailed overlay setting (persisted as `perf_overlay`).
  TizGB 1.2.0, TizNES 1.1.0, TizGBA 0.2.0, TizNeo 0.3.0 and TizPSX 0.3.0 were
  rebuilt and installed on the Q60A with it. `tests/test_perf_overlay.c` passes
  with ASan/UBSan; `tests/fake_efl.h` drives per-app host harnesses (GB 98,
  NES 75, GBA 21, NeoGeo 21, PSX 20 checks). Overlay cost on the TV has not
  been timed, and none of the five apps has been launched since the install.
- `tools/make_icon.py` is an offline Python/Pillow generator with an embedded
  pixel font, a stacked Neo Geo AES badge preset, NES/GB/GBA sprites, custom
  RGBA sprite input, and integer nearest-neighbor output. Dependency setup is
  documented in README.
- `output/neogeo.png` was regenerated and visually inspected: PNG, 256×256,
  RGB, 1,738 bytes. SHA-256:
  `fe759dd3fb790b89cad42c47e08b7a1377930d7dfd2bad3185d651b2aa4733be`.
  Python compilation passed; NES, GB and GBA preset generation completed to
  temporary images.

## First consumer: TizNeo

- The TizNeo 0.2.7 native TPK and launcher 1.0.3 WGT now use the AES wordmark
  design; all four installed app/cache icon copies match. The app follows the
  framework's settings and controller contracts. Metal Slug 3 rendered its
  animated title screen for at least 50 seconds and KOF 2002 rendered its intro
  for over 30 seconds without a crash. NES/GB watchers are active after the
  check; the NES watcher owns the shared gamepad node at idle. Full gameplay
  controls, audio and save persistence remain unverified.
- TizNES/TizGB/TizNeo watcher sources share `/run/tizen-input-access.lock` and
  publish recovery markers before device-permission changes. TizNeo's live
  capture check confirmed its exact event-node grab persists when the TV rejects
  state-query ioctls. The watcher services were restored NES-first; NES owns the
  gamepad at idle. Future GBA integration and other consumer code paths remain
  open.
