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

// Run the updated provider Lab gates from the exact shipped HTML.
const vm=require('node:vm');
const labStart=html.indexOf("const LAB_STORE=");
const labEnd=html.indexOf("let labProvider=",labStart);
assert.ok(labStart>=0&&labEnd>labStart);
const lab=vm.runInNewContext(html.slice(labStart,labEnd)+
 '({LAB_FIELDS,LAB_PROVIDERS,LAB_CASES,LAB_RUBRIC,LAB_SMOKE,labValueValid,labCohortValid,providerLabDecision,providerLabPrompt})');
const {LAB_FIELDS,LAB_PROVIDERS,LAB_CASES,LAB_RUBRIC,LAB_SMOKE,labValueValid,labCohortValid,providerLabDecision,providerLabPrompt}=lab;
const [gemini]=LAB_PROVIDERS,mixed=LAB_PROVIDERS.at(-1);
assert.deepEqual(Array.from(LAB_PROVIDERS,p=>p.name),[
 'Google Gemini API','GroqCloud','Inferbase','OpenRouter','Cloudflare Workers AI',
 'SambaNova Cloud','Cohere','NeverMetered','Vercel AI Gateway','AIHubMix'
]);
assert.equal(LAB_SMOKE.length,5);
assert.ok(html.includes("LAB_COHORT_STORE=LAB_STORE+'cohort'"));
assert.ok(html.includes("id='lab-cohort-add'")||html.includes('id="lab-cohort-add"'));
assert.ok(html.includes("status.startsWith('MANUAL PASS')"));
assert.ok(html.includes('requestedModel')&&html.includes('Exact requested model ID'));
assert.ok(html.includes('lang="bn"'));
const fresh=Object.fromEntries(Object.keys(LAB_FIELDS).map(key=>[key,'']));
assert.equal(providerLabDecision(gemini,fresh).status,'NOT RUN');
const cohort={providerIds:['gemini'],evidenceRef:'cohort-2026'};
assert.equal(labCohortValid(cohort),true);
assert.equal(labCohortValid({providerIds:['gemini','groq','inferbase','vercel'],evidenceRef:'cohort-2026'}),false);
assert.equal(labCohortValid({providerIds:['gemini','gemini'],evidenceRef:'cohort-2026'}),false);
assert.equal(labCohortValid({providerIds:['aihubmix'],evidenceRef:'cohort-2026'}),false);
const qualified={
 ...fresh,run:'synth-run',requestedModel:'requested-1',model:'served-1',route:'synthetic/provider-1',effort:'N/A',
 eligibility:'pass',quota:'pass',privacy:'pass',payment:'pass',preflightRef:'synth-s0',
 plain:'pass',stream:'pass',json:'pass',tool:'pass',agent:'pass',agentTurns:'3',agentRef:'synth-agent',
 budgetRef:'approved-budget-v1',smokeCalls:'5',smokeRef:'synth-smoke',
 reliability:'pass',repeatCalls:'6',cash:'0',credit:'0.08',quotaUnits:'21',
 quotaType:'requests',seconds:'50',reviewRef:'synth-review'
};
for(const [i,c] of LAB_CASES.entries()){
 assert.equal(c.id,'P'+String(i+1).padStart(2,'0'));
 const prompt=providerLabPrompt(c);
 assert.ok(prompt.includes('CASE ID: '+c.id)&&prompt.includes('TASK: '+c.task+'\nOUTPUT:'));
 assert.ok(prompt.includes('All prices invented for testing, not real offers.'));
 assert.doesNotMatch(prompt,/SOURCE_UNVERIFIED|ELIGIBILITY_UNVERIFIED|Expected reviewer evidence/);
 for(const [key,,max] of LAB_RUBRIC)qualified[c.id+key]=String(i<8?max:0);
 qualified[c.id+'critical']='no';
 qualified[c.id+'ref']='synth-'+c.id;
}
const notSelected=providerLabDecision(gemini,qualified,{providerIds:[],evidenceRef:''});
assert.equal(notSelected.status,'HOLD');
assert.equal(notSelected.qualityReady,false);
assert.equal(notSelected.canJoinCohort,true);
const selected=providerLabDecision(gemini,qualified,cohort);
assert.equal(selected.status,'MANUAL PASS — REVIEW PENDING');
assert.equal(selected.accepted,8);
assert.equal(selected.scored,10);
assert.equal(selected.critical,0);
assert.equal(selected.qualityReady,true);
for(const change of [
 {eligibility:''},{privacy:'hold'},{payment:'hold'},{stream:'hold'},{tool:''},{agent:''},
 {agentTurns:'4'},{agentRef:''},{budgetRef:''},{requestedModel:'auto'},{model:'auto'},
 {route:'openrouter/free'},{cash:''},{cash:'0.01'},{credit:''},{quotaType:''},{reviewRef:''},
 {reliability:''},{repeatCalls:'5'},{P10ref:''},{P10critical:'yes'},{P01accuracy:'0'},
 {smokeCalls:'6'}
])assert.equal(providerLabDecision(gemini,{...qualified,...change},cohort).status,'HOLD',JSON.stringify(change));
assert.equal(providerLabDecision(gemini,{...qualified,smokeCalls:'6'},cohort).qualityReady,false);
assert.equal(providerLabDecision(mixed,qualified,cohort).status,'HOLD');
assert.equal(providerLabDecision(mixed,qualified,cohort).qualityReady,false);
assert.equal(labValueValid('effort','N/A'),true);
assert.equal(labValueValid('cash','0'),true);
assert.equal(labValueValid('cash',''),true);
assert.equal(labValueValid('cash','-1'),false);
assert.equal(labValueValid('smokeCalls','5.5'),false);
assert.equal(labValueValid('P01accuracy','3'),false);
assert.equal(labValueValid('model','@cf/toy/model'),true);
assert.equal(labValueValid('model','example@example.test'),false);
assert.equal(labValueValid('run','<img>'),false);
assert.equal(labValueValid('preflightRef','https://example.test/?token=example'),false);
assert.equal(labValueValid('preflightRef','sk-demonstration'),false);
console.log('PASS: Lab prompts, R-AGENT, manual status, shared top-three, budget and evidence gates');
