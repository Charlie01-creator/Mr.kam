/* Kamulegeya Mathematics — minimal JS: mobile menu + enquiry forms. No dependencies. */
(function(){
var CFG={"phone": "", "whatsapp": "", "email": ""};
var $=function(s,c){return(c||document).querySelector(s)};
var esc=function(s){return String(s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})};

/* ---- mobile menu: Escape closes, focus is trapped while open and returned on close ---- */
var mb=$("#mb"),mp=$("#mp");
if(mb&&mp){
 var open=function(o){
  mp.classList.toggle("open",o);document.body.classList.toggle("lock",o);
  mb.setAttribute("aria-expanded",o?"true":"false");mb.setAttribute("aria-label",o?"Close menu":"Open menu");
  if(o){var a=$("a",mp);if(a)a.focus()}
 };
 mb.addEventListener("click",function(){open(!mp.classList.contains("open"))});
 mp.addEventListener("click",function(e){if(e.target.closest("a"))open(false)});
 document.addEventListener("keydown",function(e){
  if(!mp.classList.contains("open"))return;
  if(e.key==="Escape"){open(false);mb.focus();return}
  if(e.key==="Tab"){
   var f=[mb].concat(Array.prototype.slice.call(mp.querySelectorAll("a"))),i=f.indexOf(document.activeElement);
   if(e.shiftKey&&i<=0){e.preventDefault();f[f.length-1].focus()}
   else if(!e.shiftKey&&i===f.length-1){e.preventDefault();f[0].focus()}
  }
 });
 var mq=window.matchMedia("(min-width:1040px)");
 var close=function(e){if(e.matches)open(false)};
 if(mq.addEventListener)mq.addEventListener("change",close);else if(mq.addListener)mq.addListener(close);
}

/* ---- enquiry forms ----
   There is no server. A submitted form only builds a summary; the visitor sends it by WhatsApp or email
   (when a verified contact is set in build.py) or copies it. Nothing here ever claims delivery. */
var f=$("#f");if(!f)return;
var pad=function(n){return n<10?"0"+n:""+n};
var dt=f.querySelector('input[type="date"]');
if(dt){var t0=new Date();dt.min=t0.getFullYear()+"-"+pad(t0.getMonth()+1)+"-"+pad(t0.getDate())}
var errEl=function(n){return f.querySelector('[data-e="'+n+'"]')};
var clear=function(el){var e=errEl(el.name);if(e)e.textContent="";el.removeAttribute("aria-invalid")};
f.addEventListener("input",function(e){if(e.target.name)clear(e.target)});
f.addEventListener("change",function(e){if(e.target.name)clear(e.target)});
var labelOf=function(el){var l=el.id&&f.querySelector('label[for="'+el.id+'"]');return l?l.childNodes[0].textContent.trim():el.name};

f.addEventListener("submit",function(e){
 e.preventDefault();
 var v={},first=null,k=f.dataset.k;
 f.querySelectorAll("[data-e]").forEach(function(s){s.textContent=""});
 f.querySelectorAll("[aria-invalid]").forEach(function(x){x.removeAttribute("aria-invalid")});
 var bad=function(n,m){var el=f.elements[n];errEl(n).textContent=m;el.setAttribute("aria-invalid","true");if(!first)first=el};
 Array.prototype.forEach.call(f.elements,function(el){
  if(!el.name)return;
  v[el.name]=(el.value||"").trim();
  if(el.required&&!v[el.name])bad(el.name,"This field is required.")
 });
 if(v.phone&&!(/^\+?[0-9 ()-]{7,18}$/.test(v.phone)&&v.phone.replace(/\D/g,"").length>=7))bad("phone","Enter a valid phone number (digits, spaces, + or brackets).");
 if(v.email&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v.email))bad("email","Enter a valid email address.");
 if(v.qty!==undefined&&!(+v.qty>=1&&+v.qty<=500&&Math.floor(+v.qty)===+v.qty))bad("qty","Enter a whole number from 1 to 500.");
 if(v.date&&dt&&dt.min&&v.date<dt.min)bad("date","Choose today or a later date.");
 if(first){first.focus();first.scrollIntoView({block:"center"});return}

 var title={session:"Tutoring session request",order:"Book order request",school:"School enquiry",enquiry:"Enquiry"}[k]||"Enquiry";
 var body=title+"\n"+Array.prototype.filter.call(f.elements,function(el){return el.name&&v[el.name]}).map(function(el){return labelOf(el)+": "+v[el.name]}).join("\n");
 var link="",how="Direct sending is not set up on this website yet. Copy the summary below and send it to Mr. Kamulegeya yourself.";
 if(CFG.whatsapp){link="https://wa.me/"+CFG.whatsapp+"?text="+encodeURIComponent(body);how="Use the button to open WhatsApp with this summary ready to send."}
 else if(CFG.email){link="mailto:"+CFG.email+"?subject="+encodeURIComponent(title)+"&body="+encodeURIComponent(body);how="Use the button to open your email app with this summary ready to send."}
 f.hidden=true;
 var res=$("#res");
 res.innerHTML='<div class="rs" role="status" tabindex="-1"><h2>Your request is ready, but not sent</h2><p>'+how+' <strong>Nothing has been sent or booked yet.</strong></p><pre class="sum">'+esc(body)+'</pre><div class="row">'+(link?'<a class="btn" href="'+esc(link)+'" target="_blank" rel="noopener">Send it now</a>':'<button class="btn" id="cp" type="button">Copy summary</button>')+'<button class="btn o" id="ed" type="button">Edit request</button></div><p class="note" id="cpm" aria-live="polite"></p></div>';
 var box=$(".rs",res);box.focus();box.scrollIntoView({block:"start"});
 $("#ed").onclick=function(){res.innerHTML="";f.hidden=false;var a=f.querySelector("input,select,textarea");if(a)a.focus()};
 var cp=$("#cp");
 if(cp)cp.onclick=function(){
  var m=$("#cpm");
  var ok=function(){m.textContent="Summary copied. Paste it into a message to Mr. Kamulegeya."};
  var no=function(){m.textContent="Copying was blocked. Select the text above and copy it manually."};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(body).then(ok,no);else no()
 };
});
})();
