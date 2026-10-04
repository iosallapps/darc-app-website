"""Rewrite the shared head, header and footer of every page.

    python3 _tools/build_pages.py

Each page keeps its own content. The blocks between <!-- build:NAME --> and <!-- /build:NAME -->
are regenerated here, so a nav or footer change is made once. The script also refuses to run
if any page contains an em or en dash.
"""
import os
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://darcapp.com/"
APP_STORE = "https://apps.apple.com/app/id6819036330"
APP_ID = "6819036330"
STYLE_VERSION = "1"
FORBIDDEN = ["\u2014", "\u2013"]

# file -> (title, description, canonical path)
PAGES = {
    "index.html": (
        "Darc: Dark and Light Mode for Safari",
        "Darc themes every website in Safari both ways: a real dark theme for bright sites and a "
        "light theme for dark-only sites. Per-site rules, dark hours, true black. iPhone, iPad and Mac.",
        "",
    ),
    "support.html": (
        "Support | Darc",
        "Turn on the Darc extension in Safari on iPhone, iPad and Mac, fix a site that looks wrong, "
        "restore your purchase and contact us.",
        "support.html",
    ),
    "privacy.html": (
        "Privacy Policy | Darc",
        "Darc has no account, no analytics, no ads and no servers. Pages are restyled on your device "
        "and your browsing is never sent to us.",
        "privacy.html",
    ),
    "terms.html": (
        "Terms of Use | Darc",
        "The terms for using Darc and the Darc Forever one-time purchase.",
        "terms.html",
    ),
    "404.html": (
        "Page not found | Darc",
        "This page does not exist. Go back to Darc, the dark and light mode extension for Safari.",
        None,
    ),
}

HEAD = """<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="apple-itunes-app" content="app-id={app_id}">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="theme-color" content="#0D0D17">
    <meta name="color-scheme" content="dark">{canonical}
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Darc">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{domain}og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="The Darc app icon, a glowing purple crescent around a warm golden light, next to the words Your web, your way.">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{domain}og-image.png">
    <link rel="icon" href="/favicon.ico" sizes="48x48">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="stylesheet" href="/styles.css?v={style_version}">"""

HEADER = """<header class="site-header">
        <div class="container bar">
            <a class="brand" href="/" aria-label="Darc home">
                <img src="/img/app-icon-128.webp" width="34" height="34" alt="">
                <span>Darc</span>
            </a>
            <nav aria-label="Main">
                <ul class="nav-links">
                    <li class="nav-hide"><a href="/#features">Features</a></li>
                    <li class="nav-hide"><a href="/#privacy">Privacy</a></li>
                    <li class="nav-hide"><a href="/#faq">FAQ</a></li>
                    <li class="nav-hide"><a href="/support.html">Support</a></li>
                    <li><a class="nav-cta" href="{app_store}">Get Darc</a></li>
                </ul>
            </nav>
        </div>
    </header>"""

FOOTER = """<footer class="site-footer">
        <div class="container">
            <div class="footer-grid">
                <a class="brand" href="/" aria-label="Darc home">
                    <img src="/img/app-icon-128.webp" width="28" height="28" alt="">
                    <span>Darc</span>
                </a>
                <nav aria-label="Footer">
                    <ul class="footer-links">
                        <li><a href="/support.html">Support</a></li>
                        <li><a href="/privacy.html">Privacy Policy</a></li>
                        <li><a href="/terms.html">Terms of Use</a></li>
                        <li><a href="/support.html#acknowledgements">Acknowledgements</a></li>
                        <li><a href="mailto:iosallapps@icloud.com">iosallapps@icloud.com</a></li>
                    </ul>
                </nav>
            </div>
            <div class="footer-small">
                <p>Darc's theming engine includes <a href="https://github.com/darkreader/darkreader">Dark Reader</a>, Copyright (c) 2026 Dark Reader Ltd., used under the <a href="/support.html#acknowledgements">MIT License</a>.</p>
                <p>Darc is made by Darius Cirjan. Safari, iPhone, iPad, Mac and iCloud are trademarks of Apple Inc. App Store is a service mark of Apple Inc.</p>
                <p>&copy; 2026 Darius Cirjan</p>
            </div>
        </div>
    </footer>"""


def render_head(page):
    title, description, path = PAGES[page]
    url = DOMAIN + (path or "")
    canonical = "" if path is None else f'\n    <link rel="canonical" href="{url}">'
    if path is None:
        canonical = '\n    <meta name="robots" content="noindex">'
    return HEAD.format(app_id=APP_ID, title=title, description=description, canonical=canonical,
                       url=url, domain=DOMAIN, style_version=STYLE_VERSION)


def replace_block(source, name, body):
    pattern = re.compile(rf"(<!-- build:{name} -->)(.*?)(\s*<!-- /build:{name} -->)", re.S)
    if not pattern.search(source):
        raise SystemExit(f"missing build:{name} block")
    indent = "    "
    return pattern.sub(lambda m: f"{m.group(1)}\n{indent}{body}{m.group(3)}", source, count=1)


def main():
    for page in PAGES:
        path = os.path.join(SITE, page)
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        source = replace_block(source, "head", render_head(page))
        source = replace_block(source, "header", HEADER.format(app_store=APP_STORE))
        source = replace_block(source, "footer", FOOTER)
        for dash in FORBIDDEN:
            if dash in source:
                sys.exit(f"{page}: contains a forbidden dash U+{ord(dash):04X}")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(source)
        print("built", page)


if __name__ == "__main__":
    main()
