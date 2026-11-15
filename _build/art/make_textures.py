"""Make the addon's textures (Media/*.tga) from a logo of _build/art.

    python -P _build/art/make_textures.py               # the logo in use, LOGO
    python -P _build/art/make_textures.py logo-helmet.webp

The game gets three textures:

    Media/Logo.tga      64 x 64   the addon list
    Media/Portrait.tga  128 x 128 the window's portrait, which the window frames with its own ring
    Media/Icon.tga      32 x 32   the minimap button, framed by the minimap's ring

Each logo below says how to cut each one: the whole square, or a disc (centre x, centre y,
radius, in the logo's pixels) made transparent outside the circle; beyond the circle the
disc takes the logo's background colour, so no gold of the logo's ring bleeds into its edge.
The discs were measured on each logo: a new logo needs them measured again. A third number
brightens that texture (and raises its contrast by half as much).

The game reads uncompressed 32-bit TGA files whose sides are powers of two. Needs Pillow.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent.parent / "Media"
SUPERSAMPLE = 4
SQUARE = None

LOGO = "logo-blue.webp"

LOGOS = {
    # A helmet on a dark disc inside a gold ring: the ring for the addon list, the disc elsewhere.
    "logo-helmet.webp": {
        "background": (14, 14, 16),
        "Logo.tga": (64, (619.5, 617.0, 602)),
        "Portrait.tga": (128, (619.5, 617.0, 536)),
        "Icon.tga": (32, (619.5, 617.0, 512)),
    },
    # A horned helmet whose horns break out of a gold ring: the whole square for the addon list,
    # the disc inside the ring for the window, the face alone for the minimap.
    "logo-horns.jpg": {
        "background": (16, 15, 20),
        "Logo.tga": (64, SQUARE),
        "Portrait.tga": (128, (990, 971, 850)),
        "Icon.tga": (32, (995, 775, 650), 1.4),  # brighter: the dark steel is lost at 20 pixels
    },
    # A pale horned helmet with blue eyes on a blue starry disc in a gold ring, horns over the ring:
    # the whole square for the addon list, the disc inside the ring for the window (the ring is
    # thicker at the bottom right, hence its small radius), the helmet alone for the minimap.
    "logo-blue.webp": {
        "background": (14, 15, 19),
        "Logo.tga": (64, SQUARE),
        "Portrait.tga": (128, (629, 615, 530)),
        "Icon.tga": (32, (627, 600, 440)),
    },
}


def texture(logo: Image.Image, size: int, cut, background, light: float = 1.0) -> Image.Image:
    if light != 1.0:
        logo = ImageEnhance.Contrast(ImageEnhance.Brightness(logo).enhance(light)).enhance(1 + (light - 1) / 2)
    if cut is SQUARE:
        whole = logo.resize((size, size), Image.Resampling.LANCZOS)
        whole.putalpha(255)
        return whole
    x, y, radius = cut
    square = logo.crop((round(x - radius), round(y - radius), round(x + radius), round(y + radius)))
    side = square.width
    inside = Image.new("L", square.size, 0)
    ImageDraw.Draw(inside).ellipse((0, 0, side - 1, side - 1), fill=255)
    square = Image.composite(square, Image.new("RGB", square.size, background), inside)
    big = size * SUPERSAMPLE
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    disc = square.resize((size, size), Image.Resampling.LANCZOS)
    disc.putalpha(mask.resize((size, size), Image.Resampling.LANCZOS))
    return disc


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else LOGO
    cuts = LOGOS[name]
    logo = Image.open(HERE / name).convert("RGB")
    MEDIA.mkdir(exist_ok=True)
    for target, value in cuts.items():
        if target == "background":
            continue
        texture(logo, *value[:2], cuts["background"], *value[2:]).save(MEDIA / target, format="TGA", rle=False)
        size = value[0]
        print(f"{target}: {size} x {size} from {name}")


if __name__ == "__main__":
    main()
