import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = '''<defs>
 <linearGradient id="tile" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232C35"/><stop offset="1" stop-color="#090C10"/></linearGradient>
 <linearGradient id="rim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".30"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <linearGradient id="s0" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE0FF"/><stop offset=".55" stop-color="#4FA8FF"/><stop offset="1" stop-color="#1F6FCC"/></linearGradient>
 <linearGradient id="s1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD2CC"/><stop offset=".55" stop-color="#FF6B5E"/><stop offset="1" stop-color="#D03A2E"/></linearGradient>
 <linearGradient id="s2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E3D2FF"/><stop offset=".55" stop-color="#A97CFF"/><stop offset="1" stop-color="#7240D6"/></linearGradient>
 <linearGradient id="s3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE3B8"/><stop offset=".55" stop-color="#FFA63D"/><stop offset="1" stop-color="#D97706"/></linearGradient>
 <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="22" stdDeviation="22" flood-color="#000" flood-opacity=".45"/></filter>
</defs>'''


EDGES = ("#0E3F7A", "#7A1C15", "#3F1F85", "#7F4400")


def slot(y, i):
    # Об'єм: темний нижній край, градієнт корпусу, блик зверху; лампочка на другій смужці
    s = '<rect x="212" y="%d" width="600" height="118" rx="34" fill="%s"/>' % (y + 14, EDGES[i])
    s += '<rect x="212" y="%d" width="600" height="118" rx="34" fill="url(#s%d)"/>' % (y, i)
    s += '<rect x="238" y="%d" width="548" height="20" rx="10" fill="#fff" opacity=".4"/>' % (y + 10)
    if i == 1:
        s += '<circle cx="272" cy="%d" r="26" fill="#3A0D08"/><circle cx="264" cy="%d" r="7" fill="#fff" opacity=".8"/>' % (y + 62, y + 54)
    return s


def tile():
    return ('<rect x="100" y="100" width="824" height="824" rx="188" fill="url(#tile)" filter="url(#shadow)"/>'
            '<rect x="103" y="103" width="818" height="818" rx="185" fill="none" stroke="url(#rim)" stroke-width="6"/>')


big = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">\n%s\n%s\n%s\n</svg>' % (
    DEFS, tile(), "\n".join(slot(225 + 152 * i, i) for i in range(4)))
open(os.path.join(HERE, "icon.svg"), "w").write(big)

# 16 і 32 px: смуги лягають на піксельну сітку, без блику й лампочки, які там лише розмиваються
bars = "".join('<rect x="3" y="%d" width="10" height="2" fill="%s"/>' % (3 + 3 * i, ("#4FA8FF", "#FF6B5E", "#A97CFF", "#FFA63D")[i]) for i in range(4))
small = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="512" height="512"><rect x="1" y="1" width="14" height="14" rx="3" fill="#10151A"/>%s</svg>' % bars
open(os.path.join(HERE, "icon_small.svg"), "w").write(small)
