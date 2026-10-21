#!/usr/bin/env python3
"""Mandatory Chromium behavioral test for offline single-file HTML math lessons.
Requires pip install playwright && playwright install chromium if unavailable.
Usage: python scripts/browser_contract_test.py <file.html> [--shots output_folder]
"""
from __future__ import annotations
import argparse,sys,time,shutil,hashlib
from collections import defaultdict
from pathlib import Path
from playwright.sync_api import sync_playwright


def main() -> int:
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument('html')
    arg.add_argument('--shots',default=None)
    args=arg.parse_args()
    path=Path(args.html).resolve()
    if not path.is_file():print('ERROR: 文件不存在',path);return 2
    failures=[];notes=[]
    def check(ok,msg):
        print(('PASS' if ok else 'FAIL')+': '+msg)
        if not ok:failures.append(msg)

    with sync_playwright() as p:
        browser_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('chromium-browser')
        browser=p.chromium.launch(headless=True,executable_path=browser_path,args=['--no-sandbox','--disable-gpu-sandbox'])
        for viewport,tag in [({'width':1440,'height':900},'desktop'),({'width':390,'height':844},'mobile')]:
            context=browser.new_context(viewport=viewport,device_scale_factor=1,offline=True)
            page=context.new_page()
            errors=[]
            page.on('pageerror',lambda exc:errors.append(str(exc)))
            try:
                try:
                    page.goto(path.as_uri(),wait_until='load',timeout=20000)
                    print('INFO: '+tag+': 直接 file:// 加载成功')
                except Exception as e:
                    if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(e): raise
                    # This environment blocks file: scheme. Still test the exact HTML bytes,
                    # but explicitly report that OS double-click itself was not verified.
                    page.close()
                    page=context.new_page()
                    page.on('pageerror',lambda exc:errors.append(str(exc)))
                    page.set_content(path.read_text(encoding='utf-8-sig'),wait_until='load',timeout=20000)
                    print('INFO: '+tag+': 环境阻断 file://，已用相同 HTML 内容加载；不能视为双击文件实测')
                page.wait_for_timeout(240)
                has_contract=page.evaluate('typeof window.__lessonQA?.getSnapshot === "function" && typeof window.__lessonQA?.seek === "function"')
                check(has_contract,tag+': 测试接口存在')
                if not has_contract:
                    check(False,tag+': 无法执行播放/暂停/图文同步验收（缺少接口）')
                    continue
                snap=lambda:page.evaluate('window.__lessonQA.getSnapshot()')
                start=snap()
                dur=start['durationSec']
                check(abs(start['timeSec'])<.2 and dur>0,tag+': 初始进度与总时间合理')
                check(not start['playing'],tag+': 初始状态未自动占用播放')
                # verify that the scene is time-driven and deterministic even if seek is out-of-order
                shots=[];visual_hashes=[]
                for idx,pct in enumerate([0,.25,.5,.75,1]):
                    page.evaluate('(t)=>window.__lessonQA.seek(t)',pct*dur)
                    page.wait_for_timeout(45)
                    state=snap()
                    shots.append(state)
                    viz=page.locator('canvas, svg').first
                    if viz.count(): visual_hashes.append(hashlib.sha256(viz.screenshot()).hexdigest())
                    check(abs(state['timeSec']-pct*dur)<.15,tag+f': 定位 {int(pct*100)}% 后时间正确')
                    if args.shots:
                        out=Path(args.shots);out.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(out/f'{tag}_{int(pct*100):03d}.png'))
                sigs={s['sceneSignature'] for s in shots}
                check(len(sigs)>=3,tag+': 数学场景状态存在真实中间态')
                check(len(set(visual_hashes))>=3,tag+': 画布/图形像素实际发生变化（不是伪造状态签名）')
                page.evaluate('(t)=>window.__lessonQA.seek(t)',dur*.5)
                check(snap()['sceneSignature']==shots[2]['sceneSignature'],tag+': 进度反向跳转后图形可确定性还原')
                # every major section must have active caption events, not stuck on its first sentence
                groups=defaultdict(set)
                for i in range(1,40):
                    page.evaluate('(t)=>window.__lessonQA.seek(t)',dur*i/40)
                    s=snap();groups[s['chapterId']].add(s['captionId'])
                check(len(groups)>=3,tag+': 至少三章真实教学内容')
                check(sum(len(v)>=2 for v in groups.values())>=2,tag+': 多章内部解题文字随时间变更')
                # ensure controls are actually wired to shared playhead
                page.evaluate('window.__lessonQA.seek(0)')
                start_slider=page.locator('[data-lesson-control="seek"]').input_value()
                page.evaluate('window.__lessonQA.play()')
                page.wait_for_timeout(1950)
                playing_state=snap()
                new_slider=page.locator('[data-lesson-control="seek"]').input_value()
                check(playing_state['timeSec']>.85,tag+': 自动播放真实推进时间')
                check(float(new_slider)>float(start_slider),tag+': 进度条播放时自动跟随')
                page.evaluate('window.__lessonQA.pause()')
                paused=snap()
                page.wait_for_timeout(420)
                check(abs(snap()['timeSec']-paused['timeSec'])<.05,tag+': 暂停后时间不漂移')
                page.evaluate('window.__lessonQA.play()')
                page.wait_for_timeout(360)
                page.evaluate('window.__lessonQA.pause()')
                check(snap()['timeSec']>paused['timeSec']+.15,tag+': 从暂停位置可继续播放')
                check(not errors,tag+': 无未捕获 JavaScript 异常'+(' / '+str(errors[:2]) if errors else ''))
                # frame-rate is device dependent; report without asserting a fixed FPS in CI.
                check(page.locator('canvas, svg').count()>0,tag+': 数学绘图区存在')
                overflow=page.evaluate('document.documentElement.scrollWidth-innerWidth')
                check(overflow<=8,tag+': 没有明显水平溢出')
            except Exception as e:
                check(False,tag+': 浏览器测试中断：'+str(e))
            finally:
                context.close()
        browser.close()
    print('\n总体结果：'+('不合格（必须整改）' if failures else '浏览器行为测试通过；仍需数学人工复核和真实视觉验收'))
    if failures:print('未通过项目：\n'+'\n'.join(' - '+x for x in failures))
    return 1 if failures else 0

if __name__=='__main__':sys.exit(main())