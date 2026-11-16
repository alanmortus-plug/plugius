#!/usr/bin/env python3
"""Завантажує вбудований Python для Plugius.app (python-build-standalone, обидві архітектури).

Результат: build/python/arm64/ і build/python/x86_64/ (корені збірок: bin/, lib/).
Архіви кешуються в build/downloads/ і перевіряються за SHA-256 перед розпакуванням.
"""
import hashlib, os, shutil, sys, tarfile, tempfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
RELEASE = "20261026"
VERSION = "3.13.18"
BASE = "https://github.com/astral-sh/python-build-standalone/releases/download/" + RELEASE + "/"
BUILDS = {
    "arm64": ("cpython-%s+%s-aarch64-apple-darwin-install_only_stripped.tar.gz" % (VERSION, RELEASE),
              "8392b6ea51d94391befb2c31ebe75463f045d0b69dfcf5e1bb3234e1f5fa3405"),
    "x86_64": ("cpython-%s+%s-x86_64-apple-darwin-install_only_stripped.tar.gz" % (VERSION, RELEASE),
               "7412c19d896c99431b74a18a5643e110449a7f9590fbab179c3e5ab27b9aa9e3"),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_members(tar, dest):
    """Для Python без tarfile.data_filter: не випускає файли й посилання за межі dest."""
    dest = os.path.realpath(dest)
    for m in tar.getmembers():
        target = os.path.realpath(os.path.join(dest, m.name))
        if not (target == dest or target.startswith(dest + os.sep)):
            raise ValueError("небезпечний шлях в архіві: " + m.name)
        if m.issym() or m.islnk():
            link = os.path.realpath(os.path.join(dest, os.path.dirname(m.name), m.linkname)
                                    if m.issym() else os.path.join(dest, m.linkname))
            if not (link == dest or link.startswith(dest + os.sep)):
                raise ValueError("посилання за межі архіву: " + m.name)
        if not (m.isfile() or m.isdir() or m.issym() or m.islnk()):
            raise ValueError("неочікуваний тип файлу в архіві: " + m.name)
        yield m


def fetch(arch):
    name, digest = BUILDS[arch]
    dl = os.path.join(BUILD, "downloads")
    os.makedirs(dl, exist_ok=True)
    tgz = os.path.join(dl, name)
    if not (os.path.exists(tgz) and sha256(tgz) == digest):
        print("Завантажую", name)
        tmp = tgz + ".part"
        with urllib.request.urlopen(BASE + name.replace("+", "%2B"), timeout=60) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        if sha256(tmp) != digest:
            os.remove(tmp)
            sys.exit("Помилка: SHA-256 не збігається для " + name)
        os.replace(tmp, tgz)
    out = os.path.join(BUILD, "python", arch)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmpdir = tempfile.mkdtemp(dir=os.path.dirname(out))
    try:
        with tarfile.open(tgz) as t:
            if hasattr(tarfile, "data_filter"):
                t.extractall(tmpdir, filter="data")
            else:
                t.extractall(tmpdir, members=safe_members(t, tmpdir))
        os.rename(os.path.join(tmpdir, "python"), out)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    print("OK:", out)


if __name__ == "__main__":
    for a in BUILDS:
        fetch(a)
