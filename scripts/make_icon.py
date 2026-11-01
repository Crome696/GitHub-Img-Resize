"""Render the app icon (PNG and multi-size ICO) from code.

Run from the repository root:

    python scripts/make_icon.py

The output lands in src/gh_img_resize/assets and is committed, so the build does
not need to run this script.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "src" / "gh_img_resize" / "assets"
CANVAS = 1024  # drawn large, then downscaled for smooth edges
ICON_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

BACKGROUND = (13, 17, 23, 255)  # DARK.background
SURFACE = (22, 27, 34, 255)  # DARK.surface
BORDER = (48, 54, 61, 255)  # DARK.border
ACCENT = (68, 147, 248, 255)  # DARK.accent
SUN = (121, 192, 255, 255)
MOUNTAIN_FAR = (47, 70, 104, 255)


def _draw_icon(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    s = size / 1024  # scale factor relative to the 1024 design grid

    def box(x0: float, y0: float, x1: float, y1: float) -> tuple[float, ...]:
        return (x0 * s, y0 * s, x1 * s, y1 * s)

    # Rounded app tile with a subtle inner border.
    draw.rounded_rectangle(box(40, 40, 984, 984), radius=200 * s, fill=BACKGROUND)
    draw.rounded_rectangle(
        box(40, 40, 984, 984),
        radius=200 * s,
        outline=BORDER,
        width=max(1, round(12 * s)),
    )

    # Picture frame: the image being resized.
    frame_width = max(1, round(48 * s))
    draw.rounded_rectangle(
        box(200, 260, 824, 764),
        radius=56 * s,
        fill=SURFACE,
        outline=ACCENT,
        width=frame_width,
    )

    # Landscape inside the frame.
    draw.polygon(
        [
            (230 * s, 730 * s),
            (430 * s, 470 * s),
            (560 * s, 620 * s),
            (640 * s, 530 * s),
            (794 * s, 730 * s),
        ],
        fill=MOUNTAIN_FAR,
    )
    draw.polygon(
        [(300 * s, 730 * s), (460 * s, 540 * s), (600 * s, 730 * s)],
        fill=ACCENT,
    )
    draw.ellipse(box(600, 330, 690, 420), fill=SUN)

    # Size bar under the frame: a track filled to just under the limit (999 of 1000 KB).
    bar_radius = 28 * s
    draw.rounded_rectangle(box(260, 806, 764, 862), radius=bar_radius, fill=SURFACE)
    draw.rounded_rectangle(box(260, 806, 740, 862), radius=bar_radius, fill=ACCENT)
    return image


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    master = _draw_icon(CANVAS).resize((1024, 1024), Image.Resampling.LANCZOS)
    master.resize((512, 512), Image.Resampling.LANCZOS).save(OUTPUT_DIR / "icon.png")
    master.save(
        OUTPUT_DIR / "icon.ico",
        format="ICO",
        sizes=ICON_SIZES,
    )
    print(f"Wrote {OUTPUT_DIR / 'icon.png'} and {OUTPUT_DIR / 'icon.ico'}")


if __name__ == "__main__":
    main()
