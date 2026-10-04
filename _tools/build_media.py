"""Build every image the site uses from the app's design sources.

    python3 _tools/build_media.py

Sources live outside this repo (~/Developer/DarcDesign). Every output is re-encoded from pixels
only, so no EXIF, XMP or ICC text from a source file reaches the site.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(SITE, "img")
DESIGN = os.path.expanduser("~/Developer/DarcDesign")
ICON = os.path.join(DESIGN, "assets/icon_1024.png")
WEBP_QUALITY = 80
BACKGROUND = (13, 13, 23)
ACCENT = (127, 76, 248)
FONT = "/System/Library/Fonts/SFNS.ttf"

# name -> (source, widths, crop box in source pixels or None)
SOURCES = {
    "art-browsers": ("assets/raw/browser_stack.png", (560, 900), None),
    "art-moon": ("assets/raw/paywall_moon_ribbon.png", (360, 560), (0, 100, 851, 1800)),
    "shot-mode": ("work/app/shots/pm_dash_disabled_en.png", (360, 600), None),
    "shot-site": ("work/app/shots/pm_detail_en.png", (360, 600), None),
    "shot-sites": ("work/app/shots/pm_sites_en.png", (360, 600), None),
    "shot-enable": ("work/s3/final_enable_promax_en.png", (360, 600), None),
    "shot-ipad": ("work/app/shots/ipad_dash_en.png", (560, 900), (0, 0, 2048, 1900)),
}


def clean(image):
    """A fresh image holding only pixel data."""
    mode = "RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB"
    pixels = image.convert(mode)
    fresh = Image.new(mode, pixels.size)
    fresh.paste(pixels)
    return fresh


def save_webp(image, name):
    image.save(os.path.join(IMG, name), "WEBP", quality=WEBP_QUALITY, method=6)


def build_sources():
    for name, (source, widths, box) in SOURCES.items():
        image = clean(Image.open(os.path.join(DESIGN, source)))
        if box:
            image = image.crop(box)
        for width in widths:
            height = round(image.height * width / image.width)
            save_webp(image.resize((width, height), Image.LANCZOS), f"{name}-{width}.webp")


def build_icons():
    icon = clean(Image.open(ICON)).convert("RGB")
    for size in (128, 256, 512):
        save_webp(icon.resize((size, size), Image.LANCZOS), f"app-icon-{size}.webp")
    for size in (16, 32):
        icon.resize((size, size), Image.LANCZOS).save(os.path.join(SITE, f"favicon-{size}.png"), optimize=True)
    icon.resize((180, 180), Image.LANCZOS).save(os.path.join(SITE, "apple-touch-icon.png"), optimize=True)
    icon.resize((48, 48), Image.LANCZOS).save(os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])


def build_og():
    width, height = 1200, 630
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    glow = Image.new("RGB", (width, height), BACKGROUND)
    ImageDraw.Draw(glow).ellipse((-120, -40, 620, 700), fill=(70, 36, 150))
    canvas = Image.blend(canvas, glow.filter(ImageFilter.GaussianBlur(140)), 0.9)
    icon = clean(Image.open(ICON)).convert("RGB").resize((380, 380), Image.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 379, 379), radius=86, fill=255)
    canvas.paste(icon, (90, 125), mask)
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.truetype(FONT, 76)
    title.set_variation_by_name("Bold")
    body = ImageFont.truetype(FONT, 34)
    body.set_variation_by_name("Regular")
    draw.text((540, 170), "Your web,", font=title, fill=(255, 255, 255))
    draw.text((540, 258), "your way.", font=title, fill=(170, 130, 255))
    draw.text((540, 372), "Dark sites when you want them dark,", font=body, fill=(200, 200, 215))
    draw.text((540, 418), "light sites when you want them light.", font=body, fill=(200, 200, 215))
    draw.text((540, 492), "Darc for Safari", font=body, fill=(255, 214, 140))
    canvas.save(os.path.join(SITE, "og-image.png"), optimize=True)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    build_sources()
    build_icons()
    build_og()
