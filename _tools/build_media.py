"""Build every image the site uses from real captures of the Darc build.

    python3 _tools/build_media.py

Sources live outside this repo (~/Developer/DarcDesign). The Safari captures were taken in the
iOS 26.3 simulator with the Darc extension running on a hand-made sample page ("The Daily Web"
and "Night Shift"); the app captures come from the same Debug build. Every output is re-encoded
from pixels only, so no EXIF, XMP or ICC text from a source file reaches the site.

Each picture ships as AVIF and WebP at several widths; the page picks one with srcset/sizes.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(SITE, "img")
DESIGN = os.path.expanduser("~/Developer/DarcDesign")
CAPS = os.path.join(DESIGN, "work/web-build/caps")
# Apple's device art from fastlane/frameit-frames (gh-pages/latest), with the screen rectangles
# from its offsets.json. The screen masks are the frame's enclosed transparent screen area.
FRAMES = os.path.join(DESIGN, "work/web-build/frames")
IPHONE = {"frame": "iphone17pm.png", "mask": "iphone17pm_mask.png", "origin": (75, 66), "screen": (1320, 2868)}
IPAD = {"frame": "ipadpro11.png", "mask": "ipadpro11_mask.png", "origin": (95, 100), "screen": (1668, 2420)}
ICON = os.path.join(DESIGN, "assets/icon_1024.png")
MOON = os.path.join(DESIGN, "assets/raw/paywall_moon_ribbon.png")
WEBP_QUALITY = 78
AVIF_QUALITY = 58
BACKGROUND = (11, 10, 16)
FONT = "/System/Library/Fonts/SFNS.ttf"

PHONE_WIDTHS = (360, 600, 900, 1320)
FRAMED_WIDTHS = (360, 600, 900)

# Unframed screens: the before/after pairs sit under the live frame overlay on the page.
# name -> (source file in CAPS, crop box or None, widths)
SOURCES = {
    "web-article-original": ("article_orig.png", None, PHONE_WIDTHS),
    "web-article-darc": ("article_dark.png", None, PHONE_WIDTHS),
    "web-forum-original": ("forum_orig.png", None, PHONE_WIDTHS),
    "web-forum-darc": ("forum_light.png", None, PHONE_WIDTHS),
    "web-article-photo": ("article_dark.png", (0, 380, 1320, 1800), (360, 600, 900, 1320)),
    "popup-menu": ("popup.png", None, (340, 680, 1020)),
}

# Captures composited into the real device frame. name -> (source, device, widths)
FRAMED = {
    "framed-article-comments": ("c_talk.png", IPHONE, FRAMED_WIDTHS),
    "framed-enable": ("app_enable.png", IPHONE, (360, 600)),
    "framed-dashboard": ("app_dash.png", IPHONE, (300, 600)),
    "framed-ipad": ("app_ipad.png", IPAD, (560, 900, 1300)),
}


def clean(image):
    """A fresh image holding only pixel data."""
    mode = "RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB"
    pixels = image.convert(mode)
    fresh = Image.new(mode, pixels.size)
    fresh.paste(pixels)
    return fresh


def save_pair(image, stem):
    """WebP and AVIF of the same pixels."""
    image.save(os.path.join(IMG, f"{stem}.webp"), "WEBP", quality=WEBP_QUALITY, method=6)
    image.save(os.path.join(IMG, f"{stem}.avif"), "AVIF", quality=AVIF_QUALITY, speed=4)


def build_sources():
    for name, (source, box, widths) in SOURCES.items():
        image = clean(Image.open(os.path.join(CAPS, source))).convert("RGB")
        if box:
            image = image.crop(box)
        for width in widths:
            height = round(image.height * width / image.width)
            save_pair(image.resize((width, height), Image.LANCZOS), f"{name}-{width}")
        print(name, image.size)


def build_framed():
    for name, (source, device, widths) in FRAMED.items():
        frame = Image.open(os.path.join(FRAMES, device["frame"])).convert("RGBA")
        mask = Image.open(os.path.join(FRAMES, device["mask"])).convert("L")
        shot = clean(Image.open(os.path.join(CAPS, source))).convert("RGBA")
        if shot.size != device["screen"]:
            raise SystemExit(f"{source}: {shot.size} does not match the {device['frame']} screen")
        canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        screen = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        screen.paste(shot, device["origin"])
        canvas.paste(screen, (0, 0), mask)
        canvas.alpha_composite(frame)
        for width in widths:
            height = round(canvas.height * width / canvas.width)
            save_pair(canvas.resize((width, height), Image.LANCZOS), f"{name}-{width}")
        print(name, canvas.size)


def build_overlay():
    """The bare iPhone frame laid over the live before/after split, plus its screen mask."""
    frame = Image.open(os.path.join(FRAMES, IPHONE["frame"])).convert("RGBA")
    for width in (490, 980, 1470):
        height = round(frame.height * width / frame.width)
        save_pair(frame.resize((width, height), Image.LANCZOS), f"frame-iphone-{width}")
    x, y = IPHONE["origin"]
    w, h = IPHONE["screen"]
    mask = Image.open(os.path.join(FRAMES, IPHONE["mask"])).convert("L").crop((x, y, x + w, y + h))
    alpha = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    alpha.putalpha(mask)
    alpha.resize((660, 1434), Image.LANCZOS).save(os.path.join(IMG, "screen-mask.png"), optimize=True)


def build_moon():
    """The paywall's moon ribbon, used small and faded behind the Darc Forever heading."""
    moon = clean(Image.open(MOON)).convert("RGBA").crop((0, 100, 851, 1800))
    for width in (240, 480):
        height = round(moon.height * width / moon.width)
        save_pair(moon.resize((width, height), Image.LANCZOS), f"art-moon-{width}")


def build_icons():
    icon = clean(Image.open(ICON)).convert("RGB")
    for size in (64, 128, 256):
        save_pair(icon.resize((size, size), Image.LANCZOS), f"app-icon-{size}")
    for size in (16, 32):
        icon.resize((size, size), Image.LANCZOS).save(os.path.join(SITE, f"favicon-{size}.png"), optimize=True)
    icon.resize((180, 180), Image.LANCZOS).save(os.path.join(SITE, "apple-touch-icon.png"), optimize=True)
    icon.resize((48, 48), Image.LANCZOS).save(os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])


def build_og():
    width, height = 1200, 630
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    glow = Image.new("RGB", (width, height), BACKGROUND)
    ImageDraw.Draw(glow).ellipse((-60, 40, 560, 620), fill=(52, 30, 120))
    canvas = Image.blend(canvas, glow.filter(ImageFilter.GaussianBlur(150)), 0.85)
    icon = clean(Image.open(ICON)).convert("RGB").resize((300, 300), Image.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 299, 299), radius=68, fill=255)
    canvas.paste(icon, (100, 165), mask)
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.truetype(FONT, 70)
    title.set_variation_by_name("Bold")
    body = ImageFont.truetype(FONT, 32)
    body.set_variation_by_name("Regular")
    draw.text((470, 190), "Dark when it's late.", font=title, fill=(242, 240, 247))
    draw.text((470, 272), "Light when it's not.", font=title, fill=(185, 166, 255))
    draw.text((470, 384), "Darc, a Safari extension for", font=body, fill=(162, 157, 179))
    draw.text((470, 426), "iPhone, iPad and Mac.", font=body, fill=(162, 157, 179))
    canvas.save(os.path.join(SITE, "og-image.png"), optimize=True)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    build_sources()
    build_framed()
    build_overlay()
    build_moon()
    build_icons()
    build_og()
