# Plugius

Локальний каталог музичних плагінів для macOS. Нічого не надсилає в інтернет.

## Запуск
- Веб-версія: `python3 app/pluginvault.py serve` (відкриється http://127.0.0.1:8765).
- Десктопний застосунок: `python3 tools/build_app.py`, потім розпакуйте `dist/Plugius-app.zip`. Перший запуск збирає вікно (до хвилини, потрібні Command Line Tools).
  Якщо macOS блокує: `xattr -dr com.apple.quarantine Plugius.app`.

## Що рахується
AU, VST2, VST3, AAX, CLAP, LV2, RTAS, а також Windows `.dll` / Linux `.so` (за експортованими символами). Режими скану: стандартні теки або весь диск. Штатні Logic Pro та Pro Tools приховані. Автоскан раз на тиждень (Налаштування). Ручні поля не затираються повторними сканами.

## Дані
`~/Library/Application Support/PluginVault/`: база, правила (`stock_rules.json`, `license_rules.json`), лог.

## Приблизні дані
«Звідки скачана» та шляхи ліцензій визначаються евристично, решту вписуйте вручну.

## Тести
`python3 tests/test_all.py`
