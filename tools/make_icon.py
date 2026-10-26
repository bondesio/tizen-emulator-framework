#!/usr/bin/env python3
"""Offline 64-grid pixel art + prominent system wordmark, exported as RGB PNG.

Requires Pillow; no external fonts, image downloads, Tizen SDK or TV connection.
See ../docs/icons.md for the custom-art input contract and command examples.
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

GRID = 64
PALETTE = {
    "navy": (0, 29, 73),
    "navy_hi": (6, 42, 96),
    "gold": (252, 204, 103),
    "cream": (255, 236, 176),
    "amber": (232, 160, 56),
    "cyan": (88, 176, 214),
    "outline": (20, 21, 26),
}

# Original, embedded 5x7 uppercase pixel alphabet. No host-font dependence.
# Each row is a five-bit mask; this keeps the wordmark exactly on the art grid.
FONT = {
    "A": (14,17,17,31,17,17,17), "B": (30,17,17,30,17,17,30),
    "C": (14,17,16,16,16,17,14), "D": (30,17,17,17,17,17,30),
    "E": (31,16,16,30,16,16,31), "F": (31,16,16,30,16,16,16),
    "G": (14,17,16,23,17,17,15), "H": (17,17,17,31,17,17,17),
    "I": (31,4,4,4,4,4,31), "J": (7,2,2,2,18,18,12),
    "K": (17,18,20,24,20,18,17), "L": (16,16,16,16,16,16,31),
    "M": (17,27,21,21,17,17,17), "N": (17,25,25,21,19,19,17),
    "O": (14,17,17,17,17,17,14), "P": (30,17,17,30,16,16,16),
    "Q": (14,17,17,17,21,18,13), "R": (30,17,17,30,20,18,17),
    "S": (15,16,16,14,1,1,30), "T": (31,4,4,4,4,4,4),
    "U": (17,17,17,17,17,17,14), "V": (17,17,17,17,17,10,4),
    "W": (17,17,17,21,21,21,10), "X": (17,17,10,4,10,17,17),
    "Y": (17,17,10,4,4,4,4), "Z": (31,1,2,4,8,16,31),
    "0": (14,17,19,21,25,17,14), "1": (4,12,4,4,4,4,14),
    "2": (14,17,1,2,4,8,31), "3": (30,1,1,14,1,1,30),
    "4": (2,6,10,18,31,2,2), "5": (31,16,16,30,1,1,30),
    "6": (14,16,16,30,17,17,14), "7": (31,1,2,4,8,8,8),
    "8": (14,17,17,14,17,17,14), "9": (14,17,17,15,1,1,14),
    "-": (0,0,0,31,0,0,0), "+": (0,4,4,31,4,4,0),
    ".": (0,0,0,0,0,12,12), "/": (1,2,2,4,8,8,16),
    " ": (0,0,0,0,0,0,0),
}
LABELS = {"neogeo": "NEO|GEO", "nes": "NES", "gb": "GAME|BOY", "gba": "GBA"}


def wordmark(image, label):
    """Return the bottom pixel of the centered, outlined wordmark."""
    lines = [line.strip() for line in label.upper().split("|")]
    if not 1 <= len(lines) <= 2 or any(not line for line in lines):
        raise ValueError("wordmark needs one or two nonempty lines; use | between lines")
    unknown = sorted(set("".join(lines)) - FONT.keys())
    if unknown:
        raise ValueError("unsupported wordmark characters: " + repr("".join(unknown)))
    widths = [len(line) * 6 - 1 for line in lines]
    scale = min(2, 56 // max(widths))
    if scale < 1:
        raise ValueError("wordmark too wide; use two shorter lines separated by |")
    mask = Image.new("L", (GRID, GRID))
    draw = ImageDraw.Draw(mask)
    top = 4
    for line, width in zip(lines, widths):
        left = (GRID - width * scale) // 2
        for index, char in enumerate(line):
            for row, bits in enumerate(FONT[char]):
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        x = left + (index * 6 + col) * scale
                        y = top + row * scale
                        draw.rectangle((x, y, x + scale - 1, y + scale - 1), fill=255)
        top += 7 * scale + 2
    # A one-grid-pixel dark outline separates letters from the sparkle field.
    shifted = Image.new("L", mask.size)
    for dx, dy in ((-1,0), (1,0), (0,-1), (0,1), (1,1)):
        shifted.paste(mask, (dx, dy))
        image.paste(PALETTE["outline"], mask=shifted)
    colors = Image.new("RGB", image.size, PALETTE["gold"])
    ImageDraw.Draw(colors).rectangle((0, 0, 63, 8), fill=PALETTE["cream"])
    image.paste(colors, mask=mask)
    return top - 3


def background():
    image = Image.new("RGB", (GRID, GRID), PALETTE["navy"])
    draw = ImageDraw.Draw(image)
    # Light fans behind the lower hardware, leaving the wordmark unobstructed.
    for ray in range(13):
        angle = math.pi + ray * math.pi / 12
        length = 23 if ray % 2 == 0 else 19
        start = (32 + round(math.cos(angle) * 8), 48 + round(math.sin(angle) * 8))
        end = (32 + round(math.cos(angle) * length), 48 + round(math.sin(angle) * length))
        draw.line((start, end), fill=PALETTE["gold" if ray % 2 else "amber"])
    draw.ellipse((24, 38, 40, 52), fill=PALETTE["cream"])
    for x, y, color in ((6,8,"gold"), (57,13,"cream"), (5,37,"gold"),
                        (58,43,"gold"), (10,58,"cyan"), (53,59,"cyan")):
        draw.line((x-1,y,x+1,y), fill=PALETTE[color])
        draw.line((x,y-1,x,y+1), fill=PALETTE[color])
    for x, y in ((3,23), (60,29), (15,2), (49,3), (3,53), (61,56)):
        draw.point((x,y), fill=PALETTE["cyan"])
    return image


def hardware(system):
    """Original secondary hardware sprites; all use a transparent 48x24 grid."""
    image = Image.new("RGBA", (48, 24))
    d = ImageDraw.Draw(image)
    edge = PALETTE["outline"]
    if system == "neogeo":
        d.polygon(((5,10),(42,10),(46,13),(46,21),(42,23),(5,23),(1,20),(1,13)),
                  fill=(40,41,48), outline=edge)
        d.line((5,11,42,11), fill=(90,92,104))
        d.line((4,21,43,21), fill=(24,25,30))
        d.rectangle((12,5,14,17), fill=(150,150,150))
        d.ellipse((7,0,19,11), fill=(18,19,24), outline=(80,82,92))
        d.rectangle((10,2,12,3), fill=(130,132,142))
        for x, y in ((27,15),(32,12),(37,12),(42,15)):
            d.ellipse((x-2,y-2,x+2,y+2), fill=(196,32,40), outline=(128,16,24))
            d.point((x-1,y-1), fill=(255,128,128))
        d.line((20,20,35,20), fill=PALETTE["gold"])
    elif system == "gb":
        d.polygon(((16,0),(32,0),(34,2),(34,20),(31,23),(16,23),(14,21),(14,2)),
                  fill=(196,196,188), outline=edge)
        d.rectangle((17,3,31,12), fill=(84,86,104))
        d.rectangle((19,4,29,10), fill=(155,188,15))
        d.rectangle((20,7,23,9), fill=(48,98,48))
        d.rectangle((18,14,20,20), fill=edge)
        d.rectangle((16,16,22,18), fill=edge)
        d.ellipse((29,14,32,17), fill=(210,40,64))
        d.ellipse((25,17,28,20), fill=(210,40,64))
        d.line((23,21,27,21), fill=(110,112,122))
    elif system == "nes":
        d.rectangle((2,4,45,21), fill=(196,196,188), outline=edge)
        d.line((3,5,44,5), fill=(235,235,225))
        d.rectangle((5,7,42,18), fill=(45,46,52))
        d.rectangle((10,8,13,17), fill=(160,160,154))
        d.rectangle((7,11,16,14), fill=(160,160,154))
        d.rectangle((21,10,29,15), fill=(110,112,122))
        for x in (22,27):
            d.line((x,14,x+2,14), fill=edge)
        for x in (34,40):
            d.ellipse((x-2,11,x+2,15), fill=(210,40,64))
    elif system == "gba":
        d.polygon(((8,1),(39,1),(46,6),(47,17),(41,22),(6,22),(0,17),(1,6)),
                  fill=(89,76,152), outline=edge)
        d.line((8,2,39,2), fill=(155,140,210))
        d.rectangle((14,3,33,19), fill=(45,40,67))
        d.rectangle((17,5,30,16), fill=(88,176,214))
        d.rectangle((19,12,28,15), fill=(48,98,48))
        d.rectangle((6,7,8,15), fill=edge)
        d.rectangle((3,10,11,12), fill=edge)
        d.ellipse((38,6,42,10), fill=(180,174,190))
        d.ellipse((35,11,39,15), fill=(180,174,190))
    else:
        raise ValueError("custom system requires --art")
    return image


def neogeo_badge(image):
    """Draw the stacked Neo Geo AES wordmark and its separator inscription."""
    big = {
        "N": (31,17,25,21,19,17,31), "E": (31,16,16,30,16,16,31),
        "O": (31,17,17,17,17,17,31), "G": (31,17,16,23,17,17,31),
    }
    small = {
        "A": (2,5,7,5,5), "C": (3,4,4,4,3), "D": (6,5,5,5,6),
        "E": (7,4,6,4,7), "I": (7,2,2,2,7), "M": (5,7,7,5,5),
        "N": (5,7,7,7,5), "R": (6,5,6,5,5), "S": (3,4,2,1,6),
        "T": (7,2,2,2,2), "V": (5,5,5,5,2), "Y": (5,5,2,2,2),
        " ": (0,0,0,0,0),
    }

    def large(text, top):
        mask = Image.new("L", (GRID, GRID))
        draw = ImageDraw.Draw(mask)
        scale, gap = 2, 1
        width = len(text) * 10 + (len(text) - 1) * gap
        left = (GRID - width) // 2
        for i, char in enumerate(text):
            for y, bits in enumerate(big[char]):
                for x in range(5):
                    if bits & (1 << (4 - x)):
                        px = left + i * (10 + gap) + x * scale
                        py = top + y * scale
                        draw.rectangle((px, py, px + 1, py + 1), fill=255)
        outline = Image.new("L", mask.size)
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(1,1)):
            shifted = Image.new("L", mask.size)
            shifted.paste(mask, (dx,dy))
            outline = ImageChops.lighter(outline, shifted)
        image.paste(PALETTE["outline"], mask=outline)
        image.paste((196,32,40), mask=mask)
        image.paste(PALETTE["gold"], mask=mask)

    def caption(text, top):
        width = sum(3 if c != " " else 2 for c in text) + len(text) - 1
        x = (GRID - width) // 2
        draw = ImageDraw.Draw(image)
        for char in text:
            for y, bits in enumerate(small[char]):
                for col in range(3):
                    if bits & (1 << (2-col)):
                        draw.point((x+col, top+y), fill=PALETTE["cream"])
            x += (3 if char != " " else 2) + 1

    large("NEO", 3)
    draw = ImageDraw.Draw(image)
    draw.line((16,20,48,20), fill=PALETTE["amber"])
    caption("ADVANCED", 22)
    caption("ENTERTAINMENT", 28)
    caption("SYSTEM", 34)
    draw.rectangle((31,40,32,41), fill=PALETTE["gold"])
    draw.line((16,41,48,41), fill=PALETTE["amber"])
    large("GEO", 43)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", required=True, choices=(*LABELS, "custom"))
    parser.add_argument("--wordmark", help="uppercase pixel text; | separates up to two lines")
    parser.add_argument("--art", type=Path, help="custom 48x24 transparent PNG hardware sprite")
    parser.add_argument("--size", type=int, default=256, help="square size, a multiple of 64 (default 256)")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if not 64 <= args.size <= 4096 or args.size % GRID:
            raise ValueError("size must be a multiple of 64 between 64 and 4096")
        label = args.wordmark if args.wordmark is not None else LABELS.get(args.system)
        if label is None:
            raise ValueError("custom system requires --wordmark")
        if args.art:
            with Image.open(args.art) as source:
                if source.format != "PNG" or source.size != (48,24) or "A" not in source.getbands():
                    raise ValueError("custom art must be a 48x24 PNG with an alpha channel")
                art = source.convert("RGBA")
        else:
            art = hardware(args.system)
        image = background()
        aes_badge = args.system == "neogeo" and not args.art and args.wordmark is None
        if aes_badge:
            neogeo_badge(image)
        else:
            wordmark(image, label)
        # Hardware lives in the lower 24 rows; even a two-line 2x title clears it.
        if not aes_badge:
            image.paste(art, (8,38), mask=art.getchannel("A"))
        output = image.resize((args.size,args.size), Image.Resampling.NEAREST)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output.save(args.output, format="PNG", optimize=True)
        print(f"wrote {args.output}: {args.size}x{args.size} RGB PNG; wordmark={label!r}")
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
