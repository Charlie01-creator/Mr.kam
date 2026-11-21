(function(){var CFG={"phone": "", "whatsapp": "", "email": ""};var $=function(s){return document.querySelector(s)};
var mb=$("#mb"),mp=$("#mp");var tg=function(o){mp.classList.toggle("open",o);mb.setAttribute("aria-expanded",o);mb.textContent=o?"Close":"Menu"};mb.onclick=function(){tg(!mp.classList.contains("open"))};
document.addEventListener("keydown",function(e){if(e.key==="Escape"&&mp.classList.contains("open")){tg(false);mb.focus()}});
var q=$("#q"),chips=document.querySelectorAll("[data-chip]"),tiles=document.querySelectorAll("[data-tile]"),ct=$("#count"),sub="";
var run=function(){var s=(q?q.value:"").toLowerCase(),n=0;tiles.forEach(function(t){var ok=(!sub||t.dataset.topics.split("|").indexOf(sub)>-1)&&(!s||t.dataset.title.toLowerCase().indexOf(s)>-1);t.hidden=!ok;if(ok)n++});if(ct)ct.textContent=n+(n==1?" publication":" publications")};
if(q)q.addEventListener("input",run);chips.forEach(function(c){c.onclick=function(){sub=c.dataset.chip;chips.forEach(function(x){x.setAttribute("aria-pressed",x===c)});run()}});
var esc=function(s){return s.replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})};
var d=$("#direct");if(d){var r=[];if(CFG.phone)r.push('Phone: <a href="tel:'+esc(CFG.phone)+'">'+esc(CFG.phone)+'</a>');if(CFG.whatsapp)r.push('WhatsApp: <a href="https://wa.me/'+esc(CFG.whatsapp)+'">Chat on WhatsApp</a>');if(CFG.email)r.push('Email: <a href="mailto:'+esc(CFG.email)+'">'+esc(CFG.email)+'</a>');if(r.length){d.className="card";d.innerHTML=r.map(function(x){return"<p>"+x+"</p>"}).join("")}}
var f=$("#f");if(!f)return;
f.addEventListener("submit",function(e){e.preventDefault();var v={},bad=0,k=f.dataset.k;
f.querySelectorAll("[data-e]").forEach(function(s){s.textContent=""});
function set(n,m){f.querySelector('[data-e="'+n+'"]').textContent=m;bad++}
Array.prototype.forEach.call(f.elements,function(el){if(el.name){v[el.name]=(el.value||"").trim();if(el.required&&!v[el.name])set(el.name,"Required.")}});
if(v.phone&&!/^\+?[0-9 ()-]{7,18}$/.test(v.phone))set("phone","Enter a valid phone number.");
if(v.email&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v.email))set("email","Enter a valid email address.");
if(v.qty!==undefined&&!(+v.qty>=1&&+v.qty<=500))set("qty","Enter a quantity from 1 to 500.");
if(bad){var x=f.querySelector(".err:not(:empty)");x.scrollIntoView({block:"center"});return}
var t={session:"Tutoring session request",order:"Book order request",school:"School enquiry",enquiry:"Enquiry"}[k];
var body=t+"\n"+Object.keys(v).filter(function(n){return v[n]}).map(function(n){return n+": "+v[n]}).join("\n");
var link="",how="Copy the summary below and send it to Mr. Kamulegeya. Direct sending is not configured yet.";
if(CFG.whatsapp){link="https://wa.me/"+CFG.whatsapp+"?text="+encodeURIComponent(body);how="Send it on WhatsApp to complete your request."}
else if(CFG.email){link="mailto:"+CFG.email+"?subject="+encodeURIComponent(t)+"&body="+encodeURIComponent(body);how="Send it by email to complete your request."}
f.hidden=true;var res=$("#res");
res.innerHTML='<div class="card ok" role="status"><h2 style="margin-top:0">Almost done</h2><p>'+how+' Nothing has been sent or booked yet.</p><pre style="white-space:pre-wrap;font:.9rem system-ui;background:var(--bg);padding:12px;border-radius:6px">'+esc(body)+'</pre><div class="row">'+(link?'<a class="btn" href="'+esc(link)+'" target="_blank" rel="noopener">Send now</a>':'<button class="btn" id="cp" type="button">Copy summary</button>')+'<button class="btn o" id="ed" type="button">Edit request</button></div></div>';
$("#ed").onclick=function(){res.innerHTML="";f.hidden=false};
var cp=$("#cp");if(cp)cp.onclick=function(){(navigator.clipboard?navigator.clipboard.writeText(body):Promise.reject()).then(function(){cp.textContent="Copied"},function(){cp.textContent="Select the text above and copy it"})};
res.scrollIntoView({block:"start"})})})();
