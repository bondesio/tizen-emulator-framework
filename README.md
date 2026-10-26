# Tizen emulator starter kit

> **Context.** These kits are for *native* Tizen 6 apps (C against EFL/Evas, built as signed TPKs),
> not Tizen web apps. They run on one rooted Samsung QE75Q60AAUXXC; see the investigation this builds on:
>
> - [Samsung QE75Q60AAUXXC root research](https://github.com/bondesio/qe75q60aa-root-research): how that TV was rooted and how apps are installed.
> - [Native Tizen 6 apps and UEP](https://github.com/bondesio/tizen6-native-app-uep-research): why a native UI could render at all.

A small set of source conventions and offline artwork tools for the native C/Evas
emulators on Pablo's Tizen 6.0, 32-bit ARM Q60A. This is a kit to copy from, not a
new runtime library, emulator core, build system, or installed TV service.

Start with these documents:

1. [Controller contract](docs/controllers.md): the complete TizNES option set,
   identity matching, capture status, per-model mappings, and watcher boundaries.
2. [Settings and navigation](docs/settings.md): Controllers → Audio → Video →
   System, non-selectable headings, remote/gamepad controls, and Evas layout.
   [settings_rows.h](snippets/settings_rows.h) is a copyable C enum/section table.
3. [Performance overlay](docs/overlay.md): the Off / FPS / Detailed setting and
   [perf_overlay.h](snippets/perf_overlay.h), a header-only, host-tested counter.
   The library layout (Exit first, games, Settings last) is in the settings document
   with [library_rows.h](snippets/library_rows.h).
4. [Icon style and generator](docs/icons.md): shared palette, 64-pixel grid,
   prominent system lettering, and distinct hardware art.

## Check the snippets and the frontends

`tests/fake_efl.h` is a host-side fake of the EFL / Ecore / audio-out calls the
frontends hand-declare; each app's `harness/` directory builds its real UI
source against it (`make -C <app>/harness ui-tests`).

```sh
cc -std=c99 -Wall -Wextra -Wpedantic -I snippets tests/test_perf_overlay.c -o /tmp/t && /tmp/t
```

## Generate an icon

Python 3 and Pillow are required. If Pillow is not already available, install it
in a local virtual environment (this does not require Tizen Studio):

```sh
cd tizen-emulator-framework
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/make_icon.py --system neogeo --output output/neogeo.png
```

An existing Python with Pillow can run `python3 tools/make_icon.py` directly.
The committed [Neo Geo example](output/neogeo.png) is a 256×256 RGB PNG. Its
stacked NEO / GEO wordmark and small Advanced Entertainment System inscription
follow the structure of the AES badge over the shared navy/gold sparkle motif.
Nothing writes to another repo.

## Use this in a new emulator

- Copy the **structure** of [TizGB](https://github.com/bondesio/tizgb): `app/`, `launcher/`, `tools/`,
  and an independently named `input-watcher/`. Keep core-specific code in that
  emulator. Read its Makefile and libc shims before reusing its build recipe.
- Port the proven controller functions from [`app/nes_main.c` in TizNES](https://github.com/bondesio/tiznes/blob/main/app/nes_main.c)
  together with their state and mapping persistence; follow the controller
  document's source map. A copied menu alone does not implement input capture.
- Adapt the settings snippet to the core's actual options. Add system-specific
  options inside the existing groups rather than adding unrelated top-level
  pages. Persist choices from the first usable version.
- Generate the icon here, review it, then deliberately copy the chosen PNG to
  both the emulator's `app/shared/res/icon.png` and `launcher/icon.png`. Packaging,
  app IDs, versioning, signing and cache refresh remain that emulator's concern.
- Preserve the working launcher behavior: native app ID must match its manifest;
  exit the WGT when hidden behind the native window, not after a fixed timeout.

Reference consumers: TizNES supplies two-player input, TizGB supplies the simpler
frontend/library structure, and [TizGBA](https://github.com/bondesio/tizgba)
follows this group order, two controller slots and capture default On.
The emulators stay independent; none of them depends on this kit at build time.

All kit execution is offline. For native builds and any TV work, first read the
[root research](https://github.com/bondesio/qe75q60aa-root-research) and the [UEP research](https://github.com/bondesio/tizen6-native-app-uep-research). Kernel, modules, firmware
and the boot chain are outside the emulator implementation boundary.

## License

Released under the Unlicense (see `LICENSE`).
