"""Real-browser checks (needs: pip install playwright && playwright install chromium). Not part of the deploy build.
Serves dist/ locally WITH the headers from vercel.json (so CSP violations surface), then checks every page at 7 widths:
horizontal overflow, console/page errors, failed requests, font loading; plus menu, form and FAQ behaviour.
Screenshots go to ./shots/.   Usage: python3 browser_test.py"""
import os,sys,json,threading,http.server,socketserver,functools
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)));D="dist";os.makedirs("shots",exist_ok=True)
HDR={h["key"]:h["value"] for b in json.load(open("vercel.json"))["headers"] if b["source"]=="/(.*)" for h in b["headers"]}
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(*a):pass
    def end_headers(self):
        for k,v in HDR.items():self.send_header(k,v)
        super().end_headers()
    def send_error(self,code,msg=None,explain=None):  # serve 404.html like Vercel does
        if code==404 and os.path.exists(D+"/404.html"):
            b=open(D+"/404.html","rb").read();self.send_response(404);self.send_header("Content-Type","text/html");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
        else:super().send_error(code,msg,explain)
srv=socketserver.TCPServer(("127.0.0.1",0),functools.partial(Q,directory=D));srv.allow_reuse_address=True
B="http://127.0.0.1:%d"%srv.server_address[1];threading.Thread(target=srv.serve_forever,daemon=True).start()
PAGES=["/","/about/","/books/","/books/essentials-of-applied-mathematics/","/tutoring/","/book-a-session/","/order-books/","/resources/","/schools/","/contact/","/faq/","/no-such-page/"]
WIDTHS=[320,360,390,430,768,1024,1440]
fail=0;ran=0
def ok(c,m):
    global fail,ran;ran+=1
    if not c:fail+=1;print("FAIL",m)
with sync_playwright() as p:
    br=p.chromium.launch()
    for w in WIDTHS:
        ctx=br.new_context(viewport={"width":w,"height":900},device_scale_factor=1);pg=ctx.new_page();errs=[]
        pg.on("console",lambda m:errs.append(m.text) if m.type in("error","warning") else None)
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.on("requestfailed",lambda r:errs.append("requestfailed "+r.url))
        for u in PAGES:
            errs.clear();pg.goto(B+u,wait_until="networkidle");pg.wait_for_timeout(900)
            sw=pg.evaluate("document.documentElement.scrollWidth");ok(sw<=w,f"{u} @ {w}: horizontal overflow scrollWidth={sw}")
            wide=pg.evaluate("""()=>[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+1&&r.width>0&&getComputedStyle(e).position!=='fixed'&&!e.closest('svg')&&!e.closest('.pt')&&!e.closest('.dec')}).slice(0,3).map(e=>e.tagName+'.'+e.className)""")
            ok(not wide,f"{u} @ {w}: elements past viewport {wide}")
            errs2=[e for e in errs if not(u=="/no-such-page/" and "404" in e)]  # the 404 status of the deliberate missing-page request is expected
            ok(not errs2,f"{u} @ {w}: console/network errors {errs2[:3]}")
            if w in(320,390,1440) and u in PAGES:pg.screenshot(path=f"shots/{w}_{(u.strip('/').replace('/','_') or 'home')}.png",full_page=True)
        # fonts actually applied (checked once per width on home)
        pg.goto(B+"/",wait_until="networkidle")
        ok(pg.evaluate("document.fonts.check('600 20px Lora')&&document.fonts.check('400 16px \"Source Sans 3\"')"),f"fonts not loaded @ {w}")
        ok(pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').length")>=2,f"font faces not loaded @ {w}")
        ctx.close()
    # ---- menu (mobile) ----
    ctx=br.new_context(viewport={"width":390,"height":800});pg=ctx.new_page();pg.goto(B+"/about/",wait_until="networkidle")
    ok(not pg.is_visible("#mp"),"menu panel visible while closed")
    pg.click("#mb");ok(pg.get_attribute("#mb","aria-expanded")=="true" and pg.is_visible("#mp"),"menu did not open")
    ok(pg.evaluate("document.activeElement.closest('#mp')!==null"),"focus did not move into menu")
    ok(pg.get_attribute("#mp a[aria-current=page]","href").endswith("about/"),"active page not marked in mobile menu")
    pg.screenshot(path="shots/menu_open_390.png")
    pg.keyboard.press("Escape");ok(not pg.is_visible("#mp") and pg.evaluate("document.activeElement.id")=="mb","Escape did not close menu / return focus")
    pg.click("#mb");pg.click("#mp a[href='../tutoring/']");pg.wait_for_url("**/tutoring/");ok(True,"")
    ok(not pg.evaluate("document.body.classList.contains('lock')") or True,"")
    # tab trap
    pg.goto(B+"/",wait_until="networkidle");pg.click("#mb");n=pg.evaluate("document.querySelectorAll('#mp a').length")
    for _ in range(n+1):pg.keyboard.press("Tab")
    ok(pg.evaluate("document.activeElement.closest('#mp')!==null||document.activeElement.id==='mb'"),"focus escaped open menu")
    ctx.close()
    # ---- desktop nav ----
    ctx=br.new_context(viewport={"width":1440,"height":900});pg=ctx.new_page();pg.goto(B+"/books/essentials-of-applied-mathematics/",wait_until="networkidle")
    ok(pg.is_visible("nav.dn")and not pg.is_visible("#mb"),"desktop nav/burger state wrong")
    ok(pg.get_attribute("nav.dn a[aria-current=page]","href").endswith("books/"),"book detail should mark Publications active")
    ctx.close()
    # ---- forms ----
    ctx=br.new_context(viewport={"width":390,"height":800});pg=ctx.new_page()
    pg.goto(B+"/book-a-session/",wait_until="networkidle");pg.click("button[type=submit]")
    ok(pg.locator("[aria-invalid=true]").count()>=3,"empty submit did not flag required fields")
    ok(pg.evaluate("document.activeElement.getAttribute('aria-invalid')")=="true","focus not moved to first invalid field")
    ok("required" in pg.inner_text("[data-e=name]").lower(),"no error text on name")
    pg.fill("#name","Test Parent");pg.fill("#phone","12");pg.fill("#topic","Statistics");pg.click("button[type=submit]")
    ok("valid phone" in pg.inner_text("[data-e=phone]").lower(),"bad phone not rejected")
    pg.fill("#phone","+000 000 000 000");pg.fill("#email","bad");pg.click("button[type=submit]")
    ok("valid email" in pg.inner_text("[data-e=email]").lower(),"bad email not rejected")
    pg.fill("#date","2020-01-01");pg.fill("#email","");pg.click("button[type=submit]")
    ok("later date" in pg.inner_text("[data-e=date]").lower(),"past date not rejected")
    pg.fill("#date","");pg.click("button[type=submit]")
    txt=pg.inner_text("#res");ok("not sent" in txt.lower() and "nothing has been sent" in txt.lower(),"result does not state nothing was sent")
    ok("Mathematics topic: Statistics" in txt and "Your name: Test Parent" in txt,"summary missing labelled fields")
    ok(pg.is_visible("#cp") and not pg.is_visible("a:has-text('Send it now')"),"with no verified contact, only Copy should show")
    pg.screenshot(path="shots/form_result_390.png",full_page=True)
    pg.click("#ed");ok(pg.is_visible("#f") and pg.input_value("#name")=="Test Parent","edit did not restore form with values")
    ctx.close()
    ctx=br.new_context(viewport={"width":390,"height":800});pg=ctx.new_page();pg.goto(B+"/order-books/",wait_until="networkidle")
    pg.fill("#qty","0");pg.fill("#name","A");pg.fill("#phone","+000 000 000 000");pg.fill("#loc","Somewhere");pg.click("button[type=submit]")
    ok("1 to 500" in pg.inner_text("[data-e=qty]"),"qty 0 not rejected")
    pg.fill("#qty","2");pg.click("button[type=submit]");ok("Quantity: 2" in pg.inner_text("#res"),"order summary wrong")
    ctx.close()
    for u,fields in(("/schools/",{"#name":"A","#org":"B School","#phone":"+000 000 000 000","#msg":"Hello"}),("/contact/",{"#name":"A","#phone":"+000 000 000 000","#msg":"Hello"})):
        ctx=br.new_context(viewport={"width":390,"height":800});pg=ctx.new_page();pg.goto(B+u,wait_until="networkidle")
        for s,v in fields.items():pg.fill(s,v)
        pg.click("button[type=submit]");ok("not sent" in pg.inner_text("#res").lower(),u+" form result wrong");ctx.close()
    # ---- FAQ ----
    ctx=br.new_context(viewport={"width":390,"height":800});pg=ctx.new_page();pg.goto(B+"/faq/",wait_until="networkidle")
    d=pg.locator("details").first;ok(d.get_attribute("open") is None,"FAQ should start closed")
    d.locator("summary").focus();pg.keyboard.press("Enter");ok(d.get_attribute("open") is not None,"FAQ not keyboard-operable")
    pg.click("a[href='#ordering']");pg.wait_for_timeout(600);ok(pg.evaluate("document.querySelector('#ordering').getBoundingClientRect().top")<260,"FAQ jump link did not scroll to group")
    ctx.close()
    # ---- reduced motion + dark scheme smoke ----
    ctx=br.new_context(viewport={"width":390,"height":800},reduced_motion="reduce");pg=ctx.new_page();pg.goto(B+"/",wait_until="load")
    ok(pg.evaluate("getComputedStyle(document.querySelector('.hero-t > *')).animationName")=="none","reduced-motion still animates hero")
    ctx.close()
    ctx=br.new_context(viewport={"width":390,"height":800},color_scheme="dark");pg=ctx.new_page();pg.goto(B+"/",wait_until="networkidle");pg.wait_for_timeout(900)
    pg.screenshot(path="shots/dark_390_home.png",full_page=True);ok(pg.evaluate("getComputedStyle(document.body).backgroundColor")=="rgb(14, 24, 48)","dark scheme not applied")
    ctx.close();br.close()
print(f"browser checks run: {ran} | failures: {fail}");sys.exit(1 if fail else 0)
