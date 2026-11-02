# Малює PNG через Google Chrome без вікна й збирає desktop/Plugius.icns (iconutil, sips). Лише macOS.
import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
tmp = tempfile.mkdtemp(prefix="plugius_icon_")


def shot(name, size):
    src, out = os.path.join(tmp, name + ".svg"), os.path.join(tmp, name + ".png")
    shutil.copy(os.path.join(HERE, name + ".svg"), src)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                    "--user-data-dir=" + os.path.join(tmp, "profile"), "--screenshot=" + out,
                    "--window-size=%d,%d" % (size, size), "file://" + src], check=True, capture_output=True)
    return out


big, small = shot("icon", 1024), shot("icon_small", 512)
shutil.copy(big, os.path.join(HERE, "icon1024.png"))
iconset = os.path.join(tmp, "Plugius.iconset")
os.makedirs(iconset)
for size in (16, 32, 64, 128, 256, 512, 1024):
    source = small if size <= 32 else big
    names = []
    if size <= 512:
        names.append("icon_%dx%d.png" % (size, size))
    if size >= 32:
        names.append("icon_%dx%d@2x.png" % (size // 2, size // 2))
    for n in names:
        subprocess.run(["sips", "-z", str(size), str(size), source, "--out", os.path.join(iconset, n)], check=True, capture_output=True)
subprocess.run(["iconutil", "-c", "icns", iconset, "-o", os.path.join(os.path.dirname(HERE), "desktop", "Plugius.icns")], check=True)
shutil.rmtree(tmp, ignore_errors=True)
