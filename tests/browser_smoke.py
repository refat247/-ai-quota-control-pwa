"""Synthetic-only Chromium smoke tests. No personal dataset or production writes."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, Error

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text('utf8')
STORE='ai-quota-control-center-v1'
BASE='https://quota-test.example/'
GITHUB='https://refat247.github.io/-ai-quota-control-pwa/'

def fixture():
    subs=[{'id':f's{i}','provider':'SuperGrok' if i==5 else f'Synthetic Provider {i}', 'plan':f'Test Plan {i}', 'emails':'', 'status':'unknown'} for i in range(6)]
    windows=['weekly','5h','custom']
    quotas=[{'id':f'q{i}','subId':f's{i%6}','model':f'Test Pool {i}','scope':'synthetic','window':'weekly' if i%6==5 else windows[i%3], 'used':'15', 'nextReset':'','behavior':'manual','cycleHours':'','project':False,'verified':False,'note':''} for i in range(17)]
    milestones=[{'id':f'm{i}','title':f'Synthetic date {i}','date':'','kind':'test','note':''} for i in range(6)]
    return {'meta':{'snapshot':'synthetic','version':'3.3.1','updated':''}, 'subs':subs,'quotas':quotas,'milestones':milestones}

def assert_page(page,expression,msg):
    assert page.evaluate(expression), msg

def open_home_filters(page):
    if not page.locator('#cockpitFilters').evaluate('(e)=>e.open'):
        page.locator('#cockpitFilters summary').click()

LAB_STORE = 'ai-provider-lab-v1:gemini'

def open_lab(page):
    page.locator('button[data-tab="lab"]').click()
    assert page.get_by_role('heading', name='Provider Qualification Lab').is_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')

def lab_flow(page):
    open_lab(page)
    form=page.locator('#lab-form')
    save=form.get_by_role('button',name='Save draft')
    status=page.locator('#lab-decision-status')
    assert status.inner_text()=='NOT RUN'
    assert page.locator('#lab-provider option').count()==10
    assert page.locator('#lab-provider option').last.inner_text()=='AIHubMix'
    assert page.locator('#lab-cohort-panel').is_visible()
    assert 'কোনো provider API call করে না' in page.locator('#lab-privacy').inner_text()
    before=page.evaluate('(key)=>localStorage.getItem(key)',STORE)

    def fill(key,value): form.locator(f'[name="{key}"]').fill(value)
    def choose(key,value): form.locator(f'[name="{key}"]').select_option(value)

    for key,value in dict(run='synthetic-01',requestedModel='requested-1',model='served-1',
                          route='toy/provider-1',effort='N/A').items():
        fill(key,value)
    for key in ('eligibility','quota','privacy','payment'):
        choose(key,'pass')
    fill('preflightRef','synth-preflight')
    save.click()
    assert status.inner_text()=='HOLD'
    assert 'no owner-approved budget addendum is configured' in page.locator('#lab-summary').inner_text()

    form.get_by_text('S1–S2 · Smoke and local tool checks',exact=True).click()
    for key in ('plain','stream','json','tool','agent'):
        choose(key,'pass')
    fill('agentTurns','3')
    fill('agentRef','synth-agent')
    fill('budgetRef','approved-budget-v1')
    fill('smokeCalls','5')
    fill('smokeRef','synth-smoke')
    form.get_by_text('Run metrics and reliability',exact=True).click()
    fill('cash','0')
    save.click()
    assert status.inner_text()=='HOLD'
    assert page.locator('#lab-cohort-add').is_enabled()
    page.locator('#lab-cohort-ref').fill('cohort-selection-01')
    page.locator('#lab-cohort-add').click()
    assert '1/3' in page.locator('#lab-cohort-panel').inner_text()
    assert page.locator('#lab-quality').is_enabled() is True
    assert page.locator('#lab-prompt-case').count()==1

    # Three selected IDs are the hard ceiling. A fourth provider cannot be added.
    page.evaluate("""() => localStorage.setItem('ai-provider-lab-v1:cohort',
      JSON.stringify({providerIds:['gemini','groq','inferbase'],evidenceRef:'cohort-selection-01'}))""")
    page.locator('#lab-provider').select_option('vercel')
    assert '3/3' in page.locator('#lab-cohort-panel').inner_text()
    assert page.locator('#lab-cohort-add').is_disabled()
    assert page.evaluate('(key)=>localStorage.getItem(key)',STORE)==before
    assert 'PASS' not in page.locator('#lab-summary').inner_text()
    print('PASS Lab: Bengali guidance, requested/served model, N/A, R-AGENT, budget HOLD and shared top-three cap')
 
def main():
    with sync_playwright() as p:
        executable=os.environ.get('CHROME_PATH')
        browser=p.chromium.launch(headless=True, executable_path=executable if executable else None, args=['--no-sandbox'])
        def get_page(width=390,host=BASE,add_init=None,stored=None,force_home_error=False):
            # This model environment blocks even localhost navigation. Chromium DOM
            # simulation uses an explicit in-memory localStorage and test-only
            # fileMode/origin substitutions. Do not classify as real HTTPS persistence.
            context=browser.new_context(viewport={'width':width,'height':700 if width==320 else 800 if width==360 else 844 if width==390 else 932 if width==430 else 780},service_workers='block')
            page=context.new_page()
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('dialog',lambda d:d.accept())
            seed={STORE:stored} if stored is not None else {}
            js="""window.__quotaStorage = %s;
                Object.defineProperty(window,'localStorage',{configurable:true,value:{
                  getItem(k){return Object.prototype.hasOwnProperty.call(window.__quotaStorage,k)?window.__quotaStorage[k]:null},
                  setItem(k,v){window.__quotaStorage[k]=String(v)},
                  removeItem(k){delete window.__quotaStorage[k]}
                }});
                """%json.dumps(seed)
            page.evaluate(js)
            if add_init: page.evaluate(add_init)
            fake=HTML.replace("const fileMode=!['http:','https:'].includes(location.protocol);","const fileMode=false;")
            fake=fake.replace("const sharedGitHubOrigin=location.origin==='https://refat247.github.io';", "const sharedGitHubOrigin=" + ("true" if host==GITHUB else "false") + ";")
            if force_home_error:
                fake=fake.replace('function overview(){', "function overview(){throw new TypeError('Synthetic home-only exception');",1)
            page.set_content(fake,wait_until='domcontentloaded')
            page.wait_for_selector('#appview .cockpit, #appview .page-head')
            assert not errors, f'JS errors: {errors}'
            return context,page,errors
        for width in [320,360,390,430,768,1366]:
            ctx,page,errs=get_page(width)
            assert_page(page,'document.documentElement.scrollWidth <= window.innerWidth',f'overflow at {width}')
            assert 'PRIVATE IMPORT HOLD' not in page.locator('#saveStatus').inner_text(), 'not github host'
            if width==390:
                # Correct first-use Home empty state plus guided Plan → Quota flow.
                assert 'No plans yet' in page.locator('#appview').inner_text(), 'first-run empty state incorrectly says filter miss'
                assert page.locator('[data-new="sub"]').count()>0, 'first-run Add Plan action missing'
                page.locator('button[data-tab="quotas"]').first.click()
                assert 'Start with a Plan' in page.locator('#appview').inner_text()
                page.locator('button[data-new="quota"]').first.click()
                assert page.locator('#sheetTitle').inner_text()=='Add plan', 'empty subscription opened impossible quota editor'
                assert 'Step 1 of 2' in page.locator('#sheetHint').inner_text()
                page.locator('input[name="provider"]').fill('Synthetic Provider')
                page.locator('input[name="plan"]').fill('Test Only')
                page.locator('#sheetSave').click()
                assert page.locator('#sheetTitle').inner_text()=='Add quota', 'Plan save did not resume quota form'
                assert 'Step 2 of 2' in page.locator('#sheetHint').inner_text()
                assert page.locator('select[name="subId"]').input_value()!=''
                page.locator('input[name="model"]').fill('Demo Model')
                page.locator('input[name="used"]').fill('42')
                page.locator('#sheetSave').click()
                saved=json.loads(page.evaluate('localStorage.getItem("'+STORE+'")'))
                assert len(saved['subs'])==1 and len(saved['quotas'])==1, 'guided Plan/Quota not saved'
                assert str(saved['quotas'][0]['used'])=='42'
                assert saved['quotas'][0]['subId']==saved['subs'][0]['id']
                print('PASS first-run: Add quota guides to Plan, resumes quota and saves')
            page.locator('button[data-tab="backup"]').first.click()
            assert page.locator('#pasteJSON').count()==1, 'missing paste UI'
            assert 'primary' in (page.locator('[data-action="exportJSON"]').get_attribute('class') or ''), 'safe Export must be primary'
            assert 'primary' not in (page.locator('[data-action="import"]').get_attribute('class') or ''), 'replace-all Import must not be primary'
            if width==390:
                data=fixture()
                page.locator('#pasteJSON').fill(json.dumps(data))
                page.locator('button[data-action="pasteImport"]').click()
                assert page.locator('#pasteJSON').input_value()=='', 'paste not cleared'
                # Verify file input also uses the common validated import path.
                page.locator('#filePicker').set_input_files(files={'name':'synthetic.json','mimeType':'application/json','buffer':json.dumps(data).encode()})
                page.wait_for_timeout(100)
                assert page.evaluate('localStorage.getItem("'+STORE+'")') is not None, 'file import failed'
                stored=json.loads(page.evaluate('localStorage.getItem("'+STORE+'")'))
                assert [len(stored[k]) for k in ('subs','quotas','milestones')]==[6,17,6], 'import counts'
                # Import must reject an unsupported Grok five-hour window, even via paste.
                before_bad=page.evaluate('localStorage.getItem("'+STORE+'")')
                bad=fixture();bad['quotas'][5]['window']='5h'
                page.locator('#pasteJSON').fill(json.dumps(bad))
                page.locator('button[data-action="pasteImport"]').click()
                assert page.evaluate('localStorage.getItem("'+STORE+'")')==before_bad, 'invalid import replaced previously saved data'
                bad_alias=fixture();bad_alias['subs'][5]['provider']='xAI';bad_alias['quotas'][5]['window']='5h'
                page.locator('#pasteJSON').fill(json.dumps(bad_alias))
                page.locator('button[data-action="pasteImport"]').click()
                assert page.evaluate('localStorage.getItem("'+STORE+'")')==before_bad, 'xAI 5h alias accepted'
                # v3.3.1 visual cockpit: ring cards, drilldowns, data remains untouched.
                page.locator('button[data-tab="overview"]').first.click()
                assert page.locator('#homeProviderList .provider-row').count()==6
                last_tile=page.locator('#homeProviderList .cockpit-tile').last.evaluate('(e)=>e.getBoundingClientRect().bottom')
                dock_top=page.locator('#navigation').evaluate('(e)=>e.getBoundingClientRect().top')
                if width>320:
                    assert last_tile<=dock_top+4, f'provider grid extends under bottom navigation: tile {last_tile}, dock {dock_top}'
                else:
                    assert page.evaluate('document.documentElement.scrollHeight <= innerHeight*1.20'), '320px Home is excessive scroll'
                assert page.locator('.home-kpi').count()==3
                assert page.locator('.home-usage-legend .legend-item').count()==4
                assert page.locator('.provider-row[data-sub-id="s1"] .cockpit-ring').count()==2
                assert page.locator('.provider-row[data-sub-id="s1"] .cockpit-ring-more').count()==1
                page.locator('.provider-row[data-sub-id="s1"]').click()
                assert page.locator('#cockpitDialog').evaluate('(x)=>x.open')
                assert page.locator('#cockpitDialog .cockpit-detail-row').count()==3
                assert page.locator('#cockpitDialog [data-quick]').count()==3
                page.evaluate('history.back()')
                page.wait_for_function('!document.querySelector("#cockpitDialog").open')
                assert page.locator('[data-dashboard="home"]').count()==1, 'Back left Home instead of closing dialog'
                page.locator('.provider-row[data-sub-id="s1"]').click()
                page.locator('#cockpitDialog [data-quick="q1"]').click()
                assert page.locator('#sheetback').evaluate('(x)=>x.classList.contains("open")'), 'drilldown quick edit failed'
                page.locator('#sheetCancel').click()
                page.wait_for_function('!document.querySelector("#sheetback").classList.contains("open")')
                # Provider editor cancellation returns to Home; successful save returns to provider.
                page.locator('.provider-row[data-sub-id="s1"]').click()
                page.locator('#cockpitDialog [data-quick="q1"]').click()
                page.locator('input[name="used"]').fill('61')
                page.locator('#sheetSave').click()
                page.wait_for_function('document.querySelector("#cockpitDialog").open')
                assert '61%' in page.locator('#cockpitDialog').inner_text(), 'Quick Save did not reopen same provider with updated value'
                page.locator('[data-close-cockpit]').click()
                page.locator('.provider-row[data-sub-id="s1"]').click()
                page.locator('#cockpitDialog [data-new="quota"]').click()
                assert page.locator('select[name="subId"]').input_value()=='s1', 'new model did not inherit selected provider'
                page.locator('#sheetCancel').click()
                page.locator('.provider-row[data-sub-id="s5"]').click()
                assert '5-hour pool: N/A' in page.locator('#cockpitDialog').inner_text()
                page.locator('[data-close-cockpit]').click()
                before_ui=page.evaluate('localStorage.getItem("'+STORE+'")')
                open_home_filters(page)
                page.locator('#homeSearch').fill('Synthetic Provider 1')
                assert page.locator('#homeProviderList .provider-row').count()==1
                page.locator('[data-clear-home]').click()
                assert page.locator('#homeProviderList .provider-row').count()==6
                page.locator('.provider-row[data-sub-id="s1"]').click()
                page.locator('#cockpitDialog [data-pin-provider="s1"]').click()
                open_home_filters(page)
                page.locator('[data-home-filter="pinned"]').click()
                assert page.locator('#homeProviderList .provider-row').count()==1
                open_home_filters(page)
                page.locator('[data-home-filter="all"]').click()
                open_home_filters(page)
                page.locator('[data-home-density="comfortable"]').click()
                assert page.evaluate('document.documentElement.dataset.quotaDensity')=='comfortable'
                assert page.evaluate('localStorage.getItem("'+STORE+'")')==before_ui
                assert page.evaluate('localStorage.getItem("ai-quota-ui-preferences-v1")') is not None
                page.locator('button[data-tab="subscriptions"]').first.click()
                assert page.locator('.cockpit-plan-tile').count()==6
                page.locator('[data-open-plan="s1"]').click()
                assert page.locator('#cockpitDialog [data-edit="sub"]').count()==1
                page.locator('[data-close-cockpit]').click()
                page.locator('button[data-tab="deadlines"]').first.click()
                assert page.locator('.cockpit-segments button').count()==4
                assert page.locator('.cockpit-event-list .eventrow').count()<=3
                page.locator('[data-open-events="all"]').click()
                assert page.locator('#cockpitDialog').evaluate('(x)=>x.open')
                page.locator('[data-close-cockpit]').click()
                assert page.evaluate('localStorage.getItem("'+STORE+'")')==before_ui
                print('PASS v3.3.1 visual cockpit, plan/quotas/date navigation and untouched JSON')

                page.locator('button[data-tab="quotas"]').first.click()
                assert page.locator('.cockpit-icon-tile').count()==6, 'six quota provider shortcuts'
                assert page.locator('.cockpit-icon-tile .cockpit-ring').count()>=5, 'provider shortcut must show worst-used ring'
                page.locator('[data-quota-list="list"]').click()
                assert page.locator('#quotaList .quota-card').count()==17, 'all models retained'
                assert page.locator('#quotaList .compact-quota').count()==17, 'old tall quota cards not replaced'
                assert page.locator('#quotaList [data-quick]').count()==17, 'every model Update missing'
                page.locator('[data-quick="q0"]').first.click()
                assert page.locator('#sheetSave').inner_text()=='Save changes'
                assert page.locator('.layout').evaluate('(e)=>e.inert') is True, 'background not inert'
                page.locator('input[name="used"]').fill('140')
                page.locator('#sheetSave').click()
                assert page.locator('#sheetError').is_visible(), '140 must show inline validation error'
                assert page.locator('input[name="used"]').get_attribute('aria-invalid')=='true', 'invalid input must be announced'
                page.locator('input[name="used"]').fill('42')
                page.locator('#sheetSave').click()
                assert page.locator('.layout').evaluate('(e)=>e.inert') is False
                assert 'Saved automatically' in page.locator('#saveStatus').inner_text()
                saved_raw=page.evaluate('localStorage.getItem("'+STORE+'")')
                ctx2,page2,errs2=get_page(390,stored=saved_raw)
                stored=json.loads(page2.evaluate('localStorage.getItem("'+STORE+'")'))
                ctx2.close()
                assert str(stored['quotas'][0]['used'])=='42', 'quota reverted after reload'
                assert not errs,errs
                print('PASS 390px: 6/17/6 paste, Grok5h rejection, 42% edit, same-origin reload, focus inert')
            ctx.close()
            print('PASS viewport',width)
        for width in (320, 390, 768, 1366):
            ctx, page, errs = get_page(width)
            if width == 390:
                lab_flow(page)
            else:
                open_lab(page)
                assert page.locator('#lab-decision-status').inner_text() == 'NOT RUN'
            assert not errs, errs
            ctx.close()
        ctx, page, errs = get_page(host=GITHUB)
        open_lab(page)
        assert page.get_by_role('button', name='Save draft').is_disabled()
        assert not errs, errs
        ctx.close()
        ctx, page, errs = get_page(add_init="""localStorage.setItem('ai-provider-lab-v1:gemini','{corrupt');""")
        open_lab(page)
        assert page.get_by_role('button', name='Save draft').is_disabled()
        assert page.evaluate('(key) => localStorage.getItem(key)', LAB_STORE) == '{corrupt'
        assert not errs, errs
        ctx.close()
        # v3.3.1 synthetic thresholds; every color must retain a textual percentage/Unknown.
        color_fixture=fixture()
        color_fixture['quotas'][0]['used']='30'
        color_fixture['quotas'][1]['used']='80'
        color_fixture['quotas'][2]['used']='95'
        color_fixture['quotas'][3]['used']=''
        color_fixture['quotas'][4]['used']='0'
        color_fixture['quotas'][13]['used']='100'
        color_fixture['quotas'][14]['used']='95'
        color_raw=json.dumps(color_fixture)
        for width in (320,360,390,430):
            ctx,page,errs=get_page(width,stored=color_raw)
            for tone in ('low','high','critical'):
                assert page.locator('.cockpit-ring.tone-'+tone).count()>0, 'missing Home semantic '+tone+' ring'
            assert page.locator('.home-usage-legend').is_visible(), 'usage legend is missing'
            # Critical-first Home can hide 0% / Unknown. They MUST remain reachable,
            # accurately distinguished in the complete model list, and never averaged.
            page.locator('button[data-tab="quotas"]').first.click()
            page.locator('[data-quota-list="list"]').click()
            assert page.locator('#quotaList .cockpit-ring.tone-low .meter-text').filter(has_text='0%').count()>=1, 'zero must not be unknown'
            assert page.locator('#quotaList .cockpit-ring.tone-unknown').count()>=1, 'blank must remain Unknown in full list'
            page.locator('button[data-tab="overview"]').first.click()
            assert page.locator('#homeProviderList .provider-row').count()==6, 'six provider compact rows required'

            # A112: measure actual DOM geometry, not just element counts.
            metrics=page.evaluate("""() => {
              const tiles=[...document.querySelectorAll('#homeProviderList .cockpit-tile')];
              let overlap=0,outside=0,clippedWidth=0;
              for(const tile of tiles){
                const box=tile.getBoundingClientRect();
                const labels=[...tile.querySelectorAll('.cockpit-ring-label')];
                const rects=labels.map(l=>l.getBoundingClientRect());
                for(let i=0;i<rects.length;i++){
                  const r=rects[i];
                  if(r.left<box.left-.5||r.right>box.right+.5)outside++;
                  if(labels[i].scrollWidth>labels[i].clientWidth+.5)clippedWidth++;
                  for(let j=i+1;j<rects.length;j++){
                    const x=Math.min(r.right,rects[j].right)-Math.max(r.left,rects[j].left);
                    const y=Math.min(r.bottom,rects[j].bottom)-Math.max(r.top,rects[j].top);
                    if(x>.5&&y>.5)overlap++;
                  }
                }
              }
              return {overlap,outside,clippedWidth,doc:document.documentElement.scrollHeight,
                      viewport:innerHeight,last:tiles.at(-1)?.getBoundingClientRect().bottom,
                      nav:document.querySelector('#navigation')?.getBoundingClientRect().top};
            }""")
            assert metrics['overlap']==0, f'A112 N1 label boxes overlap at {width}: {metrics}'
            assert metrics['outside']==0, f'A112 N1 labels leave provider tile at {width}: {metrics}'
            if width==320:
                assert (metrics['doc'] <= 1.15*metrics['viewport']+1 or metrics['last'] <= metrics['nav']-2), f'A112 320px failed both fold <=1.15 and 6/6 visible tiles: {metrics}'
            print('A112 measured geometry',width,metrics)
            page.locator('button[data-tab="quotas"]').first.click()
            centering=page.locator('.cockpit-icon-tile .cockpit-ring').first.evaluate("""r=>{
              const outer=r.getBoundingClientRect(),t=r.querySelector('.meter-text').getBoundingClientRect();
              return {dx:Math.abs((outer.left+outer.right-t.left-t.right)/2),
                      dy:Math.abs((outer.top+outer.bottom-t.top-t.bottom)/2)};
            }""")
            assert centering['dx']<=1.5 and centering['dy']<=1.5, f'A112 N2 ring text off-center {width}: {centering}'
            page.locator('button[data-tab="overview"]').first.click()

            assert '100%' in page.locator('.provider-row[data-sub-id="s1"]').inner_text(), '100% critical quota hidden behind +N'
            assert '95%' in page.locator('.provider-row[data-sub-id="s2"]').inner_text(), '95% critical quota hidden behind +N'
            assert 'Test Pool 13' in page.locator('.provider-row[data-sub-id="s1"]').inner_text(), 'individual model identity not shown'
            assert_page(page,'document.documentElement.scrollWidth <= window.innerWidth','v3.3.1 compact UI overflow')
            assert page.evaluate('localStorage.getItem("'+STORE+'")')==color_raw, 'UI changed original quota JSON'
            assert not errs, 'v3.3.1 JS errors: '+str(errs)
            ctx.close()
        print('PASS v3.3.1 manual color legend, per-model chips, quick vs comfortable and 320/390px')
        # Batch A data-driven filter regression: timed resets and type filters.
        # Synthetic Dhaka timestamps only; avoids user's private quota data.
        filter_data=fixture()
        dhaka=timezone(timedelta(hours=6))
        now_bd=datetime.now(dhaka)
        filter_data['quotas'][0]['nextReset']=(now_bd+timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
        filter_data['quotas'][2]['nextReset']=(now_bd-timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
        filter_raw=json.dumps(filter_data)
        ctx,page,errs=get_page(390,stored=filter_raw)
        open_home_filters(page)
        page.locator('[data-home-filter="soon"]').click()
        assert page.locator('#homeProviderList .provider-row').count()==1, 'soon filter should match one provider'
        assert page.locator('#homeProviderList .provider-row').first.get_attribute('data-sub-id')=='s0', 'soon filter provider mismatch'
        open_home_filters(page)
        page.locator('[data-home-filter="overdue"]').click()
        assert page.locator('#homeProviderList .provider-row').count()==1, 'overdue filter should match one provider'
        assert page.locator('#homeProviderList .provider-row').first.get_attribute('data-sub-id')=='s2', 'overdue filter provider mismatch'
        open_home_filters(page)
        page.locator('[data-home-filter="weekly"]').click()
        assert page.locator('#homeProviderList .provider-row[data-sub-id="s5"]').count()==1, 'weekly should include Grok weekly'
        open_home_filters(page)
        page.locator('[data-home-filter="5h"]').click()
        assert page.locator('#homeProviderList .provider-row[data-sub-id="s1"]').count()==1, '5-hour should include matching provider'
        assert page.locator('#homeProviderList .provider-row[data-sub-id="s5"]').count()==0, 'Grok must not acquire fake 5-hour pool'
        assert page.evaluate('localStorage.getItem("'+STORE+'")')==filter_raw, 'Home filters modified quota JSON'
        assert not errs, f'Home filter JS errors: {errs}'
        ctx.close()
        print('PASS Batch A deterministic 24h/overdue/weekly/5h filtering; quota JSON unchanged')
        # F1: a formerly valid saved dataset made invalid by a plan/provider change
        # must enter non-destructive read-only recovery; it must not silently reset.
        corrupted=fixture()
        corrupted['subs'][1]['provider']='xAI'
        assert corrupted['quotas'][1]['window']=='5h'
        raw_corrupt=json.dumps(corrupted)
        ctx,page,_=get_page(390,stored=raw_corrupt)
        assert 'Read-only recovery' in page.locator('#appview').inner_text()
        assert page.locator('[data-action="exportRaw"]').count()==1
        assert page.evaluate('localStorage.getItem("'+STORE+'")')==raw_corrupt
        page.locator('button[data-tab="subscriptions"]').first.click()
        assert 'Read-only recovery' in page.locator('#appview').inner_text()
        assert page.evaluate('localStorage.getItem("'+STORE+'")')==raw_corrupt
        ctx.close()
        print('PASS F1 malformed cache preserves original raw data and locks editing')
        # F1: an edit to xAI must be rejected while a linked 5h quota exists.
        valid=fixture()
        ctx,page,_=get_page(390,stored=json.dumps(valid))
        page.locator('button[data-tab="subscriptions"]').first.click()
        page.locator('.cockpit-plan-tile[data-open-plan="s1"]').click()
        page.locator('#cockpitDialog [data-edit="sub"][data-id="s1"]').click()
        page.locator('input[name="provider"]').fill('xAI')
        page.locator('#sheetSave').click()
        assert json.loads(page.evaluate('localStorage.getItem("'+STORE+'")'))['subs'][1]['provider']=='Synthetic Provider 1'
        assert page.locator('#sheetback').evaluate('(e)=>e.classList.contains("open")') is True
        ctx.close()
        print('PASS F1 invalid provider rename blocked before localStorage write')
        # Shared-origin MUST NOT accept private JSON even when file-picker event is forced.
        ctx,page,_=get_page(390,GITHUB)
        assert 'PRIVATE IMPORT HOLD' in page.locator('#saveStatus').inner_text()
        page.locator('button[data-tab="backup"]').first.click()
        assert page.locator('#pasteJSON').is_disabled()
        assert page.locator('button[data-action="import"]').is_disabled()
        page.locator('#filePicker').set_input_files(files={'name':'dummy.json','mimeType':'application/json','buffer':json.dumps(fixture()).encode()})
        page.wait_for_timeout(300)
        assert page.evaluate('localStorage.getItem("'+STORE+'")') is None,'shared-origin import succeeded'
        page.locator('button[data-tab="subscriptions"]').first.click()
        page.locator('button[data-new="sub"]').first.click()
        assert not page.locator('#sheetback').evaluate('(e)=>e.classList.contains("open")'), 'editor opened on shared origin'
        assert page.evaluate('localStorage.getItem("'+STORE+'")') is None,'shared-origin manual edit wrote storage'
        ctx.close()
        print('PASS shared github.io origin import and manual editor blocked')
        # A86 root cause: multiple monthly renewal dates previously hit
        # ReferenceError because comparator referenced undefined 'o' not 'a'.
        # Tests use synthetic data only; never inspect owner localStorage.
        renewals=fixture()
        renewals['subs'][0]['renewDay']='24'
        renewals['subs'][1]['renewDay']='25'
        original_renewals=json.dumps(renewals)
        ctx,page,errs=get_page(390,stored=original_renewals)
        assert page.locator('#appview .home-kpi').count()==3, 'Home failed with two renewal dates'
        assert 'Home temporarily unavailable' not in page.locator('#appview').inner_text(), 'root bug still triggers the fallback'
        assert 'Synthetic Provider 0' in page.locator('.home-kpi').nth(1).inner_text(), 'incorrect earliest expected renewal'
        assert page.evaluate('localStorage.getItem("'+STORE+'")')==original_renewals, 'Home changed stored synthetic data'
        ctx.close()
        print('PASS A86 two monthly renewals: Home renders and selects earliest without storage change')
        # A85 Android blank-Home regression: a synthetic view failure must show a
        # non-destructive recovery panel and keep original localStorage untouched.
        original=json.dumps(fixture())
        ctx,page,errs=get_page(390,stored=original,force_home_error=True)
        assert 'Home temporarily unavailable' in page.locator('#appview').inner_text()
        assert 'Diagnostic: TypeError' in page.locator('#appview').inner_text()
        assert page.locator('#saveStatus').inner_text().strip(), 'save status blank after Home exception'
        assert page.evaluate('localStorage.getItem("'+STORE+'")')==original, 'Home fallback changed stored data'
        page.locator('button[data-tab="backup"]').first.click()
        assert 'Home temporarily unavailable' not in page.locator('#appview').inner_text(), 'backup navigation failed'
        assert page.locator('[data-action="exportJSON"]').count()>0, 'private export unavailable after Home error'
        assert page.evaluate('localStorage.getItem("'+STORE+'")')==original, 'backup route mutated records'
        ctx.close()
        print('PASS A85 forced Home TypeError: visible error boundary, Backup available, storage unchanged')
        # Simulate quota-save storage failure, status must not claim saved.
        init="const real=window.localStorage.setItem.bind(window.localStorage); window.localStorage.setItem=function(k,v){if(k==='"+STORE+"')throw Error('Simulated quota storage failure');return real(k,v)};"
        ctx,page,_=get_page(390,BASE,init,stored=json.dumps(fixture()))
        page.locator('button[data-tab="quotas"]').first.click()
        page.locator('[data-quota-list="list"]').click()
        page.locator('[data-quick="q0"]').first.click()
        page.locator('input[name="used"]').fill('44')
        page.locator('#sheetSave').click()
        assert 'Not saved reliably' in page.locator('#saveStatus').inner_text()
        assert 'Saved automatically' not in page.locator('#saveStatus').inner_text()
        ctx.close(); print('PASS localStorage setItem failure status')
        if os.environ.get('QUOTA_REAL_ORIGIN_TEST') == '1':
            # GitHub-hosted runner can reach a real loopback HTTP origin.
            # This is stronger than the mock-store test, but not Android acceptance.
            import threading
            from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
            class QuietHandler(SimpleHTTPRequestHandler):
                def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
                def log_message(self,*args):pass
            srv=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler)
            thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
            try:
                url=f'http://127.0.0.1:{srv.server_address[1]}/'
                ctx=browser.new_context(viewport={'width':390,'height':780},service_workers='block')
                page=ctx.new_page(); page.on('dialog',lambda d:d.accept())
                page.goto(url,wait_until='domcontentloaded')
                page.locator('button[data-tab="backup"]').first.click()
                page.locator('#pasteJSON').fill(json.dumps(fixture()))
                page.locator('button[data-action="pasteImport"]').click()
                assert len(json.loads(page.evaluate('localStorage.getItem("'+STORE+'")'))['quotas'])==17
                page.locator('button[data-tab="quotas"]').first.click()
                page.locator('[data-quota-list="list"]').click()
                page.locator('[data-quick="q0"]').first.click()
                page.locator('input[name="used"]').fill('42')
                page.locator('#sheetSave').click()
                page.close()
                page=ctx.new_page();page.goto(url,wait_until='domcontentloaded')
                assert str(json.loads(page.evaluate('localStorage.getItem("'+STORE+'")'))['quotas'][0]['used'])=='42'
                print('PASS CI real localhost origin: imported 17 quotas; 42% survives new Chromium tab')
                before = page.evaluate('(key) => localStorage.getItem(key)', STORE)
                requests = []
                ctx.on('request', lambda request: requests.append(request.url))
                lab_flow(page)
                assert page.evaluate('(key) => localStorage.getItem(key)', STORE) == before
                assert not requests, requests
                page.locator('button[data-tab="backup"]').click()
                with page.expect_download() as export:
                    page.get_by_role('button', name='Export private JSON backup').click()
                quota_backup = json.loads(Path(export.value.path()).read_text('utf8'))
                assert quota_backup == json.loads(before)
                page.reload()
                open_lab(page)
                assert page.locator('#lab-decision-status').inner_text() == 'HOLD'
                assert '0/10 scored' in page.locator('#lab-summary').inner_text()
                ctx.close()

                # HTTP localhost is secure for service workers. Register the
                # shipped worker explicitly because auto-registration needs HTTPS.
                ctx = browser.new_context(service_workers='allow')
                page = ctx.new_page()
                page.goto(url)
                page.evaluate("async () => {await navigator.serviceWorker.register('./sw.js'); await navigator.serviceWorker.ready;}")
                page.wait_for_function('navigator.serviceWorker.controller !== null')
                open_lab(page)
                page.locator('#lab-form [name="run"]').fill('offline-synthetic')
                page.get_by_role('button', name='Save draft').click()
                ctx.set_offline(True)
                page.reload()
                open_lab(page)
                assert page.locator('#lab-form [name="run"]').input_value() == 'offline-synthetic'
                assert page.locator('#lab-decision-status').inner_text() == 'HOLD'
                print('PASS Lab: no requests during capture, quota backup unchanged, origin reload and cached offline draft')
                ctx.close()
            finally:srv.shutdown();srv.server_close()
        browser.close()
if __name__=='__main__':main()