#!/usr/bin/env python3
"""Generate the SLDS 2 styled chrome used by the profile README.

GitHub strips CSS from markdown, so the SLDS look (page header, card headers,
badge pills) is rendered as SVG instead. Every element is emitted twice --
`<name>.light.svg` and `<name>.dark.svg` -- so the README can serve the right
one with <picture media="(prefers-color-scheme: dark)">.

Usage: python tools/slds_cards.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_PATH = os.path.join(ROOT, "tools", "slds.tokens.json")
OUT_DIR = os.path.join(ROOT, "img", "slds")

WIDTH = 900
CARD_H = 48
HERO_H = 132

FONT = "'Salesforce Sans',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
RADIUS = 4

# Glyphs are drawn on a 24x24 grid; {fg} is substituted with the tile foreground.
GLYPHS = {
    "bolt": '<path d="M13.6 2 5 13.4h4.9L8.4 22 19 10.6h-5.4z" fill="{fg}"/>',
    "user": '<circle cx="12" cy="8" r="4.1" fill="{fg}"/>'
            '<path d="M3.6 21.4c0-4.6 3.8-8.4 8.4-8.4s8.4 3.8 8.4 8.4z" fill="{fg}"/>',
    "code": '<path d="M8.6 5.9 2.5 12l6.1 6.1 1.9-1.9L6.3 12l4.2-4.2zM15.4 5.9l-1.9 1.9 4.2 4.2'
            '-4.2 4.2 1.9 1.9L21.5 12z" fill="{fg}"/>',
    "apps": '<rect x="3" y="3" width="7.5" height="7.5" rx="1.6" fill="{fg}"/>'
            '<rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6" fill="{fg}"/>'
            '<rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6" fill="{fg}"/>'
            '<rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6" fill="{fg}"/>',
    "chart": '<rect x="3" y="13" width="4.4" height="8" rx="1.2" fill="{fg}"/>'
             '<rect x="9.8" y="7.5" width="4.4" height="13.5" rx="1.2" fill="{fg}"/>'
             '<rect x="16.6" y="3" width="4.4" height="18" rx="1.2" fill="{fg}"/>',
    "pulse": '<path d="M2.2 12h4l2.9-7.2 4.1 14.4 2.9-7.2h5.7" fill="none" stroke="{fg}" '
             'stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>',
    # {bg} paints the details back in the tile colour, cutting them out of the page shape.
    "doc": '<path d="M5.5 2.4h7.8l6.2 6.2v13h-14z" fill="{fg}"/>'
           '<path d="M13 3.2v6h6" fill="none" stroke="{bg}" stroke-width="1.6"/>'
           '<g fill="{bg}"><rect x="8" y="12" width="8" height="1.7" rx="0.85"/>'
           '<rect x="8" y="15.4" width="8" height="1.7" rx="0.85"/></g>',
    "link": '<g fill="{fg}"><path d="M9.5 15.7a4.9 4.9 0 0 1 0-6.9l2.8-2.8a4.9 4.9 0 0 1 6.9 6.9'
            'l-1.4 1.4-1.8-1.8 1.4-1.4a2.4 2.4 0 0 0-3.4-3.4l-2.8 2.8a2.4 2.4 0 0 0 0 3.4z"/>'
            '<path d="M14.5 8.3a4.9 4.9 0 0 1 0 6.9l-2.8 2.8a4.9 4.9 0 0 1-6.9-6.9l1.4-1.4 1.8 1.8'
            '-1.4 1.4a2.4 2.4 0 0 0 3.4 3.4l2.8-2.8a2.4 2.4 0 0 0 0-3.4z"/></g>',
}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_width(label, size):
    """Rough advance width for a mixed-case label in the SLDS font stack."""
    return len(label) * size * 0.58


def svg_open(width, height):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            'viewBox="0 0 {w} {h}" role="img">').format(w=width, h=height)


def tile(x, y, size, glyph, bg, fg, radius):
    """Brand-coloured rounded tile with a centred glyph, SLDS icon-container style."""
    inner = size * 0.62
    scale = inner / 24.0
    gx = x + (size - inner) / 2
    gy = y + (size - inner) / 2
    return ('<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{r}" fill="{bg}"/>'
            '<g transform="translate({gx:.2f},{gy:.2f}) scale({sc:.4f})">{glyph}</g>').format(
                x=x, y=y, s=size, r=radius, bg=bg, gx=gx, gy=gy, sc=scale,
                glyph=GLYPHS[glyph].format(fg=fg, bg=bg))


def pill(x, y, label, t, height=22):
    """SLDS badge. Returns (markup, width)."""
    size = 12
    width = text_width(label, size) + 24
    markup = ('<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{r}" fill="{bg}"/>'
              '<text x="{tx:.1f}" y="{ty:.1f}" font-family="{font}" font-size="{fs}" '
              'font-weight="600" fill="{fg}" text-anchor="middle">{label}</text>').format(
                  x=x, y=y, w=width, h=height, r=height / 2, bg=t["accent-container-1"],
                  tx=x + width / 2, ty=y + height / 2 + 4.2, font=FONT, fs=size,
                  fg=t["on-accent-container-1"], label=esc(label))
    return markup, width


def card_header(t, title, glyph, meta=""):
    """SLDS card header: icon tile, title, optional right-aligned meta, bottom divider."""
    r = RADIUS
    body = [svg_open(WIDTH, CARD_H), "<title>{0}</title>".format(esc(title))]
    # Only the top corners are rounded: the markdown body continues right below.
    body.append('<path d="M0 {r}a{r} {r} 0 0 1 {r}-{r}h{inner}a{r} {r} 0 0 1 {r} {r}v{rest}H0z" '
                'fill="{bg}"/>'.format(r=r, inner=WIDTH - 2 * r, rest=CARD_H - r,
                                       bg=t["surface-1"]))
    body.append(tile(16, 12, 24, glyph, t["accent-1"], t["on-accent-1"], RADIUS))
    body.append('<text x="52" y="30.5" font-family="{font}" font-size="15.5" font-weight="700" '
                'fill="{fg}">{title}</text>'.format(font=FONT, fg=t["on-surface-1"],
                                                    title=esc(title)))
    if meta:
        body.append('<text x="{x}" y="30.5" font-family="{font}" font-size="12" fill="{fg}" '
                    'text-anchor="end">{meta}</text>'.format(x=WIDTH - 16, font=FONT,
                                                             fg=t["on-surface-3"], meta=esc(meta)))
    body.append('<rect x="0" y="{y}" width="{w}" height="1" fill="{c}"/>'.format(
        y=CARD_H - 1, w=WIDTH, c=t["border-1"]))
    body.append("</svg>")
    return "".join(body)


def hero(t, title, subtitle, meta, pills):
    """SLDS page header: accent bar, brand tile, eyebrow, title, subtitle, badge row."""
    body = [svg_open(WIDTH, HERO_H),
            "<title>{0} - {1}</title>".format(esc(title), esc(subtitle))]
    body.append('<rect x="0.5" y="0.5" width="{w}" height="{h}" rx="{r}" fill="{bg}" '
                'stroke="{br}"/>'.format(w=WIDTH - 1, h=HERO_H - 1, r=RADIUS, bg=t["surface-1"],
                                         br=t["border-1"]))
    body.append('<path d="M{r} 1h{inner}a{r} {r} 0 0 1 {r} {r}v1H1V{r}a{r} {r} 0 0 1 {r}-{r}z" '
                'fill="{c}"/>'.format(r=RADIUS, inner=WIDTH - 2 - 2 * RADIUS, c=t["accent-1"]))
    body.append('<rect x="1" y="{y}" width="{w}" height="3" fill="{c}"/>'.format(
        y=1 + RADIUS, w=WIDTH - 2, c=t["accent-1"]))
    body.append(tile(24, 34, 52, "bolt", t["accent-1"], t["on-accent-1"], 8))
    body.append('<text x="92" y="52" font-family="{font}" font-size="12" font-weight="600" '
                'fill="{fg}" letter-spacing="0.8">{meta}</text>'.format(
                    font=FONT, fg=t["on-surface-3"], meta=esc(meta.upper())))
    body.append('<text x="92" y="79" font-family="{font}" font-size="25" font-weight="700" '
                'fill="{fg}">{title}</text>'.format(font=FONT, fg=t["on-surface-1"],
                                                    title=esc(title)))
    body.append('<text x="92" y="101" font-family="{font}" font-size="13.5" fill="{fg}">'
                '{sub}</text>'.format(font=FONT, fg=t["on-surface-2"], sub=esc(subtitle)))
    # Pills are laid out right to left so the row stays flush with the card edge.
    x = WIDTH - 24
    rendered = []
    for label in reversed(pills):
        markup, w = pill(0, 0, label, t)
        x -= w
        rendered.append('<g transform="translate({x:.1f},36)">{m}</g>'.format(x=x, m=markup))
        x -= 8
    body.extend(rendered)
    body.append("</svg>")
    return "".join(body)


def badge_row(t, labels, max_width=WIDTH):
    """Wrapping row of SLDS badges; height grows with the number of lines."""
    gap, line_h, row_h = 8, 30, 22
    rows, current, used = [], [], 0.0
    for label in labels:
        _, w = pill(0, 0, label, t)
        if current and used + w > max_width:
            rows.append(current)
            current, used = [], 0.0
        current.append((label, w))
        used += w + gap
    if current:
        rows.append(current)

    height = len(rows) * line_h - (line_h - row_h)
    body = [svg_open(max_width, height), "<title>{0}</title>".format(esc(", ".join(labels)))]
    for i, row in enumerate(rows):
        x = 0.0
        for label, w in row:
            markup, _ = pill(x, i * line_h, label, t)
            body.append(markup)
            x += w + gap
    body.append("</svg>")
    return "".join(body)


CARDS = [
    ("card-about", "About", "user", "Network & Telco engineer"),
    ("card-projects", "Open source projects", "code", "Live counters"),
    ("card-writing", "Writing", "doc", "medium.com"),
    ("card-tech", "Technologies", "apps", ""),
    ("card-stats", "GitHub stats", "chart", ""),
    ("card-activity", "Am I up?", "pulse", "Steam"),
    ("card-links", "Links", "link", ""),
]

LANGS = ["C++", "Apex", "PHP", "Python", "Java", "Scala", "Shell"]
DBS = ["PostgreSQL", "MySQL", "InfluxDB", "MongoDB"]

HERO = {
    "title": "Alan Jaouen",
    "subtitle": "Network & Telco engineer - Salesforce architecture, France",
    "meta": "Profile",
    "pills": ["Salesforce", "Telco", "C++"],
}


def main():
    with open(TOKENS_PATH, encoding="utf-8") as fh:
        tokens = json.load(fh)

    global FONT, RADIUS
    FONT = tokens["font"]
    RADIUS = tokens["radius"]

    os.makedirs(OUT_DIR, exist_ok=True)
    written = []
    for theme_name, t in tokens["themes"].items():
        files = {
            "hero": hero(t, HERO["title"], HERO["subtitle"], HERO["meta"], HERO["pills"]),
            "badges-langs": badge_row(t, LANGS),
            "badges-db": badge_row(t, DBS),
        }
        for name, title, glyph, meta in CARDS:
            files[name] = card_header(t, title, glyph, meta)
        for name, markup in files.items():
            path = os.path.join(OUT_DIR, "{0}.{1}.svg".format(name, theme_name))
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(markup + "\n")
            written.append(os.path.relpath(path, ROOT).replace(os.sep, "/"))

    for path in sorted(written):
        print(path)
    print("{0} files written".format(len(written)))


if __name__ == "__main__":
    main()
