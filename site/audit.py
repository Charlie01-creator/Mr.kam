import os,re,json,sys
from html.parser import HTMLParser
D="dist";fail=0;titles={}
def pages():
    for r,_,fs in os.walk(D):
        for f in fs:
            if f.endswith(".html"):yield os.path.join(r,f)
class H(HTMLParser):
    def __init__(s):super().__init__();s.h1=0;s.links=[];s.t="";s.in_t=0;s.desc="";s.ld="";s.in_ld=0;s.imgs_noalt=0;s.hs=[]
    def handle_starttag(s,t,a):
        a=dict(a)
        if t=="h1":s.h1+=1
        if t in("h1","h2","h3"):s.hs.append(int(t[1]))
        if t=="a" and a.get("href"):s.links.append(a["href"])
        if t=="title":s.in_t=1
        if t=="meta" and a.get("name")=="description":s.desc=a.get("content","")
        if t=="script" and a.get("type")=="application/ld+json":s.in_ld=1
        if t=="img" and not a.get("alt"):s.imgs_noalt+=1
    def handle_endtag(s,t):
        if t=="title":s.in_t=0
        if t=="script":s.in_ld=0
    def handle_data(s,d):
        if s.in_t:s.t+=d
        if s.in_ld:s.ld+=d
def bad(m):
    global fail;fail+=1;print("FAIL",m)
for p in pages():
    s=open(p).read();h=H();h.feed(s)
    if h.h1!=1:bad(f"{p}: h1 count {h.h1}")
    if not h.t or h.t in titles:bad(f"{p}: title missing/duplicate")
    titles[h.t]=p
    if not 50<=len(h.desc)<=170:bad(f"{p}: desc length {len(h.desc)}")
    try:json.loads(h.ld)
    except Exception as e:bad(f"{p}: JSON-LD {e}")
    if h.imgs_noalt:bad(f"{p}: img without alt")
    for a,b in zip(h.hs,h.hs[1:]):
        if b-a>1:bad(f"{p}: heading jump h{a}->h{b}")
    if re.search(r"lorem|localhost|vite|react|TODO|placeholder text",s,re.I):bad(f"{p}: dev/placeholder text")
    for l in h.links:
        if re.match(r"(https?:|mailto:|tel:|#)",l):continue
        t=l.split("#")[0]
        base=D if t.startswith("/") else os.path.dirname(p)
        path=os.path.normpath(os.path.join(base,t.lstrip("/")))
        if os.path.isdir(path):path=os.path.join(path,"index.html")
        if not os.path.exists(path):bad(f"{p}: broken link {l}")
print("pages checked:",len(titles),"| failures:",fail)
print("total dist bytes:",sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(D) for f in fs))
print("source maps:",[f for r,_,fs in os.walk(D) for f in fs if f.endswith(".map")])
