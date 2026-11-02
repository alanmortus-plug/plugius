import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
# Той самий знак, що в хедері (app/ui.html, .logo): блакитна P зі шрифту, за нею ліворуч три шари
# Плитка суцільна, як тло хедера: контур шарів того самого кольору зливається з нею й лишається лише проміжком між шарами
TILE = "#12161A"
LAYERS = ((.165, "#FF9A1F"), (.11, "#9B5CFF"), (.055, "#FF5244"), (0, TILE))
FONT_SIZE = 824
# Шрифт береться з ui.html, щоб літера була точно такою, як у хедері, а іконка не залежала від установлених шрифтів
with open(os.path.join(os.path.dirname(HERE), "app", "ui.html"), encoding="utf8") as f:
    faces = [m for m in re.findall(r"@font-face\{.*?\}", f.read(), re.S) if "Plugius Display" in m and "font-weight:700" in m]
assert len(faces) == 1
DEFS = '''<defs>
 <style>%s</style>
 <linearGradient id="rim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".30"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <linearGradient id="front" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4FA3FF"/><stop offset="1" stop-color="#0D5FD6"/></linearGradient>
 <filter id="shadow" color-interpolation-filters="sRGB" x="-20%%" y="-20%%" width="140%%" height="150%%"><feDropShadow dx="0" dy="22" stdDeviation="22" flood-color="#000" flood-opacity=".45"/></filter>
</defs>''' % faces[0]


def mark():
    # Висота великих літер .655em, друкована частина від -.135em (лівий шар) до .36em: вписано по центру плитки
    x0, base = 512 - .1125 * FONT_SIZE, 512 + .655 * FONT_SIZE / 2
    attrs = 'y="%.1f" font-family="Plugius Display" font-weight="700" font-size="%d"' % (base, FONT_SIZE)
    s = ""
    for off, color in LAYERS:
        s += '<text x="%.1f" %s fill="%s" stroke="%s" stroke-width="%.1f" paint-order="stroke fill">P</text>' % (x0 - off * FONT_SIZE, attrs, color, TILE, .05 * FONT_SIZE)
    return s + '<text x="%.1f" %s fill="url(#front)">P</text>' % (x0, attrs)


def tile():
    return ('<rect x="100" y="100" width="824" height="824" rx="188" fill="%s" filter="url(#shadow)"/>' % TILE +
            '<rect x="103" y="103" width="818" height="818" rx="185" fill="none" stroke="url(#rim)" stroke-width="6"/>')


big = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">\n%s\n%s\n%s\n</svg>' % (DEFS, tile(), mark())
open(os.path.join(HERE, "icon.svg"), "w").write(big)

# 16 і 32 px: шрифт там розмивається, тому той самий знак намальовано на піксельній сітці
layers = "".join('<rect x="%d" y="3" width="1" height="10" fill="%s"/>' % (x, c) for x, c in ((4, "#FF9A1F"), (5, "#9B5CFF"), (6, "#FF5244")))
small = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="512" height="512"><rect x="1" y="1" width="14" height="14" rx="3" fill="#12161A"/>'
         '%s<rect x="7" y="3" width="2" height="10" fill="#2E90FF"/><rect x="9" y="3" width="3" height="2" fill="#2E90FF"/>'
         '<rect x="11" y="5" width="1" height="2" fill="#2E90FF"/><rect x="9" y="7" width="3" height="2" fill="#2E90FF"/></svg>') % layers
open(os.path.join(HERE, "icon_small.svg"), "w").write(small)
