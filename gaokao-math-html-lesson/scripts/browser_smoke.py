#!/usr/bin/env python3
"""Browser smoke test for single-file HTML math lessons. Requires playwright & Chromium.
Usage: python scripts/browser_smoke.py /path/to/lesson.html [--screenshot out.png]
Install if not available: pip install playwright; playwright install chromium
Tests load, offline reload, runtime errors, canvas visual updates during auto demo,
pause stability, and responsive viewport. Does not replace manual math audits.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sys
import shutil

def main(path:Path, screenshot:Path|None):
    try:from playwright.sync_api import sync_playwright
    except ImportError:
        print('UNAVAILABLE: playwright is not installed. Perform equivalent manual browser tests.');return 2
    errors=[];reports=[]
    try:
        with sync_playwright() as p:
            browser_args=dict(headless=True,args=['--no-sandbox'])
            system_chrome=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
            if system_chrome:browser_args['executable_path']=system_chrome
            browser=p.chromium.launch(**browser_args)
            context=browser.new_context(viewport={'width':1360,'height':850},device_scale_factor=1)
            page=context.new_page()
            page.on('pageerror',lambda exc:errors.append(str(exc)))
            page.on('console',lambda msg:errors.append('console: '+msg.text) if msg.type=='error' else None)
            file_loaded=True
            try:
                page.goto(path.resolve().as_uri(),wait_until='load',timeout=25000)
            except Exception as ex:
                if 'BLOCKED_BY_ADMINISTRATOR' not in str(ex):raise
                file_loaded=False
                reports.append('NOTE: file:// is blocked by this Chromium administrator policy; browser DOM/animation tested with identical inline HTML content instead')
                page.close()
                page=context.new_page()
                page.on('pageerror',lambda exc:errors.append(str(exc)))
                page.on('console',lambda msg:errors.append('console: '+msg.text) if msg.type=='error' else None)
                page.set_content(path.read_text(encoding='utf-8-sig'),wait_until='load')
            page.wait_for_timeout(400)
            title=page.title();reports.append('Loaded: '+title)
            if screenshot:
                screenshot.parent.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(screenshot),full_page=True)
                reports.append('Desktop screenshot: '+str(screenshot))
            canvas=page.locator('canvas').first
            has_canvas=page.locator('canvas').count()>0
            if has_canvas and canvas.bounding_box():
                btn=page.locator('button').filter(has_text=re.compile('自动演示|播放演示|播放动画')).first
                if btn.count()>0:
                    btn.click();page.wait_for_timeout(420)
                    a=canvas.screenshot()
                    page.wait_for_timeout(900)
                    b=canvas.screenshot()
                    if a==b:errors.append('Canvas did not visually change during 0.9s auto playback')
                    else:reports.append('Canvas changes continuously during auto playback')
                    pause=page.locator('button').filter(has_text=re.compile('暂停')).first
                    if pause.count()>0:
                        pause.click();page.wait_for_timeout(220)
                        c=canvas.screenshot();page.wait_for_timeout(420);d=canvas.screenshot()
                        if c!=d:errors.append('Canvas changed after pause; check continuous rendering/camera updates')
                        else:reports.append('Canvas stays stable after pausing')
                    # Verify the global playback timeline can jump to different moments.
                    seek=page.locator('#demoSeek, #seek').first
                    if seek.count()>0:
                        pics=[]
                        for fraction in (0.10,0.50,0.90):
                            seek.evaluate('''(el,f)=>{el.value=String(Math.round(Number(el.max)*f));el.dispatchEvent(new Event('input',{bubbles:true}));}''',fraction)
                            page.wait_for_timeout(110)
                            pics.append(canvas.screenshot())
                        if len(set(pics))<3:errors.append('Seek 10%, 50%, 90% did not produce distinct frames')
                        else:reports.append('Seek to 10%, 50%, 90% yields distinct frames')
                else:reports.append('No Chinese auto-demo button found; manually inspect controls')
            else:reports.append('No visible Canvas to pixel-test; manually assess SVG/WebGL interactions')
            context.set_offline(True)
            if file_loaded:page.reload(wait_until='load',timeout=25000)
            else:
                # set_content on same page executes inline let/const twice in the same realm.
                # Use a fresh document for the offline check.
                page.close()
                page=context.new_page()
                page.on('pageerror',lambda exc:errors.append(str(exc)))
                page.on('console',lambda msg:errors.append('console: '+msg.text) if msg.type=='error' else None)
                page.set_content(path.read_text(encoding='utf-8-sig'),wait_until='load')
            page.wait_for_timeout(300)
            if page.locator('body').inner_text().strip():reports.append('Offline '+('reload' if file_loaded else 'inline-load')+' passed')
            else:errors.append('Empty body after offline reload')
            context.set_offline(False)
            page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(300)
            bad=page.evaluate('document.documentElement.scrollWidth > innerWidth + 8')
            if bad:errors.append('Mobile viewport has excessive horizontal overflow')
            else:reports.append('Mobile 390px width: no horizontal overflow')
            if screenshot:
                page.screenshot(path=str(screenshot.with_name(screenshot.stem+'_mobile.png')),full_page=True)
            browser.close()
    except Exception as exc:
        errors.append('Unable to run browser: '+str(exc))
    print('\n'.join(reports))
    for e in errors:print('ERROR:',e)
    print('BROWSER RESULT:', 'FAIL' if errors else 'PASS (smoke only; not math/fps proof)')
    return 1 if errors else 0

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('file',type=Path);ap.add_argument('--screenshot',type=Path);args=ap.parse_args()
    if not args.file.exists():print('File not found');sys.exit(2)
    sys.exit(main(args.file,args.screenshot))