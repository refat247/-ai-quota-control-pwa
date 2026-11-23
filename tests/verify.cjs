'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),cp=require('node:child_process'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,f),'utf8');
const version=require('../package.json').version,html=read('index.html'),sw=read('sw.js'),m=JSON.parse(read('manifest.webmanifest'));
assert.equal(version,'3.3.1');
assert.ok(read('README.md').includes('**Version:** 3.3.1'));
assert.ok(read('CHANGELOG.md').includes('## [3.3.1]'));
assert.ok(html.includes("VERSION='3.3.1'"));
assert.ok(html.startsWith('<!DOCTYPE html>')&&!html.slice(16,50).includes('<!DOCTYPE html>'));
assert.match(html,/sharedGitHubOrigin=location\.origin==='https:\/\/refat247\.github\.io'/);
assert.match(html,/function importDataset\(x\)/);
assert.ok(html.includes('if(sharedGitHubOrigin||recoveryRequired||!validDataset(data))'));
assert.ok(html.includes('function recoveryPage()'));
assert.ok(html.includes('function homeRenderFailure(error)'));
assert.ok(html.includes('view=homeRenderFailure(error)'));
assert.ok(html.includes("HOME_PREF_STORE='ai-quota-ui-preferences-v1'"));
assert.ok(html.includes('function homeMatchingProviders()'));
assert.ok(html.includes('function saveHomePreferences()'));
assert.ok(html.includes('data-home-filter'));
assert.ok(html.includes('data-home-density'));
assert.ok(html.includes('homeQuickChips(rows)'));
assert.ok(html.includes('home-usage-legend'));
assert.ok(html.includes('function homeUsageTone(q)'));
for(const f of ['visualHome','visualQuotas','visualPlans','visualDates','visualMeter','visualDialog'])assert.ok(html.includes('function '+f+'('),f+' missing');
assert.ok(html.includes('id="cockpitDialog"'));
assert.ok(html.includes('data-open-provider'));
assert.ok(html.includes('data-quota-list'));
assert.ok(html.includes('data-date-mode'));
assert.ok(html.includes('if(!commit(next))return;'));

assert.ok(html.includes('function isGrokProvider(provider)'));
assert.match(html,/function validDataset\(x\)/);
assert.match(html,/function exportJSON\(\)/);
assert.ok(html.includes('pasteImport'));
assert.ok(html.includes("q.window==='5h'"));
assert.ok(html.includes('localStorage.getItem(STORE)!==raw'));
assert.ok(html.includes('Save changes</button>'));
assert.ok(html.includes('quotaOnboarding=true'));
assert.ok(html.includes('Step 1 of 2: Create a Plan first'));
assert.ok(html.includes('Step 2 of 2: Choose the new Plan'));
assert.ok(!html.includes('Save + download HTML'));
assert.ok(sw.includes('ai-quota-shell-v3-3-1'));
assert.equal(m.display,'standalone');
for(const f of ['index.html','sw.js','manifest.webmanifest','icon-192.png','icon-512.png'])assert.ok(fs.existsSync(path.join(root,f)));
for(const icon of m.icons)assert.ok(fs.existsSync(path.join(root,icon.src)));
for(const f of ['index.html','sw.js','manifest.webmanifest','README.md','README_BN.txt','CHANGELOG.md']){
 const v=read(f);assert.ok(!/[a-zA-Z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook)\.com/i.test(v),`${f} contains an account email`);
}
assert.ok(!fs.existsSync(path.join(root,'AI_Quota_PRIVATE_One_Time_Import.json')));
cp.execFileSync(process.execPath,['--check',path.join(root,'sw.js')]);
const script=html.match(/<script>\s*(\(\(\)=>\{'use strict';[\s\S]*?)<\/script>/);
assert.ok(script&&script[1].length>1000);
cp.execFileSync(process.execPath,['--check','-'],{input:script[1],stdio:['pipe','pipe','pipe']});
const fb=JSON.parse(read('firebase.json'));
assert.equal(fb.hosting.public,'dist');
const rootRule=fb.hosting.headers.find(r=>r.source==='/');
assert.ok(rootRule?.headers.some(h=>h.key==='Cache-Control'&&h.value==='no-cache'),'Firebase root must revalidate');
console.log('PASS: versions, privacy smoke, valid asset references, JS syntax, Firebase deployment boundary');
// A109 repair source invariants. Chromium covers rendered UX separately.
for(const phrase of ['function rankedQuotas(', 'function compactQuotaCard(', 'data-date-shift', 'id="sheetError"', 'maxHiddenUsed('])assert.ok(html.includes(phrase),'A109 missing '+phrase);
// Paste-usage-text parser. SYNTHETIC samples only: written from public descriptions, NOT real /usage or /status output.
{
 const blk=html.match(/\/\*USAGE-PARSER-START\*\/([\s\S]*?)\/\*USAGE-PARSER-END\*\//);
 assert.ok(blk,'usage parser block missing');
 const {parseUsageText,matchUsageRows,usageConflicts}=new Function(blk[1]+';return {parseUsageText,matchUsageRows,usageConflicts};')();
 const NOW='2026-11-23 23:24';
 // 1. Claude-style, "used" wording, multi-line layout.
 let r=parseUsageText('Current session\n████░░░░ 12% used\nResets 3pm (Asia/Dhaka)\n\nCurrent week (all models)\n██░░ 34% used\nResets Nov 27, 9am (Asia/Dhaka)\n\nCurrent week (Sonnet only)\n 5% used\nResets Nov 27, 9am (Asia/Dhaka)\n',NOW);
 assert.ok(r.ok);assert.equal(r.detected,'claude');assert.equal(r.rows.length,3);
 assert.deepEqual(r.rows.map(x=>[x.window,x.used,x.hint,x.reset]),[['5h',12,'','2026-11-24 15:00'],['weekly',34,'','2026-11-27 09:00'],['weekly',5,'sonnet','2026-11-27 09:00']]);
 // 2. Codex-style: REMAINING must be converted to used; unit-less percent is skipped, never guessed.
 r=parseUsageText('Rate limits:\n  5h limit: [████░░] 96% left (resets 14:30)\n  Weekly limit: [███] 94% remaining (resets 14:30 on 28 Nov)\n  Context window: 100% left\n',NOW);
 assert.ok(r.ok);assert.equal(r.detected,'codex');
 assert.deepEqual(r.rows.map(x=>[x.window,x.used,x.reset]),[['5h',4,'2026-11-24 14:30'],['weekly',6,'2026-11-28 14:30']]);
 r=parseUsageText('Weekly limit: 40%\n5h limit: remaining: 70% (resets in 2h 15m)\n',NOW);
 assert.equal(r.rows.length,1);assert.equal(r.rows[0].used,30);assert.equal(r.rows[0].reset,'2026-11-24 01:39');
 assert.equal(r.skipped.length,1);assert.match(r.skipped[0].reason,/unclear/);
 r=parseUsageText('5h limit: 96% (3h left)',NOW);assert.equal(r.ok,false,'"3h left" must not be read as the percent unit');
 // 3. Missing / foreign-timezone reset: value parsed, reset left unchanged (null).
 r=parseUsageText('Current session\n 12% used\n',NOW);assert.equal(r.rows[0].reset,null);assert.equal(r.rows[0].resetNote,'');
 r=parseUsageText('Current session\n 12% used\nResets 3pm (Europe/London)\n',NOW);assert.equal(r.rows[0].reset,null);assert.match(r.rows[0].resetNote,/timezone/);
 r=parseUsageText('Current session\n 12% used\nResets someday soon\n',NOW);assert.equal(r.rows[0].reset,null);assert.match(r.rows[0].resetNote,/not understood/);
 // 4. Garbage / empty / oversized text: clear error, no rows.
 for(const g of ['','   ','hello world','Battery 50% used','\u0000\u0001{}[]','x'.repeat(20001)]){const q=parseUsageText(g,NOW);assert.equal(q.ok,false,JSON.stringify(g).slice(0,20));assert.ok(q.error);}
 assert.equal(parseUsageText('Current session\n 120% used',NOW).ok,false,'out-of-range percent rejected');
 // 5. Mapping: provider + window; ambiguity and duplicates are never resolved silently.
 const subs=[{id:'c1',provider:'Claude Pro (synthetic)'},{id:'c2',provider:'Claude Max (synthetic)'},{id:'g1',provider:'ChatGPT Plus (synthetic)'},{id:'x1',provider:'SuperGrok'}];
 const quotas=[{id:'qc1w',subId:'c1',model:'Claude weekly all',window:'weekly'},{id:'qc1s',subId:'c1',model:'Claude Sonnet weekly',window:'weekly'},{id:'qc2w',subId:'c2',model:'Claude weekly all',window:'weekly'},{id:'qc15',subId:'c1',model:'Claude session',window:'5h'},{id:'qg5',subId:'g1',model:'Codex',window:'5h'},{id:'qgw',subId:'g1',model:'Codex',window:'weekly'},{id:'qxw',subId:'x1',model:'Grok',window:'weekly'}];
 r=parseUsageText('Current session\n 12% used\nCurrent week (all models)\n 34% used\nCurrent week (Sonnet only)\n 5% used\nCurrent week (Opus only)\n 1% used',NOW);
 let m=matchUsageRows(r.rows,'claude',subs,quotas);
 assert.deepEqual(m.map(x=>x.status),['matched','ambiguous','matched','unmatched']);
 assert.deepEqual([...m[1].candidates].sort(),['qc1s','qc1w','qc2w']);
 assert.equal(m[1].candidates.length,3,'two Claude accounts + Sonnet pool all weekly candidates for an unhinted row');
 assert.equal(m[2].poolId,'qc1s');assert.equal(m[0].poolId,'qc15');
 r=parseUsageText('5h limit: 96% left\nWeekly limit: 94% left',NOW);
 m=matchUsageRows(r.rows,'codex',subs,quotas);assert.deepEqual(m.map(x=>x.poolId),['qg5','qgw']);
 assert.equal(matchUsageRows(r.rows,null,subs,quotas)[0].status,'unmatched','undetected provider never auto-maps');
 assert.deepEqual(usageConflicts(['qg5','qg5','skip','skip','']),['qg5']);
 assert.deepEqual(usageConflicts(['qg5','qgw','skip','']),[]);
 // Same text pasted twice => both rows auto-map to the same single pool => conflict that blocks Confirm.
 r=parseUsageText('5h limit: 96% left\n5h limit: 90% left',NOW);m=matchUsageRows(r.rows,'codex',subs,quotas);
 assert.deepEqual(usageConflicts(m.map(x=>x.poolId)),['qg5']);
 // Invariants: no network primitives, storage key unchanged.
 assert.ok(!/fetch\(|XMLHttpRequest|sendBeacon|WebSocket/.test(html.replace(/self\.addEventListener[^\n]*/,'')),'index.html must stay network-free');
 assert.ok(html.includes("STORE='ai-quota-control-center-v1'"));
 console.log('PASS: paste-usage parser (normal, remaining-vs-used, missing reset, garbage, duplicate/ambiguous pools) — synthetic samples only');
}
