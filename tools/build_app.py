#!/usr/bin/env python3
"""Збирає dist/Plugius.app і dist/Plugius-app.zip.

У застосунок ідуть готовий універсальний Swift-бінарник (arm64 + x86_64) і вбудований
універсальний Python, тож на Mac користувача не потрібні Command Line Tools.
Потрібно на Mac збирача: Command Line Tools (swiftc, lipo, codesign) і один раз
`python3 tools/fetch_python.py` (завантажує Python у build/python/).
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
APP = os.path.join(DIST, "Plugius.app")
CON = os.path.join(APP, "Contents")
PYBUILD = os.path.join(ROOT, "build", "python")
ARCHS = ("arm64", "x86_64")
MIN_MACOS = "11.3"  # як LSMinimumSystemVersion в Info.plist

# Mach-O: тонкі 64/32-біт (little-endian на диску) і універсальний (fat)
MACHO_MAGIC = (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe")

# Частини Python, які застосунку не потрібні (шляхи відносно кореня збірки)
PRUNE_TOP = ("include", "share")
PRUNE_LIB_PREFIX = ("tcl", "tk", "itcl", "thread", "libtcl", "libtk", "pkgconfig", "libpython")
PRUNE_STDLIB = {"tkinter", "idlelib", "turtledemo", "ensurepip", "lib2to3", "pydoc_data",
                "site-packages", "venv", "test"}
KEEP_BIN = {"python3", "python3.13"}


class BuildError(Exception):
    pass


def prune_python(rel):
    """True, якщо файл чи теку (шлях через «/») не треба класти в застосунок."""
    parts = rel.split("/")
    if "__pycache__" in parts or parts[0] in PRUNE_TOP:
        return True
    if parts[0] == "bin":
        return len(parts) > 1 and parts[1] not in KEEP_BIN
    if parts[0] == "lib" and len(parts) > 1:
        if parts[1].startswith(PRUNE_LIB_PREFIX):
            return True
        if parts[1].startswith("python3") and len(parts) > 2:
            if parts[2].startswith("config-") or parts[2] in PRUNE_STDLIB:
                return True
            if parts[2] == "lib-dynload" and len(parts) > 3 and parts[3].startswith("_tkinter"):
                return True
    return False


def is_macho(path):
    if os.path.islink(path) or not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        return f.read(4) in MACHO_MAGIC


def macho_files(root):
    out = []
    for dp, dns, fns in os.walk(root):
        for f in sorted(fns):
            p = os.path.join(dp, f)
            if is_macho(p):
                out.append(p)
    return sorted(out)


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if p.returncode != 0:
        raise BuildError("%s\n%s" % (" ".join(cmd), p.stdout))
    return p.stdout


def run_lipo(a, b, out):
    run(["lipo", "-create", a, b, "-output", out])


def assemble_python(arm, x86, dest, lipo=run_lipo):
    """Складає універсальну збірку Python: файли з arm, кожен Mach-O склеєно з парою з x86."""
    for dp, dns, fns in os.walk(arm):
        rel_dir = os.path.relpath(dp, arm)
        rel_dir = "" if rel_dir == "." else rel_dir.replace(os.sep, "/") + "/"
        os.makedirs(os.path.join(dest, rel_dir), exist_ok=True)
        keep_dirs = []
        for d in dns:
            src = os.path.join(dp, d)
            if prune_python(rel_dir + d):
                continue
            if os.path.islink(src):
                os.symlink(os.readlink(src), os.path.join(dest, rel_dir, d))
            else:
                keep_dirs.append(d)
        dns[:] = keep_dirs
        for f in fns:
            rel = rel_dir + f
            if prune_python(rel):
                continue
            src, out = os.path.join(dp, f), os.path.join(dest, rel)
            if os.path.islink(src):
                os.symlink(os.readlink(src), out)
            elif is_macho(src):
                other = os.path.join(x86, rel)
                if not is_macho(other):
                    raise BuildError("немає x86_64-пари для " + rel)
                lipo(src, other, out)
                os.chmod(out, os.stat(src).st_mode & 0o777)
            else:
                shutil.copy2(src, out)


def sign(path):
    run(["codesign", "-s", "-", "--force", path])


def build_swift(src, out):
    """Універсальний бінарник оболонки з ad-hoc підписом."""
    parts = []
    for arch in ARCHS:
        part = out + "." + arch
        cmd = ["xcrun", "swiftc", "-O", "-swift-version", "5", "-target", "%s-apple-macos%s" % (arch, MIN_MACOS)]
        if arch == "x86_64":
            # Нові Command Line Tools (macOS 27) не мають x86_64-версій бібліотек сумісності Swift;
            # оболонка не використовує concurrency, тож вони не потрібні.
            cmd += ["-runtime-compatibility-version", "none"]
        run(cmd + [src, "-o", part, "-framework", "Cocoa", "-framework", "WebKit"])
        parts.append(part)
    run(["lipo", "-create"] + parts + ["-output", out])
    for p in parts:
        os.remove(p)
    sign(out)


def main():
    for arch in ARCHS:
        if not os.path.isfile(os.path.join(PYBUILD, arch, "bin", "python3")):
            raise BuildError("Немає вбудованого Python (%s). Спершу: python3 tools/fetch_python.py" % arch)
    if sys.platform != "darwin":
        raise BuildError("Застосунок збирається лише на macOS (потрібні swiftc, lipo, codesign)")

    shutil.rmtree(APP, ignore_errors=True)
    res = os.path.join(CON, "Resources")
    os.makedirs(os.path.join(CON, "MacOS"))
    os.makedirs(res)
    shutil.copytree(os.path.join(ROOT, "app"), os.path.join(res, "app"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    d = os.path.join(ROOT, "desktop")
    shutil.copy(os.path.join(d, "Info.plist"), CON)
    shutil.copy(os.path.join(d, "Plugius"), os.path.join(CON, "MacOS", "Plugius"))
    os.chmod(os.path.join(CON, "MacOS", "Plugius"), 0o755)
    shutil.copy(os.path.join(d, "main.swift"), res)  # для запасного збирання в лаунчері
    shutil.copy(os.path.join(d, "Plugius.icns"), res)

    build_swift(os.path.join(d, "main.swift"), os.path.join(CON, "MacOS", "Plugius-bin"))

    py = os.path.join(res, "python")
    assemble_python(os.path.join(PYBUILD, "arm64"), os.path.join(PYBUILD, "x86_64"), py)
    for m in macho_files(py):
        sign(m)

    zpath = os.path.join(DIST, "Plugius-app.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    # ditto зберігає права й посилання (zipfile посилань не тримає). Без розширених атрибутів:
    # інакше в архів потрапляють службові файли ._* (com.apple.provenance тощо).
    # Підписи Mach-O вбудовані у файли, тож атрибути для них не потрібні.
    run(["ditto", "-c", "-k", "--norsrc", "--noextattr", "--noacl", "--keepParent", APP, zpath])
    print("OK:", zpath)


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        sys.exit("Помилка збірки: %s" % e)
