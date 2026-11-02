import os

HERE = os.path.dirname(os.path.abspath(__file__))
# Той самий знак, що в хедері (app/ui.html, .pmark): чотири P одна за одною
P_SHAPE = "M26 16H56A22 22 0 0 1 56 60H44V84H26ZM44 31V45H55A7 7 0 0 0 55 31Z"
LAYERS = (("Or", "#FF9A1F", "#E86A00"), ("Vi", "#9B5CFF", "#6A2BE0"), ("Co", "#FF5244", "#D62A1E"), ("Az", "#2E90FF", "#0D5FD6"))
DEFS = '''<defs>
 <linearGradient id="tile" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232C35"/><stop offset="1" stop-color="#090C10"/></linearGradient>
 <linearGradient id="rim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".30"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
 %s
 <filter id="shadow" x="-20%%" y="-20%%" width="140%%" height="150%%"><feDropShadow dx="0" dy="22" stdDeviation="22" flood-color="#000" flood-opacity=".45"/></filter>
</defs>''' % "\n ".join(
    '<linearGradient id="p%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % layer for layer in LAYERS)


def mark():
    # Знак 66.1 на 82.1 вписано по центру плитки: темний контур під кожним шаром розділяє кольори
    scale = 7.2
    s = '<g transform="translate(%.1f %.1f) scale(%s)">' % (512 - (26 + 66.1 / 2) * scale, 512 - (1.9 + 82.1 / 2) * scale, scale)
    for i, (name, _, _) in enumerate(LAYERS):
        off = (3 - i) * 4.7
        s += ('<g transform="translate(%.1f %.1f)"><path d="%s" fill="none" stroke="#090C10" stroke-width="2.4"/>'
              '<path d="%s" fill="url(#p%s)" fill-rule="evenodd"/></g>') % (off, -off, P_SHAPE, P_SHAPE, name)
    return s + "</g>"


def tile():
    return ('<rect x="100" y="100" width="824" height="824" rx="188" fill="url(#tile)" filter="url(#shadow)"/>'
            '<rect x="103" y="103" width="818" height="818" rx="185" fill="none" stroke="url(#rim)" stroke-width="6"/>')


big = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">\n%s\n%s\n%s\n</svg>' % (DEFS, tile(), mark())
open(os.path.join(HERE, "icon.svg"), "w").write(big)


def small_p(x, y, color):
    # P на піксельній сітці: ніжка, верхня й нижня перекладини, права стінка
    rects = ((x, y, 2, 8), (x, y, 5, 1), (x + 5, y + 1, 1, 2), (x, y + 3, 5, 1))
    return "".join('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (rx, ry, w, h, color) for rx, ry, w, h in rects)


# 16 і 32 px: градієнти й контури там лише розмиваються, тому шари лягають на піксельну сітку суцільними кольорами
layers = "".join(small_p(3 + off, 5 - off, color) for off, color in ((3, "#FF9A1F"), (2, "#9B5CFF"), (1, "#FF5244")))
small = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="512" height="512"><rect x="1" y="1" width="14" height="14" rx="3" fill="#10151A"/>'
         '%s%s<rect x="5" y="6" width="3" height="2" fill="#10151A"/></svg>') % (layers, small_p(3, 5, "#2E90FF"))
open(os.path.join(HERE, "icon_small.svg"), "w").write(small)
