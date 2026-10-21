#!/usr/bin/env python3
"""V3 视觉与教学交互契约测试：对新成品进行 DOM 结构/知识卡动态内容/导航行为/响应布局检查。

不能取代真人观看、数学证明复核或参考画面对比；这是最低门槛测试。

Usage: python scripts/visual_teaching_contract_test.py new_lesson.html --shots ./visualQA
Requires: playwright + Chromium.
"""
import argparse
import sys
import shutil
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright

PCTS = [0.04, .21, .42, .67, .84, .97]
ROLES = ['step-title','objective','why','derivation','conclusion','reflection']
REGIONS = ['stage','teaching-side','chapter-nav','teaching-card','controls']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html')
    parser.add_argument('--shots', default='visualQA')
    args=parser.parse_args()
    path=Path(args.html).resolve(); output=Path(args.shots).resolve(); output.mkdir(parents=True,exist_ok=True)
    if not path.is_file(): print('ERROR file does not exist'); return 2
    failures=[]; notes=[]
    def ck(ok, text):
        print(('PASS ' if ok else 'FAIL ')+text)
        if not ok: failures.append(text)
    def log(note):
        print('INFO '+note)
        notes.append(note)
    with sync_playwright() as p:
        cb=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('chromium-browser')
        try:
            browser=p.chromium.launch(headless=True, executable_path=cb, args=['--no-sandbox','--disable-gpu-sandbox'])
        except Exception as err:
            print('BLOCKED: 无法启动 Chromium；不能宣称完成浏览器验收。',err)
            return 3
        for width,height,device in [(1440,900,'desktop'),(390,844,'mobile')]:
            context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,offline=True)
            page=context.new_page(); errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            try:
                try:page.goto(path.as_uri(),wait_until='load',timeout=20000)
                except Exception as e:
                    if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(e): raise
                    page.close()
                    page=context.new_page()
                    page.on('pageerror',lambda exc:errors.append(str(exc)))
                    page.set_content(path.read_text(encoding='utf-8-sig'),wait_until='load',timeout=20000)
                    log(device+': file:// 被环境阻断，改用同 HTML 字节内容加载（未验证双击）')
                page.wait_for_timeout(180)
                present={s:page.locator(f'[data-lesson-region="{s}"]').count()>0 for s in REGIONS}
                for s,yes in present.items(): ck(yes,device+': 结构区域 '+s)
                role_present={s:page.locator(f'[data-lesson-role="{s}"]').count()>0 for s in ROLES}
                for s,yes in role_present.items(): ck(yes,device+': 教学语义 '+s)
                if not all(present.values()) or not all(role_present.values()):
                    log(device+': 缺失 V3 语义角色，剩余检查尽可能继续，不能评为合格')
                if not page.evaluate('typeof window.__lessonQA?.getSnapshot==="function" && typeof window.__lessonQA?.seek==="function"'):
                    ck(False,device+': 缺少工程状态 QA 接口，无法验证图文同源')
                    continue
                dur=page.evaluate('window.__lessonQA.getSnapshot().durationSec')
                texts={r:set() for r in ROLES}
                keyframes=[]
                for frac in PCTS:
                    page.evaluate('(t)=>window.__lessonQA.seek(t)',float(dur)*frac)
                    page.wait_for_timeout(75)
                    obj=page.evaluate('''(roles)=>{
                       const visible=el=>{ if(!el)return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
                       const read=role=>{const els=[...document.querySelectorAll(`[data-lesson-role="${role}"]`)];return els.filter(visible).map(x=>x.innerText.trim()).join(' ');};
                       return Object.fromEntries(roles.map(r=>[r,read(r)]));
                    }''', ROLES)
                    for r,val in obj.items():
                        if val: texts[r].add(val)
                    keyframes.append(obj)
                    page.screenshot(path=str(output/f'{device}_{round(frac*100):02d}.png'),full_page=False)
                for r in ['step-title','objective','why','derivation']:
                    ck(len(texts[r])>=2,device+': '+r+' 随教学步骤真实更新')
                ck(max([len(x) for x in texts['why']] or [0])>=12,device+': 学生能读到“为什么这样做”')
                ck(max([len(x) for x in texts['derivation']] or [0])>=24,device+': 当步有可见、非一句话的推导内容')
                ck(any(len(x)>=5 for x in texts['conclusion']),device+': 有可见的阶段结论')
                ck(any(len(x)>=8 for x in texts['reflection']),device+': 有可见的提问/提示/反思')
                if present.get('stage') and present.get('teaching-side'):
                    layout=page.evaluate('''()=>{const a=document.querySelector('[data-lesson-region="stage"]').getBoundingClientRect();const b=document.querySelector('[data-lesson-region="teaching-side"]').getBoundingClientRect();return {stage:{x:a.x,y:a.y,w:a.width,h:a.height},side:{x:b.x,y:b.y,w:b.width,h:b.height},overflow:document.documentElement.scrollWidth-innerWidth};}''')
                    ck(layout['stage']['h']>= (270 if device=='desktop' else 190),device+': 主数学舞台具有足够高度')
                    ck(layout['stage']['w']>=width*(.40 if device=='desktop' else .80),device+': 数学舞台不是狭小角落')
                    ck(layout['side']['w']>=width*(.20 if device=='desktop' else .80),device+': 完整教学卡片区域可读')
                    ck((layout['side']['x']>layout['stage']['x']+layout['stage']['w']*.64) if device=='desktop' else (layout['side']['y']>=layout['stage']['y']+layout['stage']['h']-8), device+': 主舞台/教学侧栏布局符合目标')
                    ck(layout['overflow']<=8,device+': 无页面横向溢出')
                nav=page.locator('[data-lesson-chapter]')
                ck(nav.count()>=4,device+': 教学章节导航不少于4个真实入口')
                if nav.count()>=4:
                    page.evaluate('window.__lessonQA.seek(0)')
                    before=page.evaluate('window.__lessonQA.getSnapshot().timeSec')
                    nav.nth(2).click(timeout=2500)
                    page.wait_for_timeout(100)
                    after=page.evaluate('window.__lessonQA.getSnapshot().timeSec')
                    ck(abs(after-before)>.5,device+': 点击导航真正改变共享播放头')
                    active=page.locator('[data-lesson-chapter][aria-current="step"], [data-lesson-chapter].active, [data-lesson-chapter].current, [data-lesson-chapter][data-active="true"]')
                    ck(active.count()>0,device+': 导航有当前章节视觉/语义状态')
                ck(not errors,device+': 浏览器无 JavaScript 未捕获异常'+(' '+str(errors[:2]) if errors else ''))
            except Exception as e:
                ck(False,device+': 测试意外中断 '+str(e))
            finally: context.close()
        browser.close()
    print('\nV3 可执行教学视觉契约：'+('FAIL, 必须整改' if failures else 'PASS（仅最低门槛；还需参考截图对比+数学审校+真人教学审片）'))
    if failures:
        print('未通过项：\n'+'\n'.join('- '+x for x in failures))
        return 1
    return 0
if __name__=='__main__':sys.exit(main())