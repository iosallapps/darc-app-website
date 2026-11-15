"""Rewrite the shared head, header and footer of every page.

    python3 _tools/build_pages.py

Each page keeps its own content. The blocks between <!-- build:NAME --> and <!-- /build:NAME -->
are regenerated here, so a nav or footer change is made once. The script also refuses to run
if any page contains an em or en dash.
"""
import json
import os
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://darcapp.com/"
APP_STORE = "https://apps.apple.com/app/id6819036330"
APP_ID = "6819036330"
STYLE_VERSION = "8"
FORBIDDEN = ["\u2014", "\u2013", "&mdash;", "&ndash;", "&#8212;", "&#8211;"]

# file -> (title, description, canonical path)
PAGES = {
    "index.html": (
        "Darc: Dark Mode for Safari, Free on iPhone and Mac",
        "Darc is a free Safari extension that gives bright websites a real dark theme and dark-only "
        "websites a light one, on iPhone, iPad and Mac. No account needed.",
        "",
    ),
    "support.html": (
        "Darc Help: Turn On Dark Mode in Safari",
        "Turn on the Darc extension in Safari on iPhone, iPad and Mac, fix a site that looks wrong, "
        "install it on your other devices and get in touch.",
        "support.html",
    ),
    "privacy.html": (
        "Darc Privacy Policy: Safari Dark Mode App",
        "How Darc handles your data: pages are restyled on your device and your browsing never leaves "
        "Safari. Services used by the free app, consent choices and your rights.",
        "privacy.html",
    ),
    "terms.html": (
        "Darc Terms of Use: Safari Dark Mode App",
        "The terms for using Darc, the free dark mode extension for Safari: the free version, ads, the optional unlock, subscriptions, refunds and what paid-app buyers keep.",
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
    <meta name="theme-color" content="#0a0614">
    <meta name="color-scheme" content="dark">{canonical}
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Darc">
    <meta property="og:locale" content="en_US">
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
    <link rel="preload" href="/assets/fonts/instrument-serif.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="/assets/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
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
            <p class="footer-maker">Darc is made by Visto Apps, the brand of Darius Cirjan. Questions go straight to us: <a href="mailto:iosallapps@gmail.com">iosallapps@gmail.com</a>.</p>
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
                <p>This website is hosted on GitHub Pages by GitHub, Inc. Contact: <a href="mailto:iosallapps@gmail.com">iosallapps@gmail.com</a>.</p>
                <p>&copy; 2026 Visto Apps, the brand of Darius Cirjan</p>
                <p>Made by <a href="https://vistoapps.com">Visto Apps</a>. <a href="https://vistoapps.com/apps.html">More apps by Visto Apps</a></p>
            </div>
        </div>
    </footer>"""


def render_head(page):
    title, description, path = PAGES[page]
    url = DOMAIN + (path or "")
    canonical = "" if path is None else f'\n    <link rel="canonical" href="{url}">\n    <link rel="alternate" hreflang="en" href="{url}">\n    <link rel="alternate" hreflang="x-default" href="{url}">'
    if path is None:
        canonical = '\n    <meta name="robots" content="noindex">'
    head = HEAD.format(app_id=APP_ID, title=title, description=description, canonical=canonical,
                       url=url, domain=DOMAIN, style_version=STYLE_VERSION)
    return head + jsonld(page, title, description, url)


ORG = {"@type": "Organization", "name": "Visto Apps", "url": "https://vistoapps.com",
       "founder": {"@type": "Person", "name": "Darius Cirjan"}}


def faq_entities():
    with open(os.path.join(SITE, "index.html"), encoding="utf-8") as handle:
        source = handle.read()
    out = []
    for summary, answer in re.findall(r"<summary>(.*?)</summary>\s*<div class=\"answer\">(.*?)</div>", source, re.S):
        text = re.sub(r"<[^>]+>", "", answer)
        text = text.replace("&amp;", "&").strip()
        out.append({"@type": "Question", "name": summary.strip(), "acceptedAnswer": {"@type": "Answer", "text": text}})
    return out


def jsonld(page, title, description, url):
    graph = []
    if page == "index.html":
        graph.append({"@context": "https://schema.org", "@type": "WebSite", "name": "Darc", "url": DOMAIN,
                      "publisher": ORG, "inLanguage": "en"})
        graph.append({
            "@context": "https://schema.org", "@type": "MobileApplication", "name": "Darc: Dark Mode for Safari",
            "description": description, "url": DOMAIN, "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "iOS 18.0 or later, iPadOS 18.0 or later, macOS 15.0 or later",
            "downloadUrl": APP_STORE, "installUrl": APP_STORE, "image": DOMAIN + "img/app-icon-256.webp",
            "screenshot": [DOMAIN + "img/framed-dashboard-600.webp", DOMAIN + "img/framed-enable-600.webp",
                           DOMAIN + "img/popup-menu-680.webp"],
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "author": ORG, "publisher": ORG, "inLanguage": "en"})
        graph.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities()})
    elif page != "404.html":
        graph.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Darc", "item": DOMAIN},
            {"@type": "ListItem", "position": 2, "name": title, "item": url}]})
    if not graph:
        return ""
    body = json.dumps(graph, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return '\n    <script type="application/ld+json">\n' + body + "\n    </script>"


def write_sitemap(today):
    rows = []
    for page, (title, description, path) in PAGES.items():
        if path is None:
            continue
        url = DOMAIN + path
        rows.append(f'    <url><loc>{url}</loc><lastmod>{today}</lastmod>'
                    f'<xhtml:link rel="alternate" hreflang="en" href="{url}"/>'
                    f'<xhtml:link rel="alternate" hreflang="x-default" href="{url}"/></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as handle:
        handle.write(xml)


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
    write_sitemap("2026-11-15")


if __name__ == "__main__":
    main()
