# Shared pixel-art icon style

Use a recognizable system wordmark. Lettering is the focal point at Home-tile
size; add hardware art where it helps identify systems without a strong logo.
Do not substitute another emulator's icon or use an unreadable decorative line
as a supposed wordmark.

The existing TizGB/TizNeo procedural scripts establish the family palette:

| Role | RGB | Hex |
| --- | --- | --- |
| Background navy | 0, 29, 73 | `#001D49` |
| Optional navy highlight | 6, 42, 96 | `#062A60` |
| Gold sparkle / lettering | 252, 204, 103 | `#FCCC67` |
| Cream highlight | 255, 236, 176 | `#FFECB0` |
| Amber ray shadow | 232, 160, 56 | `#E8A038` |
| Cyan twinkle | 88, 176, 214 | `#58B0D6` |
| Dark outline | 20, 21, 26 | `#14151A` |

Draw on a **64×64** grid. Keep edges crisp, use a limited flat palette with
one-pixel highlights/shadows, and export **256×256 RGB PNG** using 4× nearest
neighbor. Keep the background opaque navy, with sparse gold/cream rays and
four-point twinkles behind the subject. Avoid antialiasing, gradients, system
fonts, blur and downloaded logos. Neo Geo uses an original pixel-art
interpretation of the stacked AES NEO/GEO badge, with the Advanced Entertainment
System inscription between the words. GB uses a gray/green handheld, NES a
gray/red pad, and GBA a purple handheld.

## Generator commands

From the kit directory, with Python 3 and Pillow installed:

```sh
python3 tools/make_icon.py --system neogeo --output output/neogeo.png
python3 tools/make_icon.py --system nes --output output/nes.png
python3 tools/make_icon.py --system gb --output output/gb.png
python3 tools/make_icon.py --system gba --output output/gba.png
```

The default Neo Geo icon draws its own stacked AES badge. The embedded 5×7
pixel font supports A–Z, 0–9, spaces, `-`, `+`, `.`, `/` for other labels.
Lowercase is uppercased. Separate two lines with a quoted `|`; the default Neo
Geo wordmark is `NEO|GEO`, in large 2-grid-pixel strokes. Each line is centered;
longer lines reduce to 1× grid text only if needed. More than two lines,
unsupported characters, and lines wider than 56 grid pixels fail explicitly.
For a prominent label prefer at most four letters per line at 2×, such as
`GAME|BOY`, rather than one small `GAME BOY` line. Lettering stays above the
hardware and has a dark outline to separate it from rays.

For another system, supply its own transparent **48×24 RGBA PNG** sprite. It is
pasted at grid `(8,38)` without resampling, so artwork stays on the same grid.
Use an alpha value of 0 outside the subject and 255 for solid pixels. Leave the
navy background, sparkle fan, lettering, and final export to the generator:

```sh
python3 tools/make_icon.py --system custom --wordmark 'SMS' \
  --art /absolute/path/to/master-system-48x24.png --output output/sms.png
```

`--art` can also override a built-in system's hardware while retaining its
default label. PNG dimensions and an alpha channel are checked on load. The
generator doesn't crop or silently stretch a mismatched input. To add a built-in
system, add its label to `LABELS` and its drawing branch to `hardware()`; no
emulator C changes are needed.

`--size` accepts integer multiples of 64 from 64 to 4096, with 256 as the
packaged-icon default. The generator never installs dependencies, signs a
package, contacts the TV, updates a cache, or copies to another emulator. An
existing output path is replaced intentionally, so use a new filename for a
variant you want to compare.

## Review and integration

Open the 256px result and inspect it at tile scale: the system name must read
immediately, with the hardware silhouette visible beneath it. Check size/mode
locally, for example:

```sh
python3 -c 'from PIL import Image; p=Image.open("output/neogeo.png"); print(p.format, p.size, p.mode)'
```

This is artifact inspection, not an automated test suite. The supplied Neo Geo
sample has been generated and inspected offline. TV tile readability, launcher
cache behavior and packaging integration remain consumer-level verification.
Once approved, copy the same PNG to the consumer's native and WGT icon paths,
rebuild the packages, and follow its existing install/cache procedure. This kit
does not change existing TizNES, TizGB, TizNeo or TizGBA artwork.
