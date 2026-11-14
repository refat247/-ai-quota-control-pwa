"""Synthetic-only Chromium smoke tests. No personal dataset or production writes."""
import json
import os
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
    return {'meta':{'snapshot':'synthetic','version':'3.0.2','updated':''}, 'subs':subs,'quotas':quotas,'milestones':milestones}

def assert_page(page,expression,msg):
    assert page.evaluate(expression), msg

def main():
    with sync_playwright() as p:
        executable=os.environ.get('CHROME_PATH')
        browser=p.chromium.launch(headless=True, executable_path=executable if executable else None, args=['--no-sandbox'])
        def get_page(width=390,host=BASE,add_init=None,stored=None):
            # This model environment blocks even localhost navigation. Chromium DOM
            # simulation uses an explicit in-memory localStorage and test-only
            # fileMode/origin substitutions. Do not classify as real HTTPS persistence.
            context=browser.new_context(viewport={'width':width,'height':780},service_workers='block')
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
            page.set_content(fake,wait_until='domcontentloaded')
            page.wait_for_selector('#appview .page-head')
            assert not errors, f'JS errors: {errors}'
            return context,page,errors
        for width in [320,390,768,1366]:
            ctx,page,errs=get_page(width)
            assert_page(page,'document.documentElement.scrollWidth <= window.innerWidth',f'overflow at {width}')
            assert 'PRIVATE IMPORT HOLD' not in page.locator('#saveStatus').inner_text(), 'not github host'
            if width==390:
                # Fresh installation: no plan exists, so Quotas -> Add must guide.
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
                page.locator('button[data-tab="quotas"]').first.click()
                assert page.locator('#quotaList .quota-card').count()==17, 'quota cards count'
                page.locator('[data-quick="q0"]').first.click()
                assert page.locator('#sheetSave').inner_text()=='Save changes'
                assert page.locator('.layout').evaluate('(e)=>e.inert') is True, 'background not inert'
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
        # Simulate quota-save storage failure, status must not claim saved.
        init="const real=window.localStorage.setItem.bind(window.localStorage); window.localStorage.setItem=function(k,v){if(k==='"+STORE+"')throw Error('Simulated quota storage failure');return real(k,v)};"
        ctx,page,_=get_page(390,BASE,init,stored=json.dumps(fixture()))
        page.locator('button[data-tab="quotas"]').first.click()
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
                page.locator('[data-quick="q0"]').first.click()
                page.locator('input[name="used"]').fill('42')
                page.locator('#sheetSave').click()
                page.close()
                page=ctx.new_page();page.goto(url,wait_until='domcontentloaded')
                assert str(json.loads(page.evaluate('localStorage.getItem("'+STORE+'")'))['quotas'][0]['used'])=='42'
                print('PASS CI real localhost origin: imported 17 quotas; 42% survives new Chromium tab')
                ctx.close()
            finally:srv.shutdown();srv.server_close()
        browser.close()
if __name__=='__main__':main()