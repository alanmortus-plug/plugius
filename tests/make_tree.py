# -*- coding: utf-8 -*-
"""Створює змодельований «диск macOS» з плагінами для тестів."""
import json
import os
import plistlib
import struct
import sys
from datetime import datetime, timedelta


def w(path, data=b"", mode="wb"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as f:
        f.write(data)


def fat_macho(archs):
    cpu = {"x86_64": 0x01000007, "arm64": 0x0100000c, "i386": 7}
    hdr = b"\xca\xfe\xba\xbe" + struct.pack(">I", len(archs))
    for a in archs:
        hdr += struct.pack(">IIIII", cpu[a], 3, 4096, 100, 12)
    return hdr + b"\x00" * 200


def thin_macho(arch):
    cpu = {"x86_64": 0x01000007, "arm64": 0x0100000c}
    return b"\xcf\xfa\xed\xfe" + struct.pack("<I", cpu[arch]) + b"\x00" * 200


def bundle(root, rel, info, exe=None, files=None):
    p = os.path.join(root, rel)
    os.makedirs(os.path.join(p, "Contents", "MacOS"), exist_ok=True)
    with open(os.path.join(p, "Contents", "Info.plist"), "wb") as f:
        plistlib.dump(info, f)
    if exe is not None:
        w(os.path.join(p, "Contents", "MacOS", info.get("CFBundleExecutable", "plug")), exe)
    for k, v in (files or {}).items():
        w(os.path.join(p, k), v)
    return p


def pe_dll(company=None, version=None, symbol=b"VSTPluginMain", machine=0x8664, pad=70000):
    b = bytearray(b"MZ" + b"\x00" * 62)
    b[0x3C:0x40] = struct.pack("<I", 0x80)
    b += b"\x00" * (0x80 - len(b))
    b += b"PE\x00\x00" + struct.pack("<H", machine) + b"\x00" * 100
    if symbol:
        b += b"\x00" + symbol + b"\x00"
    b += b"\x00" * 33  # робимо зсув парним
    if len(b) % 2:
        b += b"\x00"
    if company:
        b += "CompanyName".encode("utf-16-le") + b"\x00\x00\x00\x00" + company.encode("utf-16-le") + b"\x00\x00"
    if version:
        b += "FileVersion".encode("utf-16-le") + b"\x00\x00\x00\x00" + version.encode("utf-16-le") + b"\x00\x00"
    b += b"\x00" * pad
    return bytes(b)


def build(root, home):
    L = os.path.join(root, "Library/Audio/Plug-Ins")
    # --- AU сторонні
    bundle(root, "Library/Audio/Plug-Ins/Components/FabFilter Pro-Q 3.component", {
        "CFBundleIdentifier": "com.fabfilter.Pro-Q.3.AU", "CFBundleExecutable": "FabFilter Pro-Q 3",
        "CFBundleShortVersionString": "3.21", "NSHumanReadableCopyright": "© 2023 FabFilter Software Instruments",
        "AudioComponents": [{"name": "FabFilter: Pro-Q 3", "manufacturer": "FabF", "type": "aufx", "subtype": "FQ3 ", "version": 1}]},
        exe=fat_macho(["x86_64", "arm64"]), files={"Contents/Resources/data.bin": b"x" * 20000})
    bundle(root, "Library/Audio/Plug-Ins/Components/Serum.component", {
        "CFBundleIdentifier": "com.xferrecords.Serum.AU", "CFBundleExecutable": "Serum", "CFBundleShortVersionString": "1.368",
        "AudioComponents": [{"name": "Xfer Records: Serum", "manufacturer": "XfRc", "type": "aumu"}]},
        exe=thin_macho("x86_64"), files={"Contents/Resources/x.bin": b"x" * 50000})
    # --- AU Apple (штатні для Logic)
    bundle(root, "Library/Audio/Plug-Ins/Components/AUDelay.component", {
        "CFBundleIdentifier": "com.apple.audio.units.Components", "CFBundleExecutable": "AUDelay",
        "AudioComponents": [{"name": "Apple: AUDelay", "manufacturer": "appl", "type": "aufx"}]}, exe=thin_macho("arm64"))
    bundle(root, "Library/Application Support/Logic/Plug-In Extras/LogicThing.component", {
        "CFBundleIdentifier": "com.vendor.LogicThing", "CFBundleExecutable": "LogicThing"}, exe=thin_macho("arm64"))
    # --- VST3 з moduleinfo.json
    p = bundle(root, "Library/Audio/Plug-Ins/VST3/Valhalla VintageVerb.vst3", {
        "CFBundleIdentifier": "com.valhalladsp.ValhallaVintageVerb", "CFBundleExecutable": "ValhallaVintageVerb",
        "CFBundleShortVersionString": "3.0.0"}, exe=fat_macho(["arm64"]))
    w(os.path.join(p, "Contents/Resources/moduleinfo.json"), json.dumps({
        "Name": "ValhallaVintageVerb", "Vendor": "Valhalla DSP, LLC", "Version": "3.0.0",
        "Classes": [{"Category": "Audio Module Class", "Sub Categories": ["Fx", "Reverb"]}]}).encode())
    # Waves
    bundle(root, "Library/Audio/Plug-Ins/VST3/WaveShell1-VST3 14.0.vst3", {
        "CFBundleIdentifier": "com.WavesAudio.WaveShell1-VST3", "CFBundleExecutable": "WaveShell", "CFBundleShortVersionString": "14.0",
        "NSHumanReadableCopyright": "Copyright (c) 2023 Waves Audio Ltd."}, exe=fat_macho(["x86_64", "arm64"]))
    # старий 32-бітний VST2
    bundle(root, "Library/Audio/Plug-Ins/VST/OldComp.vst", {
        "CFBundleIdentifier": "com.oldco.OldComp", "CFBundleExecutable": "OldComp", "CFBundleShortVersionString": "1.0"},
        exe=fat_macho(["i386"]))
    # плагін без метаданих, лише з назви теки
    bundle(root, "Library/Audio/Plug-Ins/CLAP/Surge Synth Team/Surge XT.clap", {
        "CFBundleExecutable": "Surge XT", "CFBundleShortVersionString": "1.3.1"}, exe=thin_macho("arm64"))
    # --- AAX: сторонній і штатні Pro Tools
    base = "Library/Application Support/Avid/Audio/Plug-Ins"
    bundle(root, base + "/Pro-Q 3.aaxplugin", {"CFBundleIdentifier": "com.fabfilter.Pro-Q.3.AAX", "CFBundleExecutable": "q", "CFBundleShortVersionString": "3.21"}, exe=thin_macho("x86_64"))
    bundle(root, base + "/AIR Reverb.aaxplugin", {"CFBundleIdentifier": "com.airmusictech.reverb", "CFBundleExecutable": "r"}, exe=thin_macho("x86_64"))
    bundle(root, base + "/EQ III.aaxplugin", {"CFBundleExecutable": "e"}, exe=thin_macho("x86_64"))
    bundle(root, base + "/Mystery Fx.aaxplugin", {"CFBundleExecutable": "m"}, exe=thin_macho("x86_64"))
    # --- не-macOS
    wine = os.path.join(home, ".wine/drive_c/Program Files/VstPlugins")
    w(os.path.join(wine, "TDR Nova.dll"), pe_dll("Tokyo Dawn Labs", "2.1.3"))
    w(os.path.join(wine, "oldskool.dll"), pe_dll(symbol=None))  # без символів — «низька впевненість»
    w(os.path.join(home, ".wine/drive_c/windows/system32/kernel32.dll"), pe_dll(symbol=None))
    w(os.path.join(home, "Documents/random/library.dll"), pe_dll(symbol=b"SomeOtherExport", pad=1000))  # НЕ плагін
    w(os.path.join(home, "Music/Win Plugins/BigSynth.dll"), pe_dll("Big Co", "9.0", symbol=b"GetPluginFactory"))
    w(os.path.join(home, ".vst/linuxfx.so"), b"\x7fELF" + b"\x00" * 14 + struct.pack("<H", 0x3e) + b"\x00VSTPluginMain\x00" + b"\x00" * 100)
    w(os.path.join(home, ".vst/notaplugin.so"), b"\x7fELF" + b"\x00" * 200)
    w(os.path.join(home, "dev/proj/node_modules/x/evil.vst3/Contents/Info.plist"), b"")  # має бути пропущено
    os.makedirs(os.path.join(home, ".lv2/calf.lv2"))
    w(os.path.join(home, ".lv2/calf.lv2/manifest.ttl"), b"@prefix lv2: ...")
    w(os.path.join(home, "Music/Win Plugins/Tool.vst3/Contents/x86_64-win/Tool.vst3"), pe_dll("WinCo", "1.0", symbol=b"GetPluginFactory"))
    # --- ліцензії та інсталятори
    w(os.path.join(root, "Library/Application Support/Waves/Licenses/WaveShell.wlic"), b"lic")
    w(os.path.join(home, "Library/Application Support/u-he/Zebra2.u-he-act"), b"key")
    w(os.path.join(home, "Downloads/FabFilter-Pro-Q-3-Installer.dmg"), b"dmg")
    w(os.path.join(home, "Downloads/readme.txt"), b"x")
    # --- Mac налаштовано «зараз», а Serum має дату створення 2020 (як після міграції)
    w(os.path.join(root, "var/db/.AppleSetupDone"), b"")
    old = os.path.join(root, "Library/Audio/Plug-Ins/Components/Serum.component")
    os.utime(old, (1590000000, 1590000000))
    # --- плагіни без прив'язки файлу до пакета: дату дає лише журнал встановлень (як у Native Instruments)
    for rel, fmt_exe in (("Library/Audio/Plug-Ins/Components/Replika.component", "AU"),
                         ("Library/Application Support/Avid/Audio/Plug-Ins/Replika.aaxplugin", "AAX")):
        p = bundle(root, rel, {"CFBundleIdentifier": "com.native-instruments.Replika." + fmt_exe, "CFBundleExecutable": "r",
                               "NSHumanReadableCopyright": "Copyright © 2020 Native Instruments GmbH"}, exe=thin_macho("arm64"))
        os.utime(p, (1590000000, 1590000000))
    bundle(root, base + "/AutoAlign2.aaxplugin", {"CFBundleIdentifier": "com.soundradix.AutoAlign2.aax", "CFBundleExecutable": "a"}, exe=thin_macho("arm64"))
    bundle(root, "Library/Audio/Plug-Ins/VST3/Splitter.vst3", {"CFBundleIdentifier": "com.goodco.Splitter", "CFBundleExecutable": "s"}, exe=thin_macho("arm64"))
    bundle(root, "Library/Audio/Plug-Ins/VST3/Docs.vst3", {"CFBundleIdentifier": "com.goodco.Docs", "CFBundleExecutable": "d"}, exe=thin_macho("arm64"))
    # --- один файл AU з кількома плагінами; плагін, вимкнений у Pro Tools; виробник із роком у копірайті
    bundle(root, "Library/Audio/Plug-Ins/Components/Guitar Rig 7.component", {
        "CFBundleIdentifier": "com.native-instruments.GuitarRig7.AU", "CFBundleExecutable": "g",
        "NSHumanReadableCopyright": "Copyright © 2024 Native Instruments GmbH", "AudioComponents": [
            {"name": "Native Instruments: Guitar Rig 7 FX", "manufacturer": "-NI-", "type": "aufx"},
            {"name": "Native Instruments: Guitar Rig 7 MFX", "manufacturer": "-NI-", "type": "aumf"}]}, exe=thin_macho("arm64"))
    bundle(root, "Library/Application Support/Avid/Audio/Plug-Ins (Unused)/Disabled.aaxplugin", {
        "CFBundleIdentifier": "com.goodco.Disabled", "CFBundleExecutable": "d"}, exe=thin_macho("arm64"))
    bundle(root, "Library/Audio/Plug-Ins/VST3/Meter.vst3", {
        "CFBundleExecutable": "m", "NSHumanReadableCopyright": "2.5.15, Copyright Youlean, 2016-2026"}, exe=thin_macho("arm64"))
    bundle(root, "Library/Audio/Plug-Ins/VST3/Melo.vst3", {
        "CFBundleExecutable": "m", "NSHumanReadableCopyright": "Copyright 1999-2024 Celemony Software GmbH, All Rights Reserved."}, exe=thin_macho("arm64"))
    # --- продукти: той самий плагін з виробником у назві файлу; однакова назва в різних виробників
    bundle(root, "Library/Audio/Plug-Ins/VST3/FabFilter Pro-Q 3.vst3", {
        "CFBundleIdentifier": "com.fabfilter.Pro-Q.3.VST3", "CFBundleExecutable": "q", "CFBundleShortVersionString": "3.21",
        "NSHumanReadableCopyright": "© 2023 FabFilter Software Instruments"}, exe=thin_macho("arm64"))
    bundle(root, "Library/Audio/Plug-Ins/VST3/Comp.vst3", {
        "CFBundleExecutable": "c", "NSHumanReadableCopyright": "Copyright 2020 Alpha Audio LLC"}, exe=thin_macho("arm64"))
    bundle(root, "Library/Audio/Plug-Ins/VST/Comp.vst", {
        "CFBundleExecutable": "c", "NSHumanReadableCopyright": "Copyright 2020 Beta Audio LLC"}, exe=thin_macho("arm64"))
    now = datetime.utcnow().replace(microsecond=0)
    w(os.path.join(root, "Library/Receipts/InstallHistory.plist"), plistlib.dumps([
        {"date": now, "displayName": "Replika", "packageIdentifiers": [
            "com.native-instruments.Replika.Documentation", "com.native-instruments.Replika.AAX", "com.native-instruments.Replika.AU"]},
        {"date": now + timedelta(hours=1), "displayName": "Replika", "packageIdentifiers": ["com.native-instruments.Replika.AU"]},
        {"date": now, "displayName": "Auto-Align 2", "packageIdentifiers": ["com.SoundRadix.AutoAlign2"]},
        {"date": now, "displayName": "Чужий", "packageIdentifiers": ["com.otherco.Splitter"]},
        {"date": now, "displayName": "Документація", "packageIdentifiers": ["com.goodco.Docs.Documentation"]},
    ]))
    # --- програма, всередині якої не шукаємо
    bundle(root, "Applications/Logic Pro.app/Contents/PlugIns/Alchemy.component", {"CFBundleExecutable": "a"}, exe=thin_macho("arm64"))


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
