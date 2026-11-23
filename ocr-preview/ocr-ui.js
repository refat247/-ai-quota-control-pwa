/* OCR PREVIEW ONLY. Not part of the production 5-file Hosting allowlist.
   Reads a screenshot ON THIS DEVICE with self-hosted Tesseract.js, using several OCR passes and a vote,
   because a single pass can silently misread digits (seen on real screenshots: "5%" read as "59%").
   Only values that a clear majority of passes agree on are kept. They are written as clean text into the
   existing "Paste usage text" box; the app's own preview, a "compared with my screen" tick and an explicit
   Confirm still decide what is saved. Same-origin GETs only; the image is never uploaded, stored or cached. */
(function(){
'use strict';
var BASE=new URL('ocr/',document.baseURI).href,busy=false;
// A pass is [page-segmentation mode, scale slot, crop away left 30% (sidebar, landscape only), black/white threshold 0..1 or 0 for plain grayscale]
function makePasses(landscape){
 var p=[],m,sc;
 for(sc=0;sc<2;sc++)for(m=0;m<3;m++)p.push([[3,6,11][m],sc,0,0]);
 if(landscape){for(sc=0;sc<2;sc++)for(m=0;m<3;m++)p.push([[3,6,11][m],sc,1,0]);[6,11].forEach(function(x){p.push([x,0,0,0.6]);p.push([x,0,1,0.6])})}
 else{[0.6,0.75].forEach(function(t){[6,11].forEach(function(x){p.push([x,0,0,t])})})}
 return p;
}
function loadScript(src){return new Promise(function(ok,fail){var s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=function(){fail(new Error('OCR engine files could not be loaded.'))};document.head.appendChild(s)})}
function say(el,t){if(el)el.textContent=t}
function nowBD(){return new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Dhaka',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date()).replace(',','')}
async function variant(bitmap,scale,crop,thr){
 var sx=crop?Math.round(bitmap.width*0.3):0,sw=bitmap.width-sx;
 var c=document.createElement('canvas');c.width=Math.max(1,Math.round(sw*scale));c.height=Math.max(1,Math.round(bitmap.height*scale));
 var g=c.getContext('2d');g.filter='grayscale(1)';g.drawImage(bitmap,sx,0,sw,bitmap.height,0,0,c.width,c.height);
 if(thr){var im=g.getImageData(0,0,c.width,c.height),d=im.data,h=new Array(256).fill(0),n=d.length/4,i,y;
  for(i=0;i<d.length;i+=4){y=Math.round(0.299*d[i]+0.587*d[i+1]+0.114*d[i+2]);d[i]=y;h[y]++}
  var lo=0,hi=255,a=0;for(i=0;i<256;i++){a+=h[i];if(a>=n*0.02){lo=i;break}}a=0;for(i=255;i>=0;i--){a+=h[i];if(a>=n*0.02){hi=i;break}}
  var T=lo+(hi-lo)*thr;for(i=0;i<d.length;i+=4){y=d[i]>T?255:0;d[i]=d[i+1]=d[i+2]=y;d[i+3]=255}g.putImageData(im,0,0)}
 var blob=await new Promise(function(r){c.toBlob(r,'image/png')});c.width=c.height=1;return blob;
}
var STOP={weekly:1,limit:1,hour:1,hours:1,session:1,current:1,week:1,usage:1,this:1,left:1,used:1,reset:1,resets:1,total:1,your:1,limits:1};
function labelKey(label){return String(label||'').toLowerCase().split(/[^a-z0-9]+/).filter(function(w){return w.length>=4&&!STOP[w]}).join('-')}
function vote(results){
 var tally={},labels={},lcount={},rtally={},avt={};
 results.forEach(function(res){if(res.avail!==null&&res.avail!==undefined)avt[res.avail]=(avt[res.avail]||0)+1;var rows=res.rows;var rs={};res.resets.forEach(function(x){var key=x.kind+'|'+x.expires;if(rs[key])return;rs[key]=1;rtally[key]=rtally[key]||{n:0,x:x};rtally[key].n++});var seen={};rows.forEach(function(r){var k=r.window+'|'+r.hint+'|'+labelKey(r.label);if(seen[k])return;seen[k]=1;
  tally[k]=tally[k]||{};tally[k][r.used]=(tally[k][r.used]||0)+1;labels[k]=labels[k]||r;lcount[k]=lcount[k]||{};lcount[k][r.label]=(lcount[k][r.label]||0)+1;
  var rv=r.reset||(/^[A-Za-z0-9 :.,'\u2019()\/\u2013-]{1,60}$/.test(r.resetText||'')?'t|'+r.resetText:null);
  if(rv){var rk=k+'|r';tally[rk]=tally[rk]||{};tally[rk][rv]=(tally[rk][rv]||0)+1}})});
 var kept=[],unsure=[];
 Object.keys(tally).filter(function(k){return k.slice(-2)!=='|r'}).forEach(function(k){
  var best=null,bc=0,second=0;
  Object.keys(tally[k]).forEach(function(v){var c=tally[k][v];if(c>bc){second=bc;bc=c;best=v}else if(c>second)second=c});
  var l=labels[k];
  if(bc>=3&&bc>second){
   var reset=null,rt=tally[k+'|r']||{},rb=0;Object.keys(rt).forEach(function(v){if(rt[v]>rb&&rt[v]>=2){rb=rt[v];reset=v}});
   if(reset&&/^\d{4}-\d{2}-\d{2}$/.test(reset)){Object.keys(rt).forEach(function(v){if(v.indexOf(reset+' ')===0&&rt[v]>=2)reset=v})}
   var lb=l.label,lbc=0;Object.keys(lcount[k]).forEach(function(x){if(lcount[k][x]>lbc){lbc=lcount[k][x];lb=x}});
   kept.push({window:l.window,hint:l.hint,label:lb,used:Number(best),reset:reset});
  }else unsure.push(l.label||(l.window==='5h'?'5-hour':'weekly'));
 });
 var rkept=Object.keys(rtally).filter(function(k){return rtally[k].n>=3}).map(function(k){return rtally[k].x}).sort(function(a,b){return a.expires<b.expires?-1:1});
 var av=null,ac=0;Object.keys(avt).forEach(function(k){if(avt[k]>ac){ac=avt[k];av=Number(k)}});
 var runsure=(av!==null&&rkept.length<av)?av-rkept.length:0;
 return {kept:kept,unsure:unsure,resets:rkept,resetUnsure:runsure};
}
function canonical(kept,provider,resets){
 var out=[{claude:'Claude usage',codex:'Codex rate limits',gemini:'Gemini usage',antigravity:'Antigravity usage',grok:'Grok usage'}[provider]||'Usage'];
 kept.forEach(function(r){
  out.push(r.label||(r.window==='5h'?'Current session':'Current week'));
  out.push(r.used+'% used');
  if(r.reset)out.push('Resets '+(r.reset.indexOf('t|')===0?r.reset.slice(2):r.reset));
 });
 if(resets&&resets.length){out.push('Usage limit resets','Available '+resets.length);resets.forEach(function(x){out.push(x.kind==='Full reset'?'Full reset':'Full reset ('+x.kind+')','Expires '+x.expires+' GMT+6')})}
 return out.join('\n');
}
async function scan(file,statusEl,fileInput){
 if(busy)return;busy=true;var worker=null,bitmap=null;
 try{
  if(!file||!/^image\//.test(file.type))throw new Error('Choose an image (screenshot).');
  if(file.size>15*1024*1024)throw new Error('Image is larger than 15 MB.');
  var P=window.__quotaUsageParser;if(!P)throw new Error('Parser not available in this build.');
  say(statusEl,'Loading OCR engine…');
  if(!window.Tesseract)await loadScript(BASE+'tesseract.min.js');
  worker=await window.Tesseract.createWorker('eng',1,{workerPath:BASE+'worker.min.js',corePath:BASE+'core/',langPath:BASE+'lang/',gzip:true,workerBlobURL:false,cacheMethod:'none'});
  bitmap=await createImageBitmap(file);
  var side=Math.max(bitmap.width,bitmap.height),scales=[1,side<=1400?2:0.75],results=[],providers={},PASSES=makePasses(bitmap.width>=bitmap.height*1.2);
  for(var i=0;i<PASSES.length;i++){
   say(statusEl,'Reading screenshot… pass '+(i+1)+' of '+PASSES.length);
   await worker.setParameters({tessedit_pageseg_mode:String(PASSES[i][0]),user_defined_dpi:'300'});
   var blob=await variant(bitmap,scales[PASSES[i][1]],PASSES[i][2],PASSES[i][3]);
   var res=await worker.recognize(blob),text=String((res&&res.data&&res.data.text)||'');
   var parsed=P.parseUsageText(text,nowBD(),null);
   results.push(parsed.ok?{rows:parsed.rows,resets:(parsed.resets&&parsed.resets.items)||[],avail:parsed.resets?parsed.resets.avail:null}:{rows:[],resets:[],avail:null});
   if(parsed.ok&&parsed.detected)providers[parsed.detected]=(providers[parsed.detected]||0)+1;
  }
  var v=vote(results),prov=null,pc=0;Object.keys(providers).forEach(function(k){if(providers[k]>pc){pc=providers[k];prov=k}});
  var area=document.getElementById('usagePaste');if(!area)throw new Error('Paste box not found.');
  if(!v.kept.length&&!v.resets.length)throw new Error('No numbers could be read reliably.');
  area.value=canonical(v.kept,prov,v.resets);area.dataset.ocr='1';
  say(statusEl,'Read '+v.kept.length+' value'+(v.kept.length===1?'':'s')+(v.resets.length?' and '+v.resets.length+' full reset'+(v.resets.length===1?'':'s'):'')+' (majority of '+PASSES.length+' OCR passes)'+(v.unsure.length?'. Left out because passes disagreed: '+v.unsure.join(', ')+'.':'.')+(v.resetUnsure?' Some full-reset lines were left out because passes disagreed.':'')+' Check them against your screen, then tap Preview changes. Nothing is saved yet.');
 }catch(e){say(statusEl,'OCR failed: '+(e&&e.message?e.message:'unknown error')+' Nothing was changed.')}
 finally{
  try{if(bitmap)bitmap.close()}catch(_){}
  try{if(worker)await worker.terminate()}catch(_){}
  try{fileInput.value=''}catch(_){}
  busy=false;
 }
}
function mount(){
 document.querySelectorAll('[data-ocr-slot]').forEach(function(slot){
  if(slot.dataset.ocrReady)return;slot.dataset.ocrReady='1';
  slot.innerHTML='<label class="btn" for="usageOcrFile">Scan screenshot (on-device OCR)</label><input id="usageOcrFile" type="file" accept="image/*" hidden/><p class="help-note" id="usageOcrStatus" role="status">The image stays on this device. It is not uploaded or saved. OCR can misread digits, so you must compare the result with your screen.</p>';
  var input=slot.querySelector('input'),st=slot.querySelector('#usageOcrStatus');
  input.addEventListener('change',function(){if(input.files&&input.files[0])scan(input.files[0],st,input)});
 });
 if(!document.getElementById('ocrPreviewBanner')){
  var b=document.createElement('div');b.id='ocrPreviewBanner';b.setAttribute('role','note');
  b.style.cssText='position:sticky;top:0;z-index:50;background:#fff2da;color:#6b4300;border-bottom:1px solid #ebcb91;font:600 12px/1.4 system-ui,sans-serif;padding:6px 10px;text-align:center';
  b.textContent='OCR PREVIEW build for testing. Do not import private JSON here; this is not the production app.';
  document.body.insertBefore(b,document.body.firstChild);
 }
}
new MutationObserver(mount).observe(document.body,{childList:true,subtree:true});
mount();
})();
