'use strict';
// Builds dist-ocr/ for a SEPARATE, expiring Firebase Preview channel. It never touches dist/ or the production
// 5-file allowlist (scripts/build-hosting.cjs). Pinned engine packages must be installed first:
//   npm install --no-save tesseract.js@6.0.1 tesseract.js-core@6.0.0 @tesseract.js-data/eng@1.0.0
// (or point OCR_MODULES_DIR at a node_modules folder that has them).
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),out=path.join(root,'dist-ocr');
const mods=process.env.OCR_MODULES_DIR?path.resolve(process.env.OCR_MODULES_DIR):path.join(root,'node_modules');
const pins={'tesseract.js':'6.0.1','tesseract.js-core':'6.0.0','@tesseract.js-data/eng':'1.0.0'};
for(const [name,ver] of Object.entries(pins)){
 const p=path.join(mods,name,'package.json');
 if(!fs.existsSync(p))throw new Error(`Missing ${name}@${ver}. Run the npm install --no-save line in this file's header.`);
 const got=JSON.parse(fs.readFileSync(p,'utf8')).version;
 if(got!==ver)throw new Error(`${name} is ${got}, expected exactly ${ver}`);
}
const shell=['sw.js','manifest.webmanifest','icon-192.png','icon-512.png'];
const engine=[
 ['tesseract.js/dist/tesseract.min.js','ocr/tesseract.min.js'],
 ['tesseract.js/dist/worker.min.js','ocr/worker.min.js'],
 ['tesseract.js-core/tesseract-core-simd-lstm.wasm.js','ocr/core/tesseract-core-simd-lstm.wasm.js'],
 ['tesseract.js-core/tesseract-core-lstm.wasm.js','ocr/core/tesseract-core-lstm.wasm.js'],
 ['@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz','ocr/lang/eng.traineddata.gz'],
 ['tesseract.js/LICENSE.md','ocr/LICENSES/tesseract.js-LICENSE.md','optional'],
 ['tesseract.js-core/LICENSE','ocr/LICENSES/tesseract.js-core-LICENSE','optional'],
 ['@tesseract.js-data/eng/README.md','ocr/LICENSES/tesseract.js-data-eng-README.md','optional']
];
if(fs.existsSync(out))fs.rmSync(out,{recursive:true,force:true});
fs.mkdirSync(out,{recursive:true});
const put=(dst,buf)=>{const f=path.join(out,dst);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,buf)};
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest=[];
let html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const once=(a,b)=>{if(html.split(a).length!==2)throw new Error('Expected exactly one: '+a.slice(0,40));html=html.replace(a,()=>b)};
const csp="default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' data: blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'none'";
once('<meta charset="utf-8"/>','<meta charset="utf-8"/><meta http-equiv="Content-Security-Policy" content="'+csp+'"/>');
once('/*USAGE-PARSER-END*/','/*USAGE-PARSER-END*/\nwindow.__quotaUsageParser={parseUsageText};');
once('<title>AI Quota Control · Mobile PWA v3.3.1</title>','<title>OCR PREVIEW · AI Quota Control</title>');
once('</body>','<script src="ocr/ocr-ui.js"></script></body>');
put('index.html',Buffer.from(html));
for(const n of shell)put(n,fs.readFileSync(path.join(root,n)));
put('ocr/ocr-ui.js',fs.readFileSync(path.join(root,'ocr-preview','ocr-ui.js')));
for(const [src,dst,opt] of engine){
 const f=path.join(mods,src);
 if(!fs.existsSync(f)){if(opt)continue;throw new Error('Missing engine file '+src)}
 put(dst,fs.readFileSync(f));
}
const files=[];(function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);e.isDirectory()?walk(p):files.push(p)}})(out);
for(const f of files.sort()){const b=fs.readFileSync(f);manifest.push({file:path.relative(out,f).split(path.sep).join('/'),bytes:b.length,sha256:sha(b)})}
fs.writeFileSync(path.join(out,'OCR-MANIFEST.json'),JSON.stringify({purpose:'OCR Preview test build; not production',engine:pins,files:manifest},null,1));
const bad=files.filter(f=>/private|backup|\.json$/i.test(path.basename(f))&&!/manifest\.webmanifest$/.test(f)&&!/OCR-MANIFEST\.json$/.test(f));
if(bad.length)throw new Error('Unexpected data-like file: '+bad.join(','));
console.log(manifest.map(m=>`${m.file}: ${m.bytes} bytes sha256 ${m.sha256.slice(0,12)}…`).join('\n'));
console.log(`PASS: dist-ocr built (${manifest.length+1} files, ${(manifest.reduce((a,m)=>a+m.bytes,0)/1048576).toFixed(1)} MB). Production dist/ untouched.`);
