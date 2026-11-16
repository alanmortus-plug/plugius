# Third-party components

Plugius embeds two font families in `app/ui.html` (base64, subset to Latin and Cyrillic). Both are licensed under the SIL Open Font License, Version 1.1, not under the MIT License of this project. The subsets are renamed inside the app ("Plugius Display", "Plugius Mono") and do not use any Reserved Font Name.

| Font | Used as | Copyright | License |
|---|---|---|---|
| Sofia Sans Extra Condensed | "Plugius Display": product names, logo, numbers | Copyright 2019 The Sofia Sans Project Authors (https://github.com/lettersoup/Sofia-Sans) | [SIL OFL 1.1](licenses/OFL-SofiaSans.txt) |
| IBM Plex Mono | "Plugius Mono": formats, sizes, paths | Copyright © 2017 IBM Corp. with Reserved Font Name "Plex" | [SIL OFL 1.1](licenses/OFL-IBMPlex.txt) |

Full license texts, copied verbatim from the font projects:

- [licenses/OFL-SofiaSans.txt](licenses/OFL-SofiaSans.txt), from https://github.com/lettersoup/Sofia-Sans
- [licenses/OFL-IBMPlex.txt](licenses/OFL-IBMPlex.txt), from https://github.com/IBM/plex

## Embedded Python

`Plugius.app` bundles CPython 3.13.18 from [python-build-standalone](https://github.com/astral-sh/python-build-standalone) (release 20261026, `install_only_stripped`, Apple Silicon and Intel merged into one universal build). It is not part of this repository: `tools/fetch_python.py` downloads it at build time and checks its SHA-256.

- CPython is licensed under the Python Software Foundation License; the full text, including the licenses of components CPython itself contains, ships inside the app at `Contents/Resources/python/lib/python3.13/LICENSE.txt`.
- python-build-standalone links further libraries statically into the interpreter (among them OpenSSL under Apache-2.0, SQLite in the public domain, libffi, XZ Utils, bzip2, mpdecimal and Expat under permissive licenses). The list and their licenses are documented at https://gregoryszorc.com/docs/python-build-standalone/main/running.html#licensing.
