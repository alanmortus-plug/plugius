#!/usr/bin/env python3
"""Збирає dist/Plugius.app та dist/Plugius-app.zip з вихідників (зберігає права на запуск)."""
import os, shutil, stat, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
APP = os.path.join(DIST, "Plugius.app")
CON = os.path.join(APP, "Contents")

shutil.rmtree(APP, ignore_errors=True)
os.makedirs(os.path.join(CON, "MacOS"))
os.makedirs(os.path.join(CON, "Resources"))
shutil.copytree(os.path.join(ROOT, "app"), os.path.join(CON, "Resources", "app"),
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
d = os.path.join(ROOT, "desktop")
shutil.copy(os.path.join(d, "Info.plist"), CON)
shutil.copy(os.path.join(d, "Plugius"), os.path.join(CON, "MacOS", "Plugius"))
shutil.copy(os.path.join(d, "main.swift"), os.path.join(CON, "Resources"))
shutil.copy(os.path.join(d, "Plugius.icns"), os.path.join(CON, "Resources"))
os.chmod(os.path.join(CON, "MacOS", "Plugius"), 0o755)

zpath = os.path.join(DIST, "Plugius-app.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, dns, fns in os.walk(APP):
        rel = os.path.relpath(dp, DIST)
        zi = zipfile.ZipInfo(rel + "/"); zi.external_attr = (0o40755 << 16) | 0x10; z.writestr(zi, b"")
        for f in fns:
            p = os.path.join(dp, f); r = os.path.relpath(p, DIST)
            zi = zipfile.ZipInfo(r); zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (stat.S_IFREG | (0o755 if r.endswith("MacOS/Plugius") else 0o644)) << 16
            with open(p, "rb") as fh:
                z.writestr(zi, fh.read())
print("OK:", zpath)
