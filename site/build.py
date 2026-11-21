#!/usr/bin/env python3
"""Static site generator.  Usage: python3 build.py [https://production-domain]   (or set env SITE_URL)
The domain is optional; canonicals, og:url/og:image, sitemap.xml and absolute JSON-LD URLs are only written when it is given.

WHERE TO EDIT
  1. Verified contact details ........ CFG (below)
  2. Real images ..................... drop files in assets/img/  (names listed in README.md); they are picked up automatically
  3. Publications .................... BOOKS list (optional keys: publisher, isbn, pages, audience, contents)
  4. Downloadable resources .......... RESOURCES list + PDFs in assets/resources/
Design tokens live in assets/site.css (:root)."""
import sys,os,re,json,shutil,html,datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # always operate on this project, never the caller's cwd
DOMAIN=(sys.argv[1] if len(sys.argv)>1 else os.environ.get("SITE_URL","")).strip().rstrip("/")

# ============ 1. VERIFIED CONTACT DETAILS: fill in only after confirming with Mr. Kamulegeya ============
CFG={"phone":"","whatsapp":"","email":""}   # whatsapp = digits only, with country code (e.g. 2567XXXXXXXX)
if CFG["whatsapp"] and not re.fullmatch(r"\d{8,15}",CFG["whatsapp"]):sys.exit("CFG['whatsapp'] must be digits only with country code")
if CFG["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",CFG["email"]):sys.exit("CFG['email'] is not a valid email address")
if CFG["phone"] and not re.fullmatch(r"\+?[0-9 ()-]{7,18}",CFG["phone"]):sys.exit("CFG['phone'] is not a valid phone number")

NAME="Mr. Kamulegeya Mubarak Kiggundu"; PERSON="Kamulegeya Mubarak Kiggundu"; SHORT="Kamulegeya Mathematics"
E=html.escape

# ============ 2. IMAGE ASSETS (auto-detected from assets/img/) ============
IMG_EXT=(".webp",".jpg",".jpeg",".png")
def asset(stem):
    for e in IMG_EXT:
        if os.path.exists(f"assets/img/{stem}{e}"):return stem+e
def asset_all(prefix):
    d="assets/img"
    return sorted(f for f in (os.listdir(d) if os.path.isdir(d) else []) if f.startswith(prefix+"-") and f.lower().endswith(IMG_EXT))
def dims(fn):
    try:
        from PIL import Image
        with Image.open("assets/img/"+fn) as im:return im.size
    except Exception:return None
PORTRAIT=asset("portrait")      # assets/img/portrait.(webp|jpg|png)  -> portrait slot becomes the real photo

# ============ 3. PUBLICATIONS ============
# Only verified facts. Optional keys shown on the detail page when present:
#   "publisher","isbn","pages","audience" (str),"contents" (list of str)
BOOKS=[{"slug":"essentials-of-applied-mathematics","title":"Essentials of Applied Mathematics in Statistics and Numerical Methods","edition":"2025 Edition",
 "desc":"A mathematics textbook covering applied mathematics in statistics and numerical methods.","topics":["Statistics","Numerical Methods"]}]
for _b in BOOKS:
    _b["cover"]=_b.get("cover") or asset("cover-"+_b["slug"])      # assets/img/cover-<slug>.(webp|jpg|png)
    _b["samples"]=asset_all("sample-"+_b["slug"])                    # assets/img/sample-<slug>-1.jpg, -2.jpg ... (only where permitted)

# ============ 4. RESOURCES (leave empty until verified material exists) ============
# {"title":"...","category":"Mathematics Notes","kind":"PDF","file":"name.pdf","desc":"..."}   file lives in assets/resources/
RESOURCES=[]
RES_CATS=["Mathematics Notes","Worked Examples","Practice Exercises","Revision Materials","Past Papers","Statistics","Numerical Methods"]

SERVICES=[("one-on-one","One-on-one tutoring","Individual sessions for a single student.","Individual sessions focused on one student’s mathematics. On the booking form, say which topic you need help with and what kind of support you are looking for."),
("group","Group tutoring","Sessions arranged for more than one student.","Sessions for more than one student. Tell us how many students are involved and which topic you want to cover."),
("exam-preparation","Examination preparation","Preparation and revision ahead of examinations.","Preparation and revision ahead of mathematics examinations. Mention the examination and the topics that need the most attention."),
("online","Online tutoring","Sessions held remotely, where it can be arranged.","Sessions held remotely. Choose “Online” on the booking form and Mr. Kamulegeya will confirm whether it can be arranged."),
("consultation","Mathematics consultation","A conversation about a student’s mathematics needs.","A conversation about a student’s mathematics needs or a learning plan. Use the message field to describe what you would like to discuss.")]
INST=[("Mathematics department support","Enquire about support for a school’s mathematics department."),
("Educational consultations","Discuss a school’s mathematics education needs."),
("Textbook supply","Ask about supplying the textbook to your institution."),
("Mathematics workshops","Enquire about mathematics workshops."),
("Student revision programmes","Enquire about revision programmes for students.")]

# ============ helpers ============
ARW='<span class="ar" aria-hidden="true">→</span>'
def _grid(w,h,s):return "".join(f"M{x} 0V{h}" for x in range(0,w+1,s))+"".join(f"M0 {y}H{w}" for y in range(0,h+1,s))
PG=('<svg class="g" viewBox="0 0 400 500" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
 f'<path d="{_grid(400,500,40)}" fill="none" stroke="currentColor" stroke-opacity=".16"/>'
 '<path d="M200 0V500M0 250H400" fill="none" stroke="currentColor" stroke-opacity=".35" stroke-width="1.2"/>'
 '<path d="M0 390C90 380 150 120 400 70" fill="none" stroke="#B68A48" stroke-width="2.2"/>'
 '<text x="50%" y="58%" text-anchor="middle" font-size="200" fill="none" stroke="currentColor" stroke-opacity=".5" stroke-width="1.5" font-family="Lora,Georgia,serif">∑</text></svg>')
DEC=('<svg class="dec" viewBox="0 0 520 300" preserveAspectRatio="xMaxYMid slice" aria-hidden="true" focusable="false">'
 f'<path d="{_grid(520,300,40)}" fill="none" stroke="currentColor" stroke-opacity=".28"/>'
 '<path d="M0 260C120 250 200 60 520 30" fill="none" stroke="currentColor" stroke-width="2"/></svg>')
def imgtag(r,fn,alt,cls="",eager=False):
    d=dims(fn);wh=f' width="{d[0]}" height="{d[1]}"' if d else ""
    load='fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img class="{cls}" src="{r}assets/img/{fn}" alt="{E(alt)}"{wh} {load} decoding="async">'
def btn(h,t,o=False,ar=False,sm=False):
    c="btn"+(" o" if o else "")+(" sm" if sm else "")
    return f'<a class="{c}" href="{h}">{t}{ARW if ar else ""}</a>'
def W(x):return f'<div class="wrap">{x}</div>'
def crumbs(r,items):
    li=f'<li><a href="{r or "./"}">Home</a></li>'
    for h,t in items:li+=f'<li><a href="{r}{h}">{t}</a></li>' if h else f'<li><span aria-current="page">{t}</span></li>'
    return f'<nav class="crumb" aria-label="Breadcrumb"><ol>{li}</ol></nav>'
def ph(r,items,eyebrow,h1,lead,cls="",inner="",wide=False):
    c="ph"+(" "+cls if cls else "")+(" wide" if wide else "")
    dec="" if cls=="nv" else DEC
    head=f'{crumbs(r,items)}<p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p>'
    body=f'<div class="abt"><div>{head}</div>{inner}</div>' if inner else head
    return f'<div class="{c}">{dec}{W(body)}</div>'
def portrait(r,eager=True):
    if PORTRAIT:
        return f'<figure class="pt"><div class="pf">{imgtag(r,PORTRAIT,"Portrait of "+NAME,"",eager)}</div></figure>'
    return ('<figure class="pt slot" role="img" aria-label="Reserved space for a professional portrait of Mr. Kamulegeya. The photograph has not been supplied yet.">'
            f'<div class="pf">{PG}<div class="cap"><b>Portrait to be supplied</b><span>Reserved for a professional photograph of Mr. Kamulegeya.</span></div></div></figure>')
def cover(r,b):
    if b["cover"]:return f'<div class="cv">{imgtag(r,b["cover"],"Cover of "+b["title"]+", "+b["edition"])}</div>'
    return (f'<div class="cover slot" role="img" aria-label="Cover artwork to be supplied for {E(b["title"])}, {b["edition"]}">'
            f'<span class="t">{b["edition"]}</span><span class="mk" aria-hidden="true">∑</span><span class="l">Cover artwork<br>to be supplied</span></div>')
def meta(b,full=False):
    rows=[("Author",PERSON),("Edition",b["edition"]),("Subjects",", ".join(b["topics"]))]
    if full:
        for k,l in(("publisher","Publisher"),("isbn","ISBN"),("pages","Pages")):
            if b.get(k):rows.append((l,E(str(b[k]))))
    return '<dl class="meta">'+"".join(f"<dt>{k}</dt><dd>{v}</dd>" for k,v in rows)+"</dl>"
def pubfeat(r,b,hl="h3"):
    u=f'{r}books/{b["slug"]}/'
    return (f'<article class="pub">{cover(r,b)}<div><{hl}><a href="{u}">{E(b["title"])}</a></{hl}>{meta(b)}<p>{E(b["desc"])}</p>'
            f'<div class="row">{btn(r+"order-books/","Order this book",ar=True)}{btn(u,"Publication details",o=True)}</div></div></article>')
def fld(n,l,t="text",req=True,opts=None,ex=""):
    if t=="textarea":c=f'<textarea name="{n}" id="{n}" rows="4" aria-describedby="e-{n}"{" required" if req else ""}></textarea>'
    elif t=="select":c=f'<select name="{n}" id="{n}" aria-describedby="e-{n}">'+"".join(f"<option>{E(o)}</option>" for o in opts)+"</select>"
    else:c=f'<input name="{n}" id="{n}" type="{t}" aria-describedby="e-{n}"{" required" if req else ""} {ex}>'
    opt="" if req else '<span class="opt"> (optional)</span>'
    return f'<div class="field"><label for="{n}">{l}{opt}</label>{c}<span class="err" id="e-{n}" data-e="{n}"></span></div>'
def fs(legend,fields,two=False):
    return f'<fieldset class="fs"><legend>{legend}</legend><div class="fgrid{" two" if two else ""}">{"".join(fields)}</div></fieldset>'
def form(k,groups,b,notice):
    return (f'<div class="panel"><p class="notice">{notice}</p><form id="f" data-k="{k}" novalidate>{"".join(groups)}'
            f'<div class="subm"><button class="btn" type="submit">{b}</button><p class="note">All fields are required unless marked optional.</p></div></form><div id="res" aria-live="polite"></div></div>')
def direct():
    rows=[]
    if CFG["phone"]:rows.append(("Phone",f'<a href="tel:{E(re.sub(r"[^0-9+]","",CFG["phone"]))}">{E(CFG["phone"])}</a>'))
    if CFG["whatsapp"]:rows.append(("WhatsApp",f'<a href="https://wa.me/{CFG["whatsapp"]}">Chat on WhatsApp</a>'))
    if CFG["email"]:rows.append(("Email",f'<a href="mailto:{E(CFG["email"])}">{E(CFG["email"])}</a>'))
    if rows:return '<dl class="cdir">'+"".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k,v in rows)+"</dl>"
    return '<div class="empty"><b>Contact details pending</b><p>Mr. Kamulegeya’s direct phone, WhatsApp and email are being verified and will be published here. Until then, use the enquiry form: it prepares a message you can send yourself.</p></div>'

# ============ page shell ============
NAV=[("","Home"),("about/","About"),("books/","Publications"),("tutoring/","Tutoring"),("resources/","Resources"),("schools/","Schools"),("contact/","Contact")]
def person_ld():
    p={"@type":"Person","name":PERSON,"jobTitle":"Mathematics educator and textbook author"}
    if DOMAIN:
        p["@id"]=DOMAIN+"/#person";p["url"]=DOMAIN+"/"
        if PORTRAIT:p["image"]=f"{DOMAIN}/assets/img/{PORTRAIT}"
    return p
def ld(items,extra=None):
    ws={"@type":"WebSite","name":SHORT,"inLanguage":"en"}
    if DOMAIN:ws["url"]=DOMAIN+"/";ws["@id"]=DOMAIN+"/#website"
    g=[ws,person_ld()]
    if items and DOMAIN:
        g.append({"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":DOMAIN+"/"+h} for i,(n,h) in enumerate([("Home","")]+items)]})
    if extra:g.append(extra)
    return json.dumps({"@context":"https://schema.org","@graph":g},ensure_ascii=False).replace("</","<\\/")
def page(path,title,desc,body,r="",cur=None,items=None,extra=None,robots=None):
    can=f'<link rel="canonical" href="{DOMAIN}/{path}">\n<meta property="og:url" content="{DOMAIN}/{path}">' if DOMAIN and robots!="noindex" else ""
    if DOMAIN and os.path.exists("assets/og.png"):
        og=f'<meta property="og:image" content="{DOMAIN}/assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{SHORT}: {NAME}, mathematics educator and textbook author"><meta name="twitter:card" content="summary_large_image">'
    else:og='<meta name="twitter:card" content="summary">'
    full=title if title.startswith(NAME) else f"{title} | {SHORT}"
    links="".join(f'<a href="{r}{h}"{" aria-current=page" if h==cur else ""}>{t}</a>' for h,t in NAV)
    mlinks="".join(f'<a class="l" href="{r}{h}"{" aria-current=page" if h==cur else ""}>{t}{ARW}</a>' for h,t in NAV)
    flinks="".join(f'<li><a href="{r}{h}">{t}</a></li>' for h,t in NAV[1:])
    yr=datetime.date.today().year
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full)}</title><meta name="description" content="{E(desc)}">{('<meta name="robots" content="%s">'%robots) if robots else ""}
{can}
<meta property="og:type" content="website"><meta property="og:locale" content="en"><meta property="og:site_name" content="{SHORT}"><meta property="og:title" content="{E(full)}"><meta property="og:description" content="{E(desc)}">
{og}
<meta name="theme-color" content="#14213d"><meta name="color-scheme" content="light dark"><link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{r}assets/fonts/lora.woff" as="font" type="font/woff" crossorigin><link rel="preload" href="{r}assets/fonts/sourcesans3.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="{r}assets/site.css">
<script type="application/ld+json">{ld(items,extra)}</script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap bar"><a class="logo" href="{r or './'}"><span class="mk" aria-hidden="true">∑</span><span>Kamulegeya<small>Mathematics</small></span></a>
<nav class="dn" aria-label="Main">{links}</nav>
<a class="btn sm hd" href="{r}book-a-session/">Book a session</a>
<button id="mb" type="button" aria-expanded="false" aria-controls="mp" aria-label="Open menu"><span class="bg" aria-hidden="true"><i></i><i></i><i></i></span></button></div>
<nav id="mp" aria-label="Mobile">{mlinks}<div class="mpc">{btn(r+"book-a-session/","Book a session")}{btn(r+"order-books/","Order a book",o=True)}</div></nav></header>
<main id="main" tabindex="-1">{body}</main>
<footer class="ft"><div class="wrap"><div class="ft-g"><div><div class="fl"><span class="mk" aria-hidden="true">∑</span>{SHORT}</div><p>{NAME}: mathematics educator and textbook author.</p></div>
<nav aria-label="Footer"><p class="fh">Explore</p><ul>{flinks}</ul></nav>
<div><p class="fh">Enquire</p><ul><li><a href="{r}book-a-session/">Book a session</a></li><li><a href="{r}order-books/">Order a book</a></li><li><a href="{r}schools/">School enquiries</a></li><li><a href="{r}faq/">FAQ</a></li></ul></div></div>
<div class="fb"><span>© {yr} {PERSON}</span><span>Enquiries are requests, not confirmed bookings or orders.</span></div></div></footer>
<script src="{r}assets/site.js" defer></script></body></html>'''
def closing(r,title="Where would you like to begin?"):
    return (f'<section class="sec nv"><div class="wrap"><div class="ctr"><p class="eyebrow">Next step</p><h2>{title}</h2><p class="lead">Browse the publications, ask about tutoring, or get in touch directly. Nothing is committed until Mr. Kamulegeya confirms it with you.</p></div>'
     f'<div class="paths"><a class="path" href="{r}books/"><b>Explore publications{ARW}</b><span>Textbooks and how to order them.</span></a>'
     f'<a class="path" href="{r}book-a-session/"><b>Request tutoring{ARW}</b><span>Send a session enquiry.</span></a>'
     f'<a class="path" href="{r}contact/"><b>Contact Mr. Kamulegeya{ARW}</b><span>Questions, schools, anything else.</span></a></div></div></section>')

P={}
B0=BOOKS[0]
# ============ HOME ============
r=""
P["index.html"]=page("","%s | Mathematics Educator & Author"%NAME,"Mathematics educator and textbook author. Explore publications, request tutoring, order Essentials of Applied Mathematics, or make a school enquiry.",
f'''<section class="hero"><div class="wrap hero-g"><div class="hero-t"><p class="eyebrow">Mathematics educator · Textbook author</p>
<h1><span class="h1a">Mr. Kamulegeya</span> <span class="h1b">Mubarak Kiggundu</span></h1>
<p class="display">Mathematics education, with knowledge that goes beyond the classroom.</p>
<p class="lead">A mathematics teacher with Head of Department experience, and author of <i>{E(B0["title"])}</i> ({B0["edition"]}).</p>
<div class="row">{btn("books/","Explore publications",ar=True)}{btn("tutoring/","Explore tutoring",o=True)}</div></div>{portrait(r)}</div>
{W('<ul class="facts"><li><b>Mathematics educator</b><span>Classroom teaching and mathematics department leadership.</span></li><li><b>Head of Department</b><span>Mathematics leadership roles, as named in his 2025 book.</span></li><li><b>Published author</b><span>'+B0["edition"]+' of his applied mathematics textbook.</span></li></ul>')}</section>
<section class="sec"><div class="wrap split sticky"><div><p class="eyebrow">Professional introduction</p><h2>Teacher, department head, author.</h2></div>
<div><p class="lead">{NAME} is a mathematics educator who has held Head of Department mathematics roles and has written a textbook on applied mathematics.</p>
<p>His 2025 book names teaching and leadership experience associated with Buddo Secondary School, Kibuli Secondary School and Lubiri Secondary School. These are not presented as current employers, and dates are being confirmed with him.</p>
<p><a class="link" href="about/">Read the full profile{ARW}</a></p></div></div></section>
<section class="sec nv"><div class="wrap"><p class="eyebrow">Publications</p><h2>Featured publication</h2>
{pubfeat("",B0)}{('<div class="minis">'+"".join(f'<a class="mini" href="books/{b["slug"]}/"><span>{E(b["title"])}</span>{ARW}</a>' for b in BOOKS[1:4])+"</div>") if len(BOOKS)>1 else ""}
<p class="note">{"More titles are listed in the " if len(BOOKS)>1 else "Further titles will be added as each is confirmed. See the "}<a href="books/">full catalogue</a>.</p></div></section>
<section class="sec alt"><div class="wrap split sticky"><div><p class="eyebrow">Educational services</p><h2>Tutoring, shaped around the student.</h2><p class="lead">Five ways to enquire. Availability is confirmed with you directly; nothing is promised in advance.</p><div class="row">{btn("tutoring/","All tutoring options",ar=True)}</div></div>
<ol class="svcs">{"".join(f'<li class="svc"><span class="n" aria-hidden="true">0{i+1}</span><div><h3>{t}</h3><p>{s}</p></div><a class="link" href="tutoring/#{sid}">Enquire{ARW}</a></li>' for i,(sid,t,s,_) in enumerate(SERVICES))}</ol></div></section>
<section class="sec"><div class="wrap split sticky"><div><p class="eyebrow">Institutional engagement</p><h2>Support for schools and institutions.</h2><p class="lead">Areas a school or mathematics department can enquire about.</p><p class="note">These are enquiry topics only. Details and availability are confirmed directly.</p><div class="row">{btn("schools/","Make a school enquiry",ar=True)}</div></div>
<ul class="ilist">{"".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t,d in INST)}</ul></div></section>
{closing("")}''',r,"")
# ============ ABOUT ============
r="../"
schools=["Buddo Secondary School","Kibuli Secondary School","Lubiri Secondary School"]
P["about/index.html"]=page("about/","About","Biography of Mr. Kamulegeya Mubarak Kiggundu: mathematics educator, Head of Department experience, and author of a 2025 applied mathematics textbook.",
ph(r,[("","About")],"About","About "+NAME,"A mathematics educator whose textbook reflects classroom teaching and department leadership.",inner=portrait(r))+
f'''<section class="sec"><div class="wrap split sticky"><div><p class="eyebrow">Professional introduction</p><h2>A mathematics educator and author.</h2></div>
<div><p class="lead">{NAME} is a mathematics teacher who has held Head of Department mathematics roles.</p>
<p>He is the author of <i>{E(B0["title"])}</i> ({B0["edition"]}). His 2025 book names teaching and leadership experience associated with Buddo Secondary School, Kibuli Secondary School and Lubiri Secondary School.</p></div></div></section>
<section class="sec alt"><div class="wrap split sticky"><div><p class="eyebrow">Background</p><h2>Teaching and department leadership.</h2><p class="note">Only information from his published book and this website’s supplied material is shown. Dates and current affiliations are being confirmed with him.</p></div>
<ol class="tl"><li><h3>Mathematics teaching</h3><p>Mr. Kamulegeya is a mathematics educator and teacher.</p></li>
<li><h3>Head of Department, mathematics</h3><p>He has held Head of Department mathematics roles. The schools and dates concerned are being confirmed.</p></li>
<li><h3>Schools named in his 2025 book</h3><p>The book associates his teaching and leadership experience with these schools. This website does not state that any of them is a current employer.</p><ul class="tags">{"".join(f"<li>{s}</li>" for s in schools)}</ul></li>
<li><small>2025</small><h3>Author</h3><p><i>{E(B0["title"])}</i>, {B0["edition"]}.</p></li></ol></div></section>
<section class="sec"><div class="wrap"><p class="eyebrow">Author profile</p><h2>Publications</h2>{pubfeat(r,B0)}</div></section>
<section class="sec alt"><div class="wrap split"><div><p class="eyebrow">Educational philosophy</p><h2>In his own words.</h2></div>
<div class="quote-slot"><p class="q">This space is reserved for Mr. Kamulegeya’s own statement on how he teaches.</p><div class="empty"><b>Awaiting his statement</b><p>Nothing has been written on his behalf. His philosophy will be published here once he supplies it.</p></div></div></div></section>
{closing(r)}''',r,"about/",[("About","about/")])
# ============ PUBLICATIONS ============
P["books/index.html"]=page("books/","Publications","Mathematics textbooks by Kamulegeya Mubarak Kiggundu, including Essentials of Applied Mathematics in Statistics and Numerical Methods (2025 Edition).",
ph(r,[("","Publications")],"Catalogue","Publications",f"Textbooks by {NAME}. Each title has its own page with ordering information.","alt")+
f'''<section class="sec"><div class="wrap"><div class="shelf{" multi" if len(BOOKS)>2 else ""}">{"".join(pubfeat(r,b,"h2") for b in BOOKS)}</div>
<p class="note">Further titles will be added to this catalogue as each is confirmed. {"" }<a href="{r}order-books/">Order a book</a> · <a href="{r}faq/#ordering">Ordering FAQ</a></p></div></section>
{closing(r)}''',r,"books/",[("Publications","books/")])
# ============ BOOK DETAIL ============
r="../../"
for b in BOOKS:
    u=f"books/{b['slug']}/"
    ex={"@type":"Book","name":b["title"],"author":({"@id":DOMAIN+"/#person"} if DOMAIN else {"@type":"Person","name":PERSON}),"bookEdition":b["edition"],"description":b["desc"],"inLanguage":"en"}
    if b.get("isbn"):ex["isbn"]=b["isbn"]
    if b.get("publisher"):ex["publisher"]={"@type":"Organization","name":b["publisher"]}
    if DOMAIN:
        ex["url"]=f"{DOMAIN}/{u}"
        if b["cover"]:ex["image"]=f"{DOMAIN}/assets/img/{b['cover']}"
    aud=f'<p>{E(b["audience"])}</p>' if b.get("audience") else '<div class="empty"><b>To be confirmed</b><p>The intended audience will be stated here once it is confirmed with the author.</p></div>'
    con=('<ol>'+"".join(f"<li>{E(c)}</li>" for c in b["contents"])+"</ol>") if b.get("contents") else '<div class="empty"><b>Contents to be supplied</b><p>The table of contents will be listed here when it is provided.</p></div>'
    smp=('<div class="samples">'+"".join(imgtag(r,s,f"Sample page {i+1} from {b['title']}") for i,s in enumerate(b["samples"]))+"</div>") if b["samples"] else '<div class="empty"><b>Not yet supplied</b><p>Sample pages will appear here where the author permits them.</p></div>'
    rel=[x for x in BOOKS if x is not b]
    relh=('<div class="blk"><h2>Related publications</h2><div class="minis">'+"".join(f'<a class="mini" href="{r}books/{x["slug"]}/"><span>{E(x["title"])}</span>{ARW}</a>' for x in rel[:3])+"</div></div>") if rel else ""
    P[u+"index.html"]=page(u,b["title"],b["desc"]+" "+b["edition"]+" by "+PERSON+".",
    ph(r,[("books/","Publications"),("",E(b["title"]))],"Publication",E(b["title"]),f'{b["edition"]} · {PERSON}',wide=True)+
    f'''<section class="sec tight"><div class="wrap bk"><div class="side">{cover(r,b)}</div><div>
<div class="blk"><h2>Publication details</h2>{meta(b,True)}<p>{E(b["desc"])}</p></div>
<div class="blk"><h2>Topics covered</h2><ul class="tags">{"".join(f"<li>{t}</li>" for t in b["topics"])}</ul></div>
<div class="blk"><h2>Intended audience</h2>{aud}</div>
<div class="blk"><h2>Contents</h2>{con}</div>
<div class="blk"><h2>Sample pages</h2>{smp}</div>
<div class="ordbox"><h2>Request this book</h2><p>Orders are requests. Mr. Kamulegeya confirms availability, and payment is arranged directly after confirmation; online payment is not set up.</p><div class="row">{btn(r+"order-books/","Order this book",ar=True)}{btn(r+"books/","All publications",o=True)}</div></div>
{relh}</div></div></section>''',r,"books/",[("Publications","books/"),(b["title"],u)],ex)
# ============ TUTORING ============
r="../"
P["tutoring/index.html"]=page("tutoring/","Mathematics Tutoring","Request one-on-one, group, examination-preparation or online mathematics tutoring, or a consultation, with Mr. Kamulegeya Mubarak Kiggundu.",
ph(r,[("","Tutoring")],"Educational services","Mathematics tutoring","Tell Mr. Kamulegeya what the student needs. He will confirm what he can offer, and when.","nv")+
f'''<section class="sec tight"><div class="wrap">{"".join(f'<div class="tsv" id="{sid}"><span class="bn" aria-hidden="true">0{i+1}</span><div><h2>{t}</h2><p>{l}</p></div><div class="av"><span>Availability is confirmed on enquiry.</span>{btn(r+"book-a-session/","Enquire",o=True,sm=True)}</div></div>' for i,(sid,t,s,l) in enumerate(SERVICES))}</div></section>
<section class="sec alt"><div class="wrap"><p class="eyebrow">How it works</p><h2>From enquiry to session.</h2>
<ol class="steps"><li><b>Send a request</b><p>Complete the booking form with the topic and your preferred time.</p></li><li><b>Send the summary</b><p>The form prepares a summary for you to send; nothing goes out automatically.</p></li><li><b>Wait for confirmation</b><p>Mr. Kamulegeya confirms the topic, time and format. Nothing is booked before that.</p></li></ol>
<div class="row">{btn(r+"book-a-session/","Book a session",ar=True)}{btn(r+"faq/#tutoring","Tutoring FAQ",o=True)}</div></div></section>''',r,"tutoring/",[("Tutoring","tutoring/")])
# ============ BOOK A SESSION ============
nb="Submitting this form is an <strong>enquiry, not a confirmed booking</strong>. A session is booked only when Mr. Kamulegeya confirms it with you."
P["book-a-session/index.html"]=page("book-a-session/","Book a Tutoring Session","Request a mathematics tutoring session: choose a topic, preferred date and time, and online or in-person. Mr. Kamulegeya confirms every request.",
ph(r,[("tutoring/","Tutoring"),("","Book a session")],"Tutoring enquiry","Book a session","Complete this short form. It takes about two minutes on a phone.")+
f'''<section class="sec tight"><div class="wrap fpage">{form("session",[
fs("About you",[fld("name","Your name",ex='autocomplete="name"'),fld("role","You are a","select",opts=["Student","Parent / guardian"]),fld("phone","Phone","tel",ex='autocomplete="tel" inputmode="tel"'),fld("email","Email","email",False,ex='autocomplete="email"')],True),
fs("The session",[fld("topic","Mathematics topic"),fld("mode","Tutoring mode","select",opts=["Online","In person"]),fld("date","Preferred date","date",False),fld("time","Preferred time","time",False)],True),
fs("Anything else",[fld("msg","Additional information","textarea",False)])],"Prepare my request",nb)}
<aside class="aside nv" aria-label="What happens next"><h2>What happens next</h2><ul><li>You review a summary of your request.</li><li>You send it to Mr. Kamulegeya yourself.</li><li>He confirms the topic, time and format with you.</li></ul><p class="note">Fees and schedules are not published on this website. They are discussed when you enquire.</p><div class="row">{btn(r+"tutoring/","See tutoring options",o=True,sm=True)}</div></aside></div></section>''',r,"tutoring/",[("Tutoring","tutoring/"),("Book a Session","book-a-session/")])
# ============ ORDER ============
no="Orders on this page are <strong>requests</strong>. Mr. Kamulegeya confirms availability, and payment is arranged directly after confirmation. Online payment is not set up."
P["order-books/index.html"]=page("order-books/","Order Books","Request a copy of Essentials of Applied Mathematics in Statistics and Numerical Methods: choose quantity and pickup or delivery. Payment is arranged directly.",
ph(r,[("books/","Publications"),("","Order books")],"Book order request","Order books","Choose a title and quantity, then say how you would like to receive it.")+
f'''<section class="sec tight"><div class="wrap fpage">{form("order",[
fs("Your order",[fld("book","Book","select",opts=[b["title"] for b in BOOKS]),fld("qty","Quantity","number",ex='min="1" max="500" value="1" inputmode="numeric"')],True),
fs("Your details",[fld("name","Your name",ex='autocomplete="name"'),fld("phone","Phone","tel",ex='autocomplete="tel" inputmode="tel"'),fld("email","Email","email",False,ex='autocomplete="email"')],True),
fs("Delivery",[fld("delivery","Delivery or pickup","select",opts=["Pickup","Delivery"]),fld("loc","Location",ex='autocomplete="address-level2"'),fld("msg","Message","textarea",False)])],"Prepare my order request",no)}
<aside class="aside nv" aria-label="About ordering"><h2>Before you order</h2><ul><li>This is a request, not a confirmed order.</li><li>Payment is arranged directly once the order is confirmed.</li><li>No online payment is taken on this website.</li></ul><div class="row">{btn(r+"books/"+B0["slug"]+"/","Publication details",o=True,sm=True)}</div></aside></div></section>''',r,"books/",[("Publications","books/"),("Order Books","order-books/")])
# ============ RESOURCES ============
if RESOURCES:
    groups={}
    for x in RESOURCES:groups.setdefault(x["category"],[]).append(x)
    lib="".join(f'<div class="rgroup"><h2>{E(c)}</h2><ul class="rlist">'+"".join(f'<li><div><h3>{E(x["title"])}</h3><p>{E(x.get("desc",""))}</p></div><a class="btn o sm" href="{r}assets/resources/{x["file"]}" download>Download {E(x.get("kind","PDF"))}</a></li>' for x in v)+"</ul></div>" for c,v in groups.items())
else:
    lib=('<div class="empty big"><b>The library is being prepared</b><h2>Resources will be published here once verified.</h2><p>No notes, exercises or downloads are listed yet. Every item will be added only when it is ready and checked.</p>'
         f'<ul class="chips">{"".join(f"<li>{c}</li>" for c in RES_CATS)}</ul></div>')
P["resources/index.html"]=page("resources/","Student Resources","A library of mathematics notes, worked examples, practice exercises and revision material, published here by topic once each item is verified.",
ph(r,[("","Resources")],"Resource library","Student resources","Notes, worked examples and practice material, organised by topic and published only when verified.","alt")+
f'<section class="sec"><div class="wrap">{lib}<div class="row">{btn(r+"tutoring/","Ask about tutoring",ar=True)}{btn(r+"contact/","Suggest a topic",o=True)}</div></div></section>',r,"resources/",[("Resources","resources/")])
# ============ SCHOOLS ============
ns="Submitting this form is an <strong>enquiry only</strong>. Mr. Kamulegeya confirms what he can provide and when."
P["schools/index.html"]=page("schools/","Schools & Institutions","Enquire about mathematics department support, educational consultations, textbook supply, workshops and revision programmes for your school.",
ph(r,[("","Schools")],"Institutional engagement","Schools &amp; institutions","Areas a school or mathematics department can enquire about. Send a short note and Mr. Kamulegeya will respond.","nv")+
f'''<section class="sec"><div class="wrap"><p class="eyebrow">Enquiry topics</p><h2>What you can ask about</h2><ul class="ilist">{"".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t,d in INST)}</ul>
<p class="note">These are topics for enquiry. This website does not claim that any programme has already been delivered.</p></div></section>
<section class="sec alt" id="enquiry"><div class="wrap fpage">{form("school",[fs("Your enquiry",[fld("name","Your name",ex='autocomplete="name"'),fld("org","School or institution",ex='autocomplete="organization"'),fld("phone","Phone","tel",ex='autocomplete="tel" inputmode="tel"'),fld("email","Email","email",False,ex='autocomplete="email"'),fld("msg","What would you like to discuss?","textarea")],True)],"Prepare my enquiry",ns)}
<aside class="aside nv" aria-label="About school enquiries"><h2>Discuss a school partnership</h2><p>Tell us about your school and what you have in mind. The form prepares a message for you to send; nothing is submitted automatically.</p><div class="row">{btn(r+"books/","See the publications",o=True,sm=True)}</div></aside></div></section>''',r,"schools/",[("Schools","schools/")])
# ============ CONTACT ============
nc="This form prepares a message for you to send. Nothing is delivered from this website."
P["contact/index.html"]=page("contact/","Contact","Contact Mr. Kamulegeya Mubarak Kiggundu about tutoring, book orders or school partnerships.",
ph(r,[("","Contact")],"Get in touch","Contact","Reach Mr. Kamulegeya about tutoring, book orders or schools.")+
f'''<section class="sec tight"><div class="wrap fpage"><div><h2>Direct contact</h2>{direct()}<div class="row">{btn(r+"book-a-session/","Book a session")}{btn(r+"order-books/","Order a book",o=True)}</div></div>
<div><h2>Send an enquiry</h2>{form("enquiry",[fs("Your message",[fld("name","Your name",ex='autocomplete="name"'),fld("phone","Phone","tel",ex='autocomplete="tel" inputmode="tel"'),fld("email","Email","email",False,ex='autocomplete="email"'),fld("msg","Message","textarea")])],"Prepare my message",nc)}</div></div></section>''',r,"contact/",[("Contact","contact/")])
# ============ FAQ ============
FAQ=[("tutoring","Tutoring",[("How do I request a tutoring session?","Open the Book a Session page, complete the form and prepare your request. You then send the summary to Mr. Kamulegeya, who confirms the time and format with you."),
("Is a submitted request a confirmed booking?","No. A request is an enquiry. A session is only booked once Mr. Kamulegeya confirms it with you."),
("What kinds of tutoring can I ask about?","The enquiry covers one-on-one tutoring, group tutoring, examination preparation, online tutoring and mathematics consultation. Availability is confirmed on enquiry."),
("Does this website list fees or schedules?","No. Fees, availability and schedules are not published here. They are discussed when you enquire.")]),
("ordering","Ordering books",[("How do I order a book?","Use the Order Books page: choose the title and quantity, add your details, and say whether you prefer pickup or delivery."),
("Is an order request a confirmed order?","No. It is a request. Mr. Kamulegeya confirms availability and arrangements with you."),
("Can I pay online?","Not currently. Online payment is not set up on this website. Payment is arranged directly once your request is confirmed.")]),
("forms","Forms and enquiries",[("Is my request sent automatically?","No. This website has no server that receives forms. When you finish a form you get a summary to send yourself, by WhatsApp or email when a verified contact is set up, or by copying the summary.")]),
("schools","Schools",[("Can schools and institutions enquire?","Yes. Use the form on the Schools page to ask about mathematics department support, consultations, textbook supply, workshops or revision programmes. Details and availability are confirmed directly.")]),
("resources","Resources",[("Where are the notes and practice material?","The resource library is being prepared. Items will be published only once they are verified.")])]
allq=[x for _,_,q in FAQ for x in q]
fq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in allq]}
P["faq/index.html"]=page("faq/","Frequently Asked Questions","Answers about booking tutoring, ordering books, payment, how enquiry forms work and school enquiries.",
ph(r,[("","FAQ")],"Help","Frequently asked questions","Straight answers about tutoring, ordering and how the enquiry forms work.")+
f'''<section class="sec tight"><div class="wrap faqg"><nav class="faqnav" aria-label="FAQ topics"><p>Topics</p><ul>{"".join(f'<li><a href="#{g}">{t}</a></li>' for g,t,_ in FAQ)}</ul></nav>
<div>{"".join(f'<section class="fg" id="{g}"><h2>{t}</h2>'+"".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in qs)+"</section>" for g,t,qs in FAQ)}</div></div></section>''',r,"faq/",[("FAQ","faq/")],fq)
# ============ 404 (root-absolute links so it works at any depth) ============
P["404.html"]=page("404.html","Page not found","This page does not exist. Return to the home page, explore the publications, request tutoring or contact Mr. Kamulegeya.",
'<section class="nf"><div class="wrap"><p class="big" aria-hidden="true">404</p><p class="eyebrow">Page not found</p><h1>That page doesn’t exist.</h1><p class="lead">The link may be old or mistyped. Try one of these instead.</p>'
f'<ul>{"".join(f"""<li><a href="/{h}">{t}{ARW}</a></li>""" for h,t in [("","Home"),("books/","Publications"),("tutoring/","Tutoring"),("book-a-session/","Book a session"),("contact/","Contact")])}</ul></div></section>',"/",robots="noindex")

# ============ write dist ============
shutil.rmtree("dist",ignore_errors=True);os.makedirs("dist/assets")
for f in ("site.css","site.js","og.png"):shutil.copy("assets/"+f,"dist/assets/"+f)
shutil.copytree("assets/fonts","dist/assets/fonts")
for sub,exts in (("img",IMG_EXT),("resources",(".pdf",))):
    if os.path.isdir("assets/"+sub):
        os.makedirs("dist/assets/"+sub,exist_ok=True)
        for f in os.listdir("assets/"+sub):
            if f.lower().endswith(exts):shutil.copy(f"assets/{sub}/{f}",f"dist/assets/{sub}/{f}")
js=open("dist/assets/site.js").read().replace("__CFG__",json.dumps(CFG));open("dist/assets/site.js","w").write(js)
open("dist/assets/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#14213d"/><circle cx="32" cy="32" r="30" fill="none" stroke="#b68a48" stroke-width="2"/><text x="32" y="45" font-size="38" text-anchor="middle" fill="#d9b877" font-family="Georgia,serif">∑</text></svg>')
for p,c in P.items():
    os.makedirs(os.path.dirname("dist/"+p) or "dist",exist_ok=True);open("dist/"+p,"w").write(c)
open("dist/robots.txt","w").write("User-agent: *\nAllow: /\n"+(f"Sitemap: {DOMAIN}/sitemap.xml\n" if DOMAIN else ""))
open("dist/llms.txt","w").write(f"# {SHORT}\n\n> Website of {NAME}, mathematics educator and textbook author.\n\n## Pages\n"+"".join(f"- [{k.replace('/index.html','') or 'Home'}]({DOMAIN}/{k.replace('index.html','')})\n" for k in P if k!="404.html")+"\n## Notes\n- Only verified information is published. Contact details, images and further book titles are added once confirmed.\n- Forms prepare a message for the visitor to send; nothing is submitted automatically. Enquiries are not confirmed bookings or orders.\n")
if DOMAIN:open("dist/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{DOMAIN}/{k.replace('index.html','')}</loc></url>\n" for k in P if k!="404.html")+"</urlset>\n")
print("built",len(P),"pages")
