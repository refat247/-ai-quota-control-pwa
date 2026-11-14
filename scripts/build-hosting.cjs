'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'dist');
const allowlist = ['index.html','sw.js','manifest.webmanifest','icon-192.png','icon-512.png'];
if (fs.existsSync(output)) fs.rmSync(output, {recursive:true, force:true});
fs.mkdirSync(output, {recursive:true});
for (const name of allowlist) {
  const src = path.join(root,name); const dst=path.join(output,name);
  if (!fs.existsSync(src)) throw new Error(`Missing asset ${name}`);
  fs.copyFileSync(src,dst);
  const data=fs.readFileSync(src);
  console.log(`${name}: ${data.length} bytes, sha256 ${crypto.createHash('sha256').update(data).digest('hex').slice(0,12)}…`);
}
const actual=fs.readdirSync(output).sort();
if (JSON.stringify(actual)!==JSON.stringify([...allowlist].sort())) throw new Error('Hosting build contains unexpected files');
console.log('PASS: dist contains only 5 public-safe static assets; no private data files');