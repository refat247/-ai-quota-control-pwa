'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const cp=require('node:child_process');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const version=require('../package.json').version;
const index=read('index.html');
const sw=read('sw.js');
const manifest=JSON.parse(read('manifest.webmanifest'));
const readme=read('README.md');
const change=read('CHANGELOG.md');

assert.equal(version,'3.0.0');
assert.ok(readme.includes('**Version:** '+version),'README version drift');
assert.ok(change.includes('## ['+version+']'),'CHANGELOG version drift');
assert.ok(index.includes("VERSION='"+version+"'"),'app version drift');
assert.ok(index.startsWith('<!DOCTYPE html>'));
assert.ok(!index.slice(16,50).includes('<!DOCTYPE html>'),'duplicate DOCTYPE');
assert.ok(index.includes('localStorage'),'browser persistence implementation missing');
assert.ok(index.includes('manifest.webmanifest'),'manifest missing from HTML');
assert.ok(index.includes('serviceWorker.register'),'service worker registration missing');
assert.ok(sw.includes('ai-quota-shell-v3-0-0'));
assert.equal(manifest.display,'standalone');

const expected=['index.html','sw.js','manifest.webmanifest','icon-192.png','icon-512.png','README_BN.txt'];
for(const file of expected)assert.ok(fs.existsSync(path.join(root,file)),file+' missing');
for(const icon of manifest.icons)assert.ok(fs.existsSync(path.join(root,icon.src)),icon.src+' missing');

const safeTextFiles=['index.html','sw.js','manifest.webmanifest','README.md','README_BN.txt','CHANGELOG.md','package.json'];
for(const file of safeTextFiles){
 const content=read(file);
 assert.ok(!/[a-zA-Z0-9._%+-]+@(?:gmail|outlook|yahoo|hotmail)\.com/i.test(content),file+' contains account email');
 assert.ok(!content.includes('khaledlifespring2'),file+' contains owner account');
}
assert.ok(!fs.existsSync(path.join(root,'AI_Quota_PRIVATE_One_Time_Import.json')),'private JSON must not be committed');

cp.execFileSync(process.execPath,['--check',path.join(root,'sw.js')],{stdio:'inherit'});
const script=index.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(script&&script[1].length>1000,'inline app JavaScript missing');
cp.execFileSync(process.execPath,['--check','-'],{input:script[1],stdio:['pipe','inherit','inherit']});
console.log('PASS: versions, privacy, PWA files, JS syntax');
