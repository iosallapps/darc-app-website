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
STYLE_VERSION = "4"
FORBIDDEN = ["\u2014", "\u2013", "&mdash;", "&ndash;", "&#8212;", "&#8211;"]

# file -> (title, description, canonical path)
PAGES = {
    "index.html": (
        "Darc: Dark and Light Mode for Safari",
        "Darc is a Safari extension that gives bright websites a real dark theme and dark-only "
        "websites a light one, on iPhone, iPad and Mac. No account, no servers, no subscription.",
        "",
    ),
    "support.html": (
        "Help with Darc",
        "Turn on the Darc extension in Safari on iPhone, iPad and Mac, fix a site that looks wrong, "
        "install it on your other devices and get in touch.",
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
        "The terms for using Darc, a paid app you buy once in the App Store.",
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
    <meta name="theme-color" content="#0B0A10">
    <meta name="color-scheme" content="dark">{canonical}
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Darc">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{domain}og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="The Darc app icon, a glowing violet crescent, next to the words Dark when it’s late. Light when it’s not.">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{domain}og-image.png">
    <link rel="icon" href="/favicon.ico" sizes="48x48">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="stylesheet" href="/styles.css?v={style_version}">
    <script>document.documentElement.classList.add("js")</script>"""

HEADER = """<header class="site-header">
        <div class="wrap bar">
            <a class="brand" href="/" aria-label="Darc, home">
                <picture><source type="image/avif" srcset="/img/app-icon-64.avif 1x, /img/app-icon-128.avif 2x"><img src="/img/app-icon-64.webp" srcset="/img/app-icon-64.webp 1x, /img/app-icon-128.webp 2x" width="32" height="32" alt=""></picture>
                <span>Darc</span>
            </a>
            <nav class="nav" aria-label="Main">
                <ul class="nav-links">
                    <li><a href="/#how">How it works</a></li>
                    <li><a href="/#price">Price</a></li>
                    <li><a href="/#privacy">Privacy</a></li>
                    <li><a href="/#questions">Questions</a></li>
                </ul>
            </nav>
            <a class="badge badge-nav" href="{app_store}"><img src="/img/app-store-black-en-us.svg" width="120" height="40" alt="Download Darc on the App Store"></a>
        </div>
    </header>"""

FOOTER = """<footer class="site-footer">
        <div class="wrap">
            <p class="footer-maker">Darc is made by Darius Cirjan, one person. Questions go straight to me: <a href="mailto:iosallapps@icloud.com">iosallapps@icloud.com</a>.</p>
            <nav aria-label="Footer">
                <ul class="footer-links">
                    <li><a href="/#how">How it works</a></li>
                    <li><a href="/#price">Price</a></li>
                    <li><a href="/#questions">Questions</a></li>
                    <li><a href="/support.html">Support</a></li>
                    <li><a href="/privacy.html">Privacy</a></li>
                    <li><a href="/terms.html">Terms</a></li>
                    <li><a href="/support.html#acknowledgements">Acknowledgements</a></li>
                </ul>
            </nav>
            <div class="footer-small">
                <p>Safari, iPhone, iPad, Mac and iCloud are trademarks of Apple Inc. App Store is a service mark of Apple Inc.</p>
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
                sys.exit(f"{page}: contains a forbidden dash {dash!r}")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(source)
        print("built", page)


if __name__ == "__main__":
    main()
