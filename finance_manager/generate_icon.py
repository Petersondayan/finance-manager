"""Generate app icon as .ico from the approved design concept."""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    if r <= 0:
        draw.rectangle([x0, y0, x1, y1], fill=fill)
        return
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.ellipse([x0, y0, x0 + r * 2, y0 + r * 2], fill=fill)
    draw.ellipse([x1 - r * 2, y0, x1, y0 + r * 2], fill=fill)
    draw.ellipse([x0, y1 - r * 2, x0 + r * 2, y1], fill=fill)
    draw.ellipse([x1 - r * 2, y1 - r * 2, x1, y1], fill=fill)


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 256  # scale factor

    # Background rounded square
    r = int(44 * s)
    bg_dark = (13, 33, 55)
    bg_light = (26, 60, 94)
    # Draw gradient-ish background (two rectangles, light then dark overlay)
    draw_rounded_rect(draw, [0, 0, size - 1, size - 1], r, bg_light)
    # Gradient simulation: overlay dark at bottom-right
    for i in range(int(size * 0.6)):
        alpha = int(80 * (i / (size * 0.6)))
        draw.line(
            [(size - i, 0), (size, i)],
            fill=(13, 33, 55, alpha),
            width=1,
        )

    # Subtle grid lines
    grid_color = (255, 255, 255, 13)
    for y_frac in [80 / 256, 120 / 256, 160 / 256]:
        y = int(y_frac * size)
        draw.line([(int(36 * s), y), (int(220 * s), y)], fill=grid_color, width=1)

    # Bar chart bars  (teal palette)
    bar_colors = [
        (77, 208, 225),   # bar 1 top
        (38, 198, 218),   # bar 2 top
        (0, 229, 255),    # bar 3 top
    ]
    bars = [
        # (x, y, w, h) in 256-space
        (44, 155, 44, 55),
        (106, 110, 44, 100),
        (168, 68, 44, 142),
    ]
    bar_radius = max(2, int(6 * s))
    for (bx, by, bw, bh), color in zip(bars, bar_colors):
        bx2 = int((bx + bw) * s)
        by2 = int((by + bh) * s)
        bx = int(bx * s)
        by = int(by * s)
        draw_rounded_rect(draw, [bx, by, bx2, by2], bar_radius, color + (220,))

    # Gold trend line
    gold = (255, 213, 79)
    points_256 = [(66, 148), (128, 103), (190, 61)]
    points = [(int(x * s), int(y * s)) for x, y in points_256]
    lw = max(2, int(5 * s))
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=gold, width=lw)
    dot_r = max(2, int(5 * s))
    for px, py in points:
        draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r], fill=gold)

    # Dollar sign badge (gold circle, bottom-left)
    cx, cy, cr = int(58 * s), int(198 * s), int(26 * s)
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=gold)

    # Dollar sign text
    font_size = max(10, int(28 * s))
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    text = "$"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (cx - tw // 2 - bbox[0], cy - th // 2 - bbox[1]),
        text,
        font=font,
        fill=(13, 33, 55),
    )

    return img


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "src", "finance_manager", "assets")
    os.makedirs(out_dir, exist_ok=True)

    sizes = [256, 128, 64, 48, 32, 16]
    images = [draw_icon(s) for s in sizes]

    ico_path = os.path.join(out_dir, "app_icon.ico")
    images[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )
    print(f"Icon saved: {ico_path}")

    # Also save a 256 PNG for reference
    png_path = os.path.join(out_dir, "app_icon.png")
    images[0].save(png_path, format="PNG")
    print(f"PNG saved:  {png_path}")


if __name__ == "__main__":
    main()
