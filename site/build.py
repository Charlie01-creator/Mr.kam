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
def nav(r,cur):
    L=[("","Home"),("about/","About"),("books/","Books"),("tutoring/","Tutoring"),("resources/","Resources"),("schools/","Schools"),("contact/","Contact")]
    return "".join(f'<a href="{r}{h or ""}"{" aria-current=page" if h==cur else ""}>{t}</a>' for h,t in L)
def crumbs(r,items):
    return '<nav class="crumb" aria-label="Breadcrumb"><a href="%s">Home</a>'%(r or "./")+"".join(f' › <a href="{r}{h}">{t}</a>' if h else f' › <span aria-current="page">{t}</span>' for h,t in items)+"</nav>"
def ld(path,items,extra=None):
    g=[{"@type":"WebSite","name":SHORT,"inLanguage":"en"},{"@type":"Person","name":"Kamulegeya Mubarak Kiggundu","jobTitle":"Mathematics educator and textbook author"}]
    if DOMAIN:
        g[0]["url"]=DOMAIN+"/";g[1]["url"]=DOMAIN+"/"
    if items and DOMAIN:
        g.append({"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":DOMAIN+"/"+h} for i,(n,h) in enumerate([("Home","")]+items)]})
    if extra:g.append(extra)
    return json.dumps({"@context":"https://schema.org","@graph":g},ensure_ascii=False)
def page(path,title,desc,body,r="",cur=None,items=None,extra=None,robots=None):
    can=f'<link rel="canonical" href="{DOMAIN}/{path}">\n<meta property="og:url" content="{DOMAIN}/{path}">' if DOMAIN and robots!="noindex" else ""
    og=f'<meta property="og:image" content="{DOMAIN}/assets/og.png">\n<meta name="twitter:card" content="summary_large_image">' if DOMAIN and os.path.exists("assets/og.png") else '<meta name="twitter:card" content="summary">'
    full=title if title.startswith(NAME) else f"{title} | {SHORT}"
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full)}</title><meta name="description" content="{E(desc)}">{('<meta name="robots" content="%s">'%robots) if robots else ""}
{can}
<meta property="og:type" content="website"><meta property="og:site_name" content="{SHORT}"><meta property="og:title" content="{E(full)}"><meta property="og:description" content="{E(desc)}">
{og}
<meta name="theme-color" content="#14213d"><link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{r}assets/site.css">
<script type="application/ld+json">{ld(path,items,extra)}</script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header><div class="bar"><a class="logo" href="{r or './'}">Kamulegeya <span>∑</span> Mathematics</a><nav class="d" aria-label="Main">{nav(r,cur)}</nav>
<a class="btn hd" href="{r}book-a-session/">Book a Session</a><button id="mb" aria-expanded="false" aria-controls="mp" aria-label="Menu">☰</button></div>
<nav id="mp" aria-label="Mobile">{nav(r,cur)}<a href="{r}book-a-session/">Book a Session</a><a href="{r}order-books/">Order a Book</a></nav></header>
<main id="main" tabindex="-1">{body}</main>
<footer><div><p><b>{NAME}</b> — mathematics educator and author.</p><p><a href="{r}book-a-session/">Book a session</a> · <a href="{r}order-books/">Order a book</a> · <a href="{r}schools/">Schools</a> · <a href="{r}contact/">Contact</a> · <a href="{r}faq/">FAQ</a></p></div></footer>
<script src="{r}assets/site.js" defer></script></body></html>'''
def btn(h,t,o=False):return f'<a class="btn{" o" if o else ""}" href="{h}">{t}</a>'
def card(h,p=""):return f'<div class="card"><h2 class="ct">{h}</h2>{p}</div>'
GRID='<svg viewBox="0 0 200 250" aria-hidden="true" focusable="false"><g stroke="currentColor" stroke-width=".4" opacity=".4">'+"".join(f'<path d="M{i*20} 0V250M0 {i*25}H200"/>' for i in range(11))+'</g><path d="M0 200C50 190 80 60 200 40" fill="none" stroke="#e0a030" stroke-width="2"/></svg>'
def bookcard(b,r):
    return f'''<article class="card book"><div class="cover" role="img" aria-label="Cover placeholder for {E(b["title"])}"><span>{b["edition"]}</span><b>{E(b["title"])}</b><span>Kamulegeya M. K.</span></div>
<div><h2 class="ct"><a href="{r}books/{b["slug"]}/">{E(b["title"])}</a></h2><p class="note">{b["edition"]} · Kamulegeya Mubarak Kiggundu</p><p>{E(b["desc"])}</p><p class="note">Topics: {", ".join(b["topics"])}</p>
<div class="row">{btn(r+"order-books/","Order This Book")}{btn(r+"books/"+b["slug"]+"/","Book details",True)}</div></div></article>'''
def fld(n,l,t="text",req=True,opts=None,ex=""):
    if t=="textarea":c=f'<textarea name="{n}" rows="4" id="{n}"></textarea>'
    elif t=="select":c=f'<select name="{n}" id="{n}">'+"".join(f"<option>{E(o)}</option>" for o in opts)+"</select>"
    else:c=f'<input name="{n}" id="{n}" type="{t}" {"required" if req else ""} {ex}>'
    return f'<label for="{n}">{l}{"" if req else " (optional)"}</label>{c}<span class="err" data-e="{n}"></span>'
def form(k,fields,b):
    return f'<form id="f" data-k="{k}" novalidate>{"".join(fields)}<button class="btn" type="submit">{b}</button></form><div id="res" aria-live="polite"></div>'
P={}
r=""
P["index.html"]=page("","%s | Mathematics Educator & Author"%NAME,"Mathematics educator and textbook author. Book tutoring, order Essentials of Applied Mathematics in Statistics and Numerical Methods, or discuss a school partnership.",
f'''<section class="hero"><div><p class="kick">Mathematics educator · Textbook author</p><h1>Mathematics Education. Knowledge That Goes Beyond the Classroom.</h1>
<p class="lead">{NAME} is a mathematics teacher with Head of Department experience and author of <i>Essentials of Applied Mathematics in Statistics and Numerical Methods</i> (2025 Edition).</p>
<div class="row">{btn("book-a-session/","Book a Tutoring Session")}{btn("books/","Explore the Books",True)}</div></div>
<div class="portrait" role="img" aria-label="Portrait placeholder: photograph to be supplied">{GRID}<p>Professional portrait<br>to be added</p></div></section>
<section class="band"><h2>Mathematics educator, author, tutor</h2><div class="grid">{card("Mathematics educator","<p>Teaching and department leadership as named in his 2025 book.</p>")}{card("Textbook author","<p>Published mathematics textbooks, with more titles to be listed as confirmed.</p>")}{card("Tutoring","<p>Private, group and online tutoring requests.</p>")}{card("Educational resources","<p>Verified notes and practice material, published as they become available.</p>")}</div></section>
<h2>Featured book</h2>{bookcard(BOOKS[0],"")}
<h2>Where to next</h2><div class="grid">{card("Students and parents","<p>Request a tutoring session.</p>"+btn("book-a-session/","Book a Session"))}{card("Schools","<p>Enquire about support for a mathematics department.</p>"+btn("schools/","Discuss a School Partnership",True))}</div>''',r="",cur="")
r="../"
P["about/index.html"]=page("about/","About","Biography of Mr. Kamulegeya Mubarak Kiggundu, mathematics educator, Head of Department and author of a 2025 applied mathematics textbook.",
crumbs(r,[("","About")][:0]+[(None,"About")]) if False else crumbs(r,[("about/","About")][:0]+[("","About")]) +f'''<h1>About {NAME}</h1>
<p class="lead">A mathematics educator whose textbook reflects years of classroom teaching and department leadership.</p>
<p>Mr. Kamulegeya is a mathematics teacher who has held Head of Department mathematics roles. His 2025 book names teaching and leadership experience at Buddo Secondary School, Kibuli Secondary School and Lubiri Secondary School, and he is the author of <i>Essentials of Applied Mathematics in Statistics and Numerical Methods</i>.</p>
<h2>Career timeline</h2><div class="tl"><div><b>Mathematics teaching and Head of Department roles</b><br>Buddo S.S, Kibuli S.S and Lubiri S.S, as named in the book. Dates and current affiliation are being confirmed.</div><div><b>2025 · Author</b><br><i>Essentials of Applied Mathematics in Statistics and Numerical Methods</i>, 2025 Edition.</div></div>
<h2>Educational philosophy</h2><div class="empty">Mr. Kamulegeya’s own statement on how he teaches will be published here in his words.</div>
<div class="row">{btn(r+"tutoring/","About tutoring")}{btn(r+"books/","See the books",True)}</div>''',r,"about/",[("About","about/")])
P["books/index.html"]=page("books/","Books & Publications","Mathematics textbooks by Kamulegeya Mubarak Kiggundu, including Essentials of Applied Mathematics in Statistics and Numerical Methods (2025 Edition).",
crumbs(r,[("","Books")])+f'<h1>Books &amp; Publications</h1><p class="lead">Textbooks by {NAME}.</p><div class="shelf">{"".join(bookcard(b,r) for b in BOOKS)}</div><p class="note">Further titles will be added here as each is confirmed.</p>',r,"books/",[("Books","books/")])
r="../../"
for b in BOOKS:
    ex={"@type":"Book","name":b["title"],"author":{"@type":"Person","name":"Kamulegeya Mubarak Kiggundu"},"bookEdition":b["edition"],"description":b["desc"],"inLanguage":"en"}
    P[f"books/{b['slug']}/index.html"]=page(f"books/{b['slug']}/",b["title"],b["desc"]+" "+b["edition"]+" by Kamulegeya Mubarak Kiggundu.",
    crumbs(r,[("books/","Books"),("",b["title"])])+f'<h1>{E(b["title"])}</h1><p class="lead">{b["edition"]} · Kamulegeya Mubarak Kiggundu</p><p>{E(b["desc"])}</p><p class="note">Topics: {", ".join(b["topics"])}. Sample pages will be added where permitted.</p><div class="row">{btn(r+"order-books/","Order This Book")}{btn(r+"books/","All books",True)}</div>',r,"books/",[("Books","books/"),(b["title"],f"books/{b['slug']}/")],ex)
r="../"
P["tutoring/index.html"]=page("tutoring/","Mathematics Tutoring","Request one-on-one, group, exam-preparation or online mathematics tutoring with Mr. Kamulegeya Mubarak Kiggundu.",
crumbs(r,[("","Tutoring")])+f'<h1>Mathematics Tutoring</h1><p class="lead">Tell us what the student needs; Mr. Kamulegeya will confirm what he can offer.</p><div class="grid">{"".join(card(s,"<p class=note>Availability confirmed on enquiry.</p>") for s in ["One-on-one tutoring","Group tutoring","Exam preparation","Online tutoring","Mathematics consultation"])}</div><div class="row">{btn(r+"book-a-session/","Book a Session")}</div>',r,"tutoring/",[("Tutoring","tutoring/")])
P["book-a-session/index.html"]=page("book-a-session/","Book a Tutoring Session","Request a mathematics tutoring session: choose topic, date, time and online or in-person.",
crumbs(r,[("tutoring/","Tutoring"),("","Book a Session")])+'<h1>Book a Session</h1><p class="lead">Send a request. Nothing is booked until Mr. Kamulegeya confirms.</p>'+form("session",[fld("name","Your name"),fld("role","You are a","select",opts=["Student","Parent / guardian"]),fld("phone","Phone","tel",ex='autocomplete="tel"'),fld("email","Email","email",False),fld("topic","Topic or subject"),fld("date","Preferred date","date",False),fld("time","Preferred time","time",False),fld("mode","Mode","select",opts=["Online","In person"]),fld("msg","Additional information","textarea",False)],"Send Request"),r,"tutoring/",[("Tutoring","tutoring/"),("Book a Session","book-a-session/")])
P["order-books/index.html"]=page("order-books/","Order Books","Order Essentials of Applied Mathematics in Statistics and Numerical Methods: choose quantity and pickup or delivery.",
crumbs(r,[("books/","Books"),("","Order Books")])+'<h1>Order Books</h1><p class="lead">Choose a book and quantity. Payment is arranged directly once the order is confirmed; online payment is not set up yet.</p>'+form("order",[fld("book","Book","select",opts=[b["title"] for b in BOOKS]),fld("qty","Quantity","number",ex='min="1" max="500" value="1" inputmode="numeric"'),fld("name","Your name"),fld("phone","Phone","tel",ex='autocomplete="tel"'),fld("email","Email","email",False),fld("delivery","Delivery or pickup","select",opts=["Pickup","Delivery"]),fld("loc","Location"),fld("msg","Message","textarea",False)],"Place Order Request"),r,"books/",[("Books","books/"),("Order Books","order-books/")])
P["resources/index.html"]=page("resources/","Student Resources","Mathematics notes, revision material, practice questions and past papers will be published here once verified.",
crumbs(r,[("","Resources")])+f'<h1>Student Resources</h1><p class="lead">Verified notes, worked examples and practice material will be published here by category.</p><div class="grid">{"".join(card(c,"<p class=note>No items published yet.</p>") for c in ["Mathematics Notes","Revision Materials","Practice Questions","Past Papers","Worked Examples","Statistics","Numerical Methods"])}</div><div class="row">{btn(r+"tutoring/","Ask about tutoring")}</div>',r,"resources/",[("Resources","resources/")])
P["schools/index.html"]=page("schools/","Schools & Institutions","Enquire about mathematics department support, workshops, revision programmes and textbook supply for schools.",
crumbs(r,[("","Schools")])+f'<h1>Schools &amp; Institutions</h1><p class="lead">Send an enquiry; Mr. Kamulegeya will confirm what he can provide.</p><div class="grid">{"".join(card(s) for s in ["Mathematics department support","Educational consultations","Textbook supply","Mathematics workshops","Student revision programmes"])}</div><h2>Discuss a School Partnership</h2>'+form("school",[fld("name","Your name"),fld("org","School or institution"),fld("phone","Phone","tel"),fld("email","Email","email",False),fld("msg","What would you like to discuss?","textarea")],"Send Enquiry"),r,"schools/",[("Schools","schools/")])
P["contact/index.html"]=page("contact/","Contact","Contact Mr. Kamulegeya Mubarak Kiggundu about tutoring, book orders or school partnerships.",
crumbs(r,[("","Contact")])+f'<h1>Contact</h1><p class="lead">The quickest way to reach Mr. Kamulegeya.</p><div id="direct" class="empty">Direct contact details are being verified and will be published here. Use the form below in the meantime.</div><div class="row" style="margin-bottom:24px">{btn(r+"book-a-session/","Book a Session")}{btn(r+"order-books/","Order a Book",True)}</div><h2>Send an enquiry</h2>'+form("enquiry",[fld("name","Your name"),fld("phone","Phone","tel"),fld("email","Email","email",False),fld("msg","Message","textarea")],"Send Enquiry"),r,"contact/",[("Contact","contact/")])
FAQ=[("How do I book tutoring?","Use the Book a Session form. Mr. Kamulegeya confirms the time and format with you."),("Can I pay online?","Not yet. Payment is arranged directly once an order or session is confirmed."),("Is my request sent automatically?","Requests open in WhatsApp or email when a verified contact is configured. Otherwise you can copy the summary and send it yourself."),("How do I order a book?","Use the Order Books form and submit the request."),("Can schools get in touch?","Yes, use the form on the Schools page.")]
fq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
P["faq/index.html"]=page("faq/","Frequently Asked Questions","Answers about booking tutoring, ordering books, payment and school enquiries.",crumbs(r,[("","FAQ")])+"<h1>Frequently Asked Questions</h1>"+"".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in FAQ),r,"faq/",[("FAQ","faq/")],fq)
P["404.html"]=page("404.html","Page not found","This page does not exist. Return to the home page, book a tutoring session or contact Mr. Kamulegeya.",f'<h1>Page not found</h1><p class="lead">That page doesn’t exist.</p><div class="row">{btn("/","Back to Home")}{btn("/contact/","Contact",True)}</div>',"/",robots="noindex")
# ---- write ----
shutil.rmtree("dist",ignore_errors=True);os.makedirs("dist/assets")
for f in ("site.css","site.js","og.png"):shutil.copy("assets/"+f,"dist/assets/"+f)
js=open("dist/assets/site.js").read().replace("__CFG__",json.dumps(CFG));open("dist/assets/site.js","w").write(js)
open("dist/assets/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#14213d"/><text x="32" y="46" font-size="40" text-anchor="middle" fill="#e0a030" font-family="Georgia,serif">∑</text></svg>')
for p,c in P.items():
    os.makedirs(os.path.dirname("dist/"+p) or "dist",exist_ok=True);open("dist/"+p,"w").write(c)
open("dist/robots.txt","w").write("User-agent: *\nAllow: /\n"+(f"Sitemap: {DOMAIN}/sitemap.xml\n" if DOMAIN else ""))
open("dist/llms.txt","w").write(f"# {SHORT}\n\n> Website of {NAME}, mathematics educator and textbook author.\n\n## Pages\n"+"".join(f"- [{k.replace('/index.html','') or 'Home'}]({DOMAIN}/{k.replace('index.html','')})\n" for k in P if k!="404.html")+"\n## Notes\n- Only verified information is published. Contact details and further book titles are added once confirmed.\n")
if DOMAIN:open("dist/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{DOMAIN}/{k.replace('index.html','')}</loc></url>\n" for k in P if k!="404.html")+"</urlset>\n")
print("built",len(P),"pages")
