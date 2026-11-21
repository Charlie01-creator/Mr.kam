"""Pre-deploy checks: serves dist/ over local HTTP and fetches every page and every referenced asset.
This is NOT browser testing: it verifies status codes, URL resolution and exposed files only."""
import os,re,sys,threading,http.server,socketserver,functools
from urllib.parse import urljoin,urlparse
from urllib.request import urlopen
from urllib.error import HTTPError
from html.parser import HTMLParser
os.chdir(os.path.dirname(os.path.abspath(__file__)));D="dist";fail=0
def bad(m):
    global fail;fail+=1;print("FAIL",m)
# 1. whitelist of files that may be public
OK_EXT={".html",".css",".js",".svg",".png",".jpg",".jpeg",".webp",".txt",".xml"}
for r,_,fs in os.walk(D):
    for f in fs:
        if f.startswith(".") or os.path.splitext(f)[1] not in OK_EXT:bad("unexpected public file: "+os.path.join(r,f))
# 2. secrets / private data scan
for r,_,fs in os.walk(D):
    for f in fs:
        t=open(os.path.join(r,f),errors="ignore").read()
        for pat,n in((r"(api[_-]?key|secret|token|password)\s*[:=]","credential-like"),(r"sk-[A-Za-z0-9]{10,}","key-like"),(r"[\w.+-]+@[\w-]+\.[\w.]+","email address"),(r"\+?\d[\d ()-]{8,}\d","phone-like number")):
            m=re.search(pat,t,re.I)
            if m and not (n=="email address" and "[^@" in m.group(0)) and not (n=="phone-like number" and len(re.sub(r"\D","",m.group(0)))<9):print("NOTE",n,"in",os.path.join(r,f),"->",m.group(0)[:40])
# 3. local HTTP crawl
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(*a):pass
srv=socketserver.TCPServer(("127.0.0.1",0),functools.partial(Q,directory=D));srv.allow_reuse_address=True
port=srv.server_address[1];threading.Thread(target=srv.serve_forever,daemon=True).start();B=f"http://127.0.0.1:{port}"
class L(HTMLParser):
    def __init__(s):super().__init__();s.u=[]
    def handle_starttag(s,t,a):
        a=dict(a)
        for k in("href","src"):
            if a.get(k):s.u.append(a[k])
def get(u):
    try:
        with urlopen(u) as r:return r.status,r.read().decode("utf-8","ignore")
    except HTTPError as e:return e.code,""
pages=["/"]+["/"+os.path.relpath(os.path.dirname(os.path.join(r,f)),D)+"/" for r,_,fs in os.walk(D) for f in fs if f=="index.html" and r!=D]
checked=set()
for p in pages:
    st,h=get(B+p)
    if st!=200:bad(f"{p} -> {st}");continue
    l=L();l.feed(h)
    for u in l.u:
        if re.match(r"(mailto:|tel:|https?:)",u) or u.startswith("#"):continue
        full=urljoin(B+p,u).split("#")[0]
        if full in checked:continue
        checked.add(full);s2,_=get(full)
        if s2!=200:bad(f"{p}: {u} -> {full} returned {s2}")
for f in("/robots.txt","/llms.txt","/404.html","/assets/og.png","/assets/favicon.svg"):
    if get(B+f)[0]!=200:bad(f+" not served")
# 404 page: every link/asset is root-absolute so it works at any missing URL depth
_,h404=get(B+"/404.html");l=L();l.feed(h404)
for u in l.u:
    if not(u.startswith("/") or u.startswith("#")):bad("404.html has non-root-absolute reference: "+u)
print("pages crawled:",len(pages),"| unique URLs fetched:",len(checked),"| failures:",fail);sys.exit(1 if fail else 0)
