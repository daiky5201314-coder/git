#!/usr/bin/env python3
"""Offline HTML5 structural/engineering preflight for math lessons.
Usage: python scripts/validate_delivery.py <file.html>
Fails closed for incomplete deliverables; browser tests are still required.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from html.parser import HTMLParser

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

def main(path: str) -> int:
    p=Path(path)
    if not p.is_file():
        print('FAIL: 找不到文件:',path);return 2
    source=p.read_text(encoding='utf-8-sig')
    z=Inspect();z.feed(source)
    elems=z.elements
    errors=[];warnings=[]
    def demand(ok,msg):
        if not ok:errors.append(msg)
    demand(bool(re.search(r'(?is)^\s*<!doctype\s+html\s*>',source)),'缺少标准 <!doctype html>')
    demand(any(t=='html' and a.get('lang') for t,a in elems),'html 缺少 lang="zh-CN"')
    demand(any(t=='meta' and (a.get('charset') or '').lower()=='utf-8' for t,a in elems),'缺少 UTF-8 meta charset')
    demand(any(t=='meta' and a.get('name')=='viewport' for t,a in elems),'缺少 viewport')
    demand('<title>' in source.lower(),'缺少 title')
    for tag in ('header','main','section','aside','button','script','style'):
        demand(any(t==tag for t,_ in elems),f'缺少语义结构或交互元素: <{tag}>')
    canvas=any(t in ('canvas','svg') for t,a in elems)
    demand(canvas,'没有 Canvas 或 SVG 交互绘制区域')
    demand('requestAnimationFrame' in source,'没有浏览器动画帧驱动')
    demand('__lessonQA' in source,'缺少 window.__lessonQA 可测试契约接口')
    demand('sceneAt' in source and 'applyTime' in source,'缺少标准 sceneAt/applyTime 同一状态管线')
    for t,a in elems:
        if t=='script' and a.get('src'):errors.append('外部脚本，不满足离线单文件: '+a['src'])
        if t=='link' and a.get('rel','').lower() in ('stylesheet','modulepreload'):
            errors.append('外部 CSS/依赖，不满足离线单文件: '+str(a.get('href')))
        if t in ('iframe','object','embed') and a.get('src'):errors.append('外部嵌入资源: '+str(a.get('src')))
        if t in ('img','video','audio','source') and any(str(a.get(k,'')).startswith(('http://','https://','//')) for k in ('src','srcset','poster')):
            errors.append('媒体依赖网络，未离线自包含: '+str(a.get('src','')))
        if t=='input' and a.get('type')=='range' and not (a.get('aria-label') or a.get('id')):
            warnings.append('范围控件可能缺少关联标签')
    for action in ('play','seek','speed'):
        demand(any(a.get('data-lesson-control')==action for t,a in elems),f'缺少测试标记 data-lesson-control="{action}"')
    if re.search(r'url\s*\(\s*[\"\']?(?:https?:)?//',source,re.I):errors.append('CSS 依赖远程 URL')
    if 'setInterval(' in source:warnings.append('发现 setInterval：不要用它驱动主动画时间')
    # A successful static preflight does not imply mathematically correct or glitch-free animation.
    print(f'静态工程预检：{p.name}')
    for x in errors: print('FAIL:',x)
    for x in warnings: print('WARN:',x)
    if errors:print(f'结果：失败，{len(errors)} 个硬性问题');return 1
    print('结果：静态检查通过；还必须运行浏览器契约测试和人工数学核验。')
    return 0

if __name__=='__main__':
    if len(sys.argv)!=2:print('Usage: python validate_delivery.py <file.html>');sys.exit(2)
    sys.exit(main(sys.argv[1]))