#!/usr/bin/env python3
"""Static site generator. Usage: python3 build.py [https://production-domain]  (or set env SITE_URL)
Domain is optional; canonicals, og:url and sitemap.xml are only written when it is given."""
import sys,os,json,shutil,html
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # always operate on this project, never the caller's cwd
DOMAIN=(sys.argv[1] if len(sys.argv)>1 else os.environ.get("SITE_URL","")).strip().rstrip("/")
# ---- VERIFIED CONTACT DETAILS: fill in only after confirming with Mr. Kamulegeya ----
CFG={"phone":"","whatsapp":"","email":""}   # whatsapp = digits with country code
NAME="Mr. Kamulegeya Mubarak Kiggundu"; SHORT="Kamulegeya Mathematics"
BOOKS=[{"slug":"essentials-of-applied-mathematics","title":"Essentials of Applied Mathematics in Statistics and Numerical Methods","edition":"2025 Edition",
 "desc":"A mathematics textbook covering applied mathematics in statistics and numerical methods.","topics":["Statistics","Numerical Methods"]}]
E=html.escape
NAV=[("","Home"),("about/","About"),("books/","Publications"),("tutoring/","Tutoring"),("resources/","Learning Resources"),("schools/","Schools"),("contact/","Contact")]
SLUG=BOOKS[0]["slug"]
def nav(r,cur):
    return "".join(f'<a href="{r}{h}"{" aria-current=page" if h==cur else ""}>{t}</a>' for h,t in NAV)
def crumbs(r,items):
    return '<nav class="crumb" aria-label="Breadcrumb"><a href="%s">Home</a>'%(r or "./")+"".join(f' <i aria-hidden="true">/</i> <a href="{r}{h}">{t}</a>' if h else f' <i aria-hidden="true">/</i> <span aria-current="page">{t}</span>' for h,t in items)+"</nav>"
def ld(path,items,extra=None):
    g=[{"@type":"WebSite","name":SHORT,"inLanguage":"en"},{"@type":"Person","name":"Kamulegeya Mubarak Kiggundu","jobTitle":"Mathematics educator and textbook author"}]
    if DOMAIN:
        g[0]["url"]=DOMAIN+"/";g[1]["url"]=DOMAIN+"/"
    if items and DOMAIN:
        g.append({"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":DOMAIN+"/"+h} for i,(n,h) in enumerate([("Home","")]+items)]})
    if extra:g.append(extra)
    return json.dumps({"@context":"https://schema.org","@graph":g},ensure_ascii=False)
def foot(r):
    c=[x for x in (CFG["phone"] and f'Phone: <a href="tel:{E(CFG["phone"])}">{E(CFG["phone"])}</a>',CFG["whatsapp"] and f'<a href="https://wa.me/{E(CFG["whatsapp"])}">WhatsApp</a>',CFG["email"] and f'<a href="mailto:{E(CFG["email"])}">{E(CFG["email"])}</a>') if x]
    ct="".join(f"<p>{x}</p>" for x in c) or f'<p>Direct contact details are being verified. Until then, <a href="{r}contact/">send an enquiry</a>.</p>'
    L=lambda items:"".join(f'<li><a href="{r}{h}">{t}</a></li>' for h,t in items)
    return f'''<footer><div class="w fg"><div class="fb"><p class="fl">Kamulegeya Mathematics</p><p>{NAME}: mathematics educator and textbook author.</p>{ct}</div>
<nav aria-label="Publications"><p class="fh">Publications</p><ul>{L([("books/","All publications"),("books/"+SLUG+"/","Applied Mathematics in Statistics and Numerical Methods"),("order-books/","Order a book")])}</ul></nav>
<nav aria-label="Learning"><p class="fh">Learning</p><ul>{L([("tutoring/","Mathematics tutoring"),("book-a-session/","Book a session"),("resources/","Learning resources"),("schools/","Schools and institutions")])}</ul></nav>
<nav aria-label="About"><p class="fh">About</p><ul>{L([("about/","About Mr. Kam"),("faq/","FAQ"),("contact/","Contact")])}</ul></nav></div>
<div class="w fz"><p>© {NAME}</p><p>Payment is arranged directly; online payment is not set up.</p></div></footer>'''
def page(path,title,desc,body,r="",cur=None,items=None,extra=None,robots=None):
    can=f'<link rel="canonical" href="{DOMAIN}/{path}">\n<meta property="og:url" content="{DOMAIN}/{path}">' if DOMAIN and robots!="noindex" else ""
    og=f'<meta property="og:image" content="{DOMAIN}/assets/og.png">\n<meta name="twitter:card" content="summary_large_image">' if DOMAIN and os.path.exists("assets/og.png") else '<meta name="twitter:card" content="summary">'
    full=title if title.startswith(NAME) else f"{title} | {SHORT}"
    full_bleed=body.startswith("<!--full-->")
    body=body if full_bleed else f'<div class="w pg">{body}</div>'
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full)}</title><meta name="description" content="{E(desc)}">{('<meta name="robots" content="%s">'%robots) if robots else ""}
{can}
<meta property="og:type" content="website"><meta property="og:site_name" content="{SHORT}"><meta property="og:title" content="{E(full)}"><meta property="og:description" content="{E(desc)}">
{og}
<meta name="theme-color" content="#12233f"><link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}assets/site.css">
<script type="application/ld+json">{ld(path,items,extra)}</script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header><div class="w bar"><a class="logo" href="{r or './'}"><span class="mono" aria-hidden="true">KM</span><span>Kamulegeya<small>Mathematics, Mr. Kam</small></span></a><nav class="d" aria-label="Main">{nav(r,cur)}</nav>
<a class="btn g hd" href="{r}book-a-session/">Book a Session</a><button id="mb" aria-expanded="false" aria-controls="mp">Menu</button></div>
<nav id="mp" aria-label="Mobile">{nav(r,cur)}<a href="{r}book-a-session/">Book a Session</a><a href="{r}order-books/">Order a Book</a></nav></header>
<main id="main" tabindex="-1">{body}</main>
{foot(r)}
<script src="{r}assets/site.js" defer></script></body></html>'''
def btn(h,t,o=False,g=False):return f'<a class="btn{" o" if o else ""}{" g" if g else ""}" href="{h}">{t}</a>'
def card(h,p=""):return f'<div class="card"><h2 class="ct">{h}</h2>{p}</div>'
def slot(r,name,label,alt,cls="",eager=False):
    for e in("webp","jpg","jpeg","png"):
        if os.path.exists(f"assets/img/{name}.{e}"):
            return f'<img class="ph {cls}" src="{r}assets/img/{name}.{e}" alt="{E(alt)}" {"" if eager else "loading=lazy "}decoding="async">'
    return f'<div class="slot {cls}" role="img" aria-label="{E(label)}"><span>{E(label)}</span></div>'
def cover(r,b,cls=""):return slot(r,"cover-"+b["slug"],"Cover photograph to be supplied","Cover of "+b["title"]+", "+b["edition"],"cv "+cls)
def tile(b,r,h="h3"):
    u=f'{r}books/{b["slug"]}/'
    return f'''<article class="tile" data-tile data-title="{E(b["title"])}" data-topics="{E("|".join(b["topics"]))}"><a class="tc" href="{u}" tabindex="-1" aria-hidden="true">{cover(r,b)}</a>
<{h}><a href="{u}">{E(b["title"])}</a></{h}><p class="note">{b["edition"]}, {E(AUTH)}</p><p class="note">{", ".join(b["topics"])}</p><a class="more" href="{u}">View details</a></article>'''
AUTH="Kamulegeya Mubarak Kiggundu"
def fld(n,l,t="text",req=True,opts=None,ex=""):
    if t=="textarea":c=f'<textarea name="{n}" rows="4" id="{n}"></textarea>'
    elif t=="select":c=f'<select name="{n}" id="{n}">'+"".join(f"<option>{E(o)}</option>" for o in opts)+"</select>"
    else:c=f'<input name="{n}" id="{n}" type="{t}" {"required" if req else ""} {ex}>'
    return f'<label for="{n}">{l}{"" if req else " (optional)"}</label>{c}<span class="err" data-e="{n}"></span>'
def form(k,fields,b):
    return f'<form id="f" data-k="{k}" novalidate>{"".join(fields)}<button class="btn" type="submit">{b}</button></form><div id="res" aria-live="polite"></div>'
P={}
r=""
b0=BOOKS[0]
bu=f"books/{SLUG}/"
SUB=sorted({t for b in BOOKS for t in b["topics"]})
FACTS=[("Teaching","Mathematics teacher"),("Leadership","Head of Department roles"),("Author","2025 Edition textbook"),("Support","Tutoring and school enquiries")]
P["index.html"]=page("","%s | Mathematics Educator & Author"%NAME,"Mathematics educator and textbook author. Explore Essentials of Applied Mathematics in Statistics and Numerical Methods, request tutoring, or enquire for your school.",
f'''<!--full--><section class="hero w"><div class="ht"><h1>Mathematics taught in the classroom, now written for every learner.</h1>
<p class="lead">{NAME} is a mathematics teacher with Head of Department experience and the author of <i>Essentials of Applied Mathematics in Statistics and Numerical Methods</i>, 2025 Edition.</p>
<div class="row">{btn("books/","Explore Publications",g=True)}{btn("about/","Meet Mr. Kam",True)}</div></div>
<div class="ha">{slot(r,"portrait","Professional portrait to be supplied","Portrait of Mr. Kamulegeya Mubarak Kiggundu","pt",True)}
<a class="mini" href="{bu}">{cover(r,b0,"sm")}<span><b>Featured publication</b>{E(b0["title"])}</span></a></div></section>
<section class="facts" aria-label="Professional summary"><dl class="w">{"".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a,b in FACTS)}</dl></section>
<section class="dk show" id="featured"><div class="w sg"><div class="plinth">{cover(r,b0)}</div><div><p class="kick">Featured publication</p><h2>{E(b0["title"])}</h2>
<p class="by">{AUTH}, {b0["edition"]}</p><p>{E(b0["desc"])}</p><p class="kick">Subjects covered</p><ul class="toc">{"".join(f"<li>{t}</li>" for t in b0["topics"])}</ul>
<div class="row">{btn(bu,"View publication details",g=True)}{btn("order-books/","Enquire or order",True)}</div></div></div></section>
<section class="sec w" id="library"><div class="sh"><h2>Publications</h2>{btn("books/","View all publications",True)}</div>
<div class="shelf">{"".join(tile(b,r) for b in BOOKS)}</div><p class="note">Browse by subject: {" · ".join(SUB)}. New titles appear here only once each is confirmed.</p></section>
<section class="sec w auth"><div>{slot(r,"portrait-about","Professional portrait to be supplied","Portrait of Mr. Kamulegeya Mubarak Kiggundu","pt")}</div><div><h2>Meet the author</h2>
<p class="lead">A mathematics educator whose textbook comes out of classroom teaching and department leadership.</p>
<p>Mr. Kamulegeya is a mathematics teacher who has held Head of Department roles. His 2025 book names teaching and leadership experience at Buddo Secondary School, Kibuli Secondary School and Lubiri Secondary School.</p>
<div class="row">{btn("about/","Read the full profile")}</div></div></section>
<section class="sec w" id="learn"><h2>Learning and tutoring</h2><ul class="rows">
<li><h3>Mathematics tutoring</h3><p>One-on-one, group, exam-preparation and online sessions. Availability is confirmed on enquiry.</p>{btn("tutoring/","See tutoring options",True)}</li>
<li><h3>Individual learning support</h3><p>Students and parents can request a session by topic, date and mode.</p>{btn("book-a-session/","Book a session",True)}</li>
<li><h3>Educational resources</h3><p>Notes, worked examples and practice material, published here once verified.</p>{btn("resources/","Browse learning resources",True)}</li>
<li><h3>Schools and institutions</h3><p>Department support, workshops, revision programmes and textbook supply.</p>{btn("schools/","Discuss a school partnership",True)}</li></ul></section>
<section class="sec w trust"><div><h2>Professional background</h2><p class="lead">Only confirmed facts appear here. Further credentials will be added as Mr. Kamulegeya verifies them.</p></div>
<ul class="rows tight"><li><h3>Mathematics teaching</h3><p>Mathematics teacher, with Head of Department roles.</p></li><li><h3>Schools named in his book</h3><p>Buddo S.S, Kibuli S.S and Lubiri S.S.</p></li><li><h3>Publication</h3><p>{E(b0["title"])}, {b0["edition"]}.</p></li></ul></section>
<section class="dk cta"><div class="w"><h2>Start with the book, a session, or a question.</h2><div class="row">{btn("books/","Explore publications",g=True)}{btn("tutoring/","Enquire about tutoring",True)}{btn("contact/","Contact Mr. Kam",True)}</div></div></section>''',r="",cur="")
r="../"
P["about/index.html"]=page("about/","About","Profile of Mr. Kamulegeya Mubarak Kiggundu, mathematics educator, Head of Department and author of a 2025 applied mathematics textbook.",
crumbs(r,[("","About")])+f'''<div class="split"><aside class="stick">{slot(r,"portrait-about","Professional portrait to be supplied","Portrait of Mr. Kamulegeya Mubarak Kiggundu","pt")}</aside><div class="prose"><h1>About {NAME}</h1>
<p class="lead">A mathematics educator whose textbook reflects classroom teaching and department leadership.</p>
<p>Mr. Kamulegeya is a mathematics teacher who has held Head of Department mathematics roles. His 2025 book names teaching and leadership experience at Buddo Secondary School, Kibuli Secondary School and Lubiri Secondary School, and he is the author of <i>{E(b0["title"])}</i>.</p>
<h2>Career</h2><div class="tl"><div><h3>Mathematics teaching and Head of Department roles</h3><p>Buddo S.S, Kibuli S.S and Lubiri S.S, as named in the book. Dates and current affiliation are being confirmed.</p></div><div><h3>2025, Author</h3><p><i>{E(b0["title"])}</i>, {b0["edition"]}.</p></div></div>
<h2>Educational philosophy</h2><div class="empty">Mr. Kamulegeya’s own statement on how he teaches will be published here in his words.</div>
<h2>Publications and activities</h2><p>See <a href="{r}books/">Publications</a> for his textbook, or <a href="{r}tutoring/">Tutoring</a> for the sessions he offers.</p>
<div class="row">{btn(r+"tutoring/","About tutoring")}{btn(r+"books/","See publications",True)}</div></div></div>''',r,"about/",[("About","about/")])
P["books/index.html"]=page("books/","Publications","Mathematics textbooks by Kamulegeya Mubarak Kiggundu, including Essentials of Applied Mathematics in Statistics and Numerical Methods (2025 Edition).",
crumbs(r,[("","Publications")])+f'''<h1>Publications</h1><p class="lead">Textbooks by {NAME}.</p>
{('<div class="tools"><label for="q">Search publications</label><input id="q" type="search" autocomplete="off"><div class="chips" role="group" aria-label="Filter by subject"><button class="chip" data-chip="" aria-pressed="true">All</button>'+"".join(f'<button class="chip" data-chip="{E(t)}" aria-pressed="false">{t}</button>' for t in SUB)+'</div></div>') if len(BOOKS)>1 else f'<p class="note">Subjects: {", ".join(SUB)}. Search and filters switch on automatically once the catalogue has more than one title.</p>'}
<p class="note" id="count" aria-live="polite">{len(BOOKS)} {"publication" if len(BOOKS)==1 else "publications"}</p><div class="shelf">{"".join(tile(b,r,"h2") for b in BOOKS)}</div><p class="note">Further titles will be added here as each is confirmed.</p>''',r,"books/",[("Publications","books/")],
{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"name":b["title"]} for i,b in enumerate(BOOKS)]})
r="../../"
for b in BOOKS:
    ex={"@type":"Book","name":b["title"],"author":{"@type":"Person","name":AUTH},"bookEdition":b["edition"],"description":b["desc"],"inLanguage":"en"}
    P[f"books/{b['slug']}/index.html"]=page(f"books/{b['slug']}/",b["title"],b["desc"]+" "+b["edition"]+" by Kamulegeya Mubarak Kiggundu.",
    crumbs(r,[("books/","Publications"),("",b["title"])])+f'''<div class="split bk"><aside class="stick">{cover(r,b)}</aside><div class="prose"><h1>{E(b["title"])}</h1><p class="lead">{AUTH}, {b["edition"]}</p><p>{E(b["desc"])}</p>
<dl class="spec"><div><dt>Author</dt><dd>{AUTH}</dd></div><div><dt>Edition</dt><dd>{b["edition"]}</dd></div><div><dt>Subjects</dt><dd>{", ".join(b["topics"])}</dd></div></dl>
<h2>Topics covered</h2><ul class="toc">{"".join(f"<li>{t}</li>" for t in b["topics"])}</ul><p class="note">Intended audience, a full contents list and sample pages will be added once confirmed and permitted.</p>
<div class="row">{btn(r+"order-books/","Enquire or order",g=True)}{btn(r+"books/","All publications",True)}</div></div></div>''',r,"books/",[("Publications","books/"),(b["title"],f"books/{b['slug']}/")],ex)
r="../"
P["tutoring/index.html"]=page("tutoring/","Mathematics Tutoring","Request one-on-one, group, exam-preparation or online mathematics tutoring with Mr. Kamulegeya Mubarak Kiggundu.",
crumbs(r,[("","Tutoring")])+f'''<h1>Mathematics Tutoring</h1><p class="lead">Tell us what the student needs; Mr. Kamulegeya will confirm what he can offer.</p>
<ul class="rows">{"".join(f'<li><h2 class="ct">{s}</h2><p class="note">Availability confirmed on enquiry.</p></li>' for s in ["One-on-one tutoring","Group tutoring","Exam preparation","Online tutoring","Mathematics consultation"])}</ul>
<h2>How a request works</h2><ol class="steps"><li>Send a request with the topic and your preferred time.</li><li>Mr. Kamulegeya confirms the time and format with you.</li><li>Nothing is booked until that confirmation.</li></ol>
<div class="row">{btn(r+"book-a-session/","Book a Session",g=True)}</div>''',r,"tutoring/",[("Tutoring","tutoring/")])
P["book-a-session/index.html"]=page("book-a-session/","Book a Tutoring Session","Request a mathematics tutoring session: choose topic, date, time and online or in-person.",
crumbs(r,[("tutoring/","Tutoring"),("","Book a Session")])+'<h1>Book a Session</h1><p class="lead">Send a request. Nothing is booked until Mr. Kamulegeya confirms.</p>'+form("session",[fld("name","Your name"),fld("role","You are a","select",opts=["Student","Parent / guardian"]),fld("phone","Phone","tel",ex='autocomplete="tel"'),fld("email","Email","email",False),fld("topic","Topic or subject"),fld("date","Preferred date","date",False),fld("time","Preferred time","time",False),fld("mode","Mode","select",opts=["Online","In person"]),fld("msg","Additional information","textarea",False)],"Send Request"),r,"tutoring/",[("Tutoring","tutoring/"),("Book a Session","book-a-session/")])
P["order-books/index.html"]=page("order-books/","Order Books","Order Essentials of Applied Mathematics in Statistics and Numerical Methods: choose quantity and pickup or delivery.",
crumbs(r,[("books/","Books"),("","Order Books")])+'<h1>Order Books</h1><p class="lead">Choose a book and quantity. Payment is arranged directly once the order is confirmed; online payment is not set up yet.</p>'+form("order",[fld("book","Book","select",opts=[b["title"] for b in BOOKS]),fld("qty","Quantity","number",ex='min="1" max="500" value="1" inputmode="numeric"'),fld("name","Your name"),fld("phone","Phone","tel",ex='autocomplete="tel"'),fld("email","Email","email",False),fld("delivery","Delivery or pickup","select",opts=["Pickup","Delivery"]),fld("loc","Location"),fld("msg","Message","textarea",False)],"Place Order Request"),r,"books/",[("Books","books/"),("Order Books","order-books/")])
P["resources/index.html"]=page("resources/","Learning Resources","Mathematics notes, revision material, practice questions and past papers will be published here once verified.",
crumbs(r,[("","Learning Resources")])+f'<h1>Learning Resources</h1><p class="lead">Verified notes, worked examples and practice material will be published here by category.</p><ul class="rows cols">{"".join(f"<li><h2 class=ct>{c}</h2><p class=note>No items published yet.</p></li>" for c in ["Mathematics Notes","Revision Materials","Practice Questions","Past Papers","Worked Examples","Statistics","Numerical Methods"])}</ul><div class="row">{btn(r+"books/","See the textbook",True)}{btn(r+"tutoring/","Ask about tutoring")}</div>',r,"resources/",[("Learning Resources","resources/")])
P["schools/index.html"]=page("schools/","Schools & Institutions","Enquire about mathematics department support, workshops, revision programmes and textbook supply for schools.",
crumbs(r,[("","Schools")])+f'<h1>Schools &amp; Institutions</h1><p class="lead">Send an enquiry; Mr. Kamulegeya will confirm what he can provide.</p><div class="split sc"><ul class="rows">{"".join(f"<li><h2 class=ct>{s}</h2></li>" for s in ["Mathematics department support","Educational consultations","Textbook supply","Mathematics workshops","Student revision programmes"])}</ul><div><h2 class="ct">Discuss a School Partnership</h2>'+form("school",[fld("name","Your name"),fld("org","School or institution"),fld("phone","Phone","tel"),fld("email","Email","email",False),fld("msg","What would you like to discuss?","textarea")],"Send Enquiry")+'</div></div>',r,"schools/",[("Schools","schools/")])
P["contact/index.html"]=page("contact/","Contact","Contact Mr. Kamulegeya Mubarak Kiggundu about tutoring, book orders or school partnerships.",
crumbs(r,[("","Contact")])+f'<h1>Contact</h1><p class="lead">The quickest way to reach Mr. Kamulegeya.</p><div id="direct" class="empty">Direct contact details are being verified and will be published here. Use the form below in the meantime.</div><div class="row" style="margin-bottom:24px">{btn(r+"book-a-session/","Book a Session")}{btn(r+"order-books/","Order a Book",True)}</div><h2>Send an enquiry</h2>'+form("enquiry",[fld("name","Your name"),fld("phone","Phone","tel"),fld("email","Email","email",False),fld("msg","Message","textarea")],"Send Enquiry"),r,"contact/",[("Contact","contact/")])
FAQ=[("How do I book tutoring?","Use the Book a Session form. Mr. Kamulegeya confirms the time and format with you."),("Can I pay online?","Not yet. Payment is arranged directly once an order or session is confirmed."),("Is my request sent automatically?","Requests open in WhatsApp or email when a verified contact is configured. Otherwise you can copy the summary and send it yourself."),("How do I order a book?","Use the Order Books form and submit the request."),("Can schools get in touch?","Yes, use the form on the Schools page.")]
fq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
P["faq/index.html"]=page("faq/","Frequently Asked Questions","Answers about booking tutoring, ordering books, payment and school enquiries.",crumbs(r,[("","FAQ")])+"<h1>Frequently Asked Questions</h1>"+"".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in FAQ),r,"faq/",[("FAQ","faq/")],fq)
P["404.html"]=page("404.html","Page not found","This page does not exist. Return to the home page, book a tutoring session or contact Mr. Kamulegeya.",f'<h1>Page not found</h1><p class="lead">That page doesn’t exist.</p><div class="row">{btn("/","Back to Home")}{btn("/books/","Publications",True)}{btn("/contact/","Contact",True)}</div>',"/",robots="noindex")
# ---- write ----
shutil.rmtree("dist",ignore_errors=True);os.makedirs("dist/assets")
for f in ("site.css","site.js","og.png"):shutil.copy("assets/"+f,"dist/assets/"+f)
if os.path.isdir("assets/img"):
    os.makedirs("dist/assets/img",exist_ok=True)
    for f in os.listdir("assets/img"):
        if f.lower().endswith((".webp",".jpg",".jpeg",".png")):shutil.copy("assets/img/"+f,"dist/assets/img/"+f)
js=open("dist/assets/site.js").read().replace("__CFG__",json.dumps(CFG));open("dist/assets/site.js","w").write(js)
open("dist/assets/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#12233f"/><rect x="4" y="4" width="56" height="56" fill="none" stroke="#b08a3e" stroke-width="2"/><text x="32" y="43" font-size="26" font-weight="700" text-anchor="middle" fill="#b08a3e" font-family="Georgia,serif">KM</text></svg>')
for p,c in P.items():
    os.makedirs(os.path.dirname("dist/"+p) or "dist",exist_ok=True);open("dist/"+p,"w").write(c)
open("dist/robots.txt","w").write("User-agent: *\nAllow: /\n"+(f"Sitemap: {DOMAIN}/sitemap.xml\n" if DOMAIN else ""))
open("dist/llms.txt","w").write(f"# {SHORT}\n\n> Website of {NAME}, mathematics educator and textbook author.\n\n## Pages\n"+"".join(f"- [{k.replace('/index.html','') or 'Home'}]({DOMAIN}/{k.replace('index.html','')})\n" for k in P if k!="404.html")+"\n## Notes\n- Only verified information is published. Contact details and further book titles are added once confirmed.\n")
if DOMAIN:open("dist/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{DOMAIN}/{k.replace('index.html','')}</loc></url>\n" for k in P if k!="404.html")+"</urlset>\n")
print("built",len(P),"pages")
