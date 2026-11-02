import os, sys, tempfile, threading
HERE=os.path.dirname(os.path.abspath(__file__)); APP=os.path.join(os.path.dirname(HERE),"app")
sys.path.insert(0,APP); sys.path.insert(0,HERE)
tmp=tempfile.mkdtemp(prefix="pvui_"); os.environ["PLUGINVAULT_HOME"]=tmp+"/data"
root=tmp+"/disk"; home=root+"/Users/tester"; os.makedirs(home)
import make_tree, pv_core as core
make_tree.build(root,home)
# XSS-перевірка: ім'я з HTML
make_tree.bundle(root,"Library/Audio/Plug-Ins/Components/<img src=x onerror=window.__xss=1>.component",{"CFBundleExecutable":"a","AudioComponents":[{"name":"<b>Evil</b>: <i>x</i>","manufacturer":"zzzz","type":"aufx"}]},exe=make_tree.thin_macho("arm64"))
ctx=core.Ctx(root=root,home=home); core.scan("standard",ctx=ctx); core.scan("full",ctx=ctx)
import pluginvault as pv
from http.server import ThreadingHTTPServer
srv=ThreadingHTTPServer(("127.0.0.1",0),pv.Handler); port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
from playwright.sync_api import sync_playwright
out=os.environ.get("OUT",".")
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1400,"height":850})
    errs=[]; pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None); pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto("http://127.0.0.1:%d/"%port); pg.wait_for_selector("tr.row")
    print("rows:",pg.locator("tr.row").count(), "| stats:",pg.inner_text("#stats"))
    print("xss executed:",pg.evaluate("window.__xss===1"))
    pg.screenshot(path=out+"/ui_main.png")
    pg.check("#fStock"); print("rows with stock:",pg.locator("tr.row").count())
    pg.uncheck("#fStock")
    pg.fill("#q","fab"); print("search fab:",pg.locator("tr.row").count()); pg.fill("#q","")
    pg.click("tr.row >> nth=1"); pg.wait_for_selector("#drawer.open"); pg.fill("#fSource","https://example.com/buy"); pg.click("#dSave"); pg.wait_for_selector(".toast:visible")
    pg.screenshot(path=out+"/ui_drawer.png")
    pg.keyboard.press("Escape")
    pg.click("nav a[data-tab=history]"); pg.wait_for_selector(".scan"); pg.screenshot(path=out+"/ui_history.png")
    pg.click("nav a[data-tab=settings]"); pg.wait_for_selector(".panel"); pg.screenshot(path=out+"/ui_settings.png")
    pg.click("nav a[data-tab=plugins]"); pg.check("#fForeign"); print("foreign only:",pg.locator("tr.row").count())
    pg.emulate_media(color_scheme="dark"); pg.uncheck("#fForeign"); pg.screenshot(path=out+"/ui_dark.png")
    print("console errors:",errs)
    b.close()
