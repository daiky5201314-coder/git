#!/usr/bin/env python3
"""Dependency-free structural/offline checker for a delivered single-file HTML lesson.
Usage: python scripts/check_html.py /path/to/lesson.html
This is a static check, NOT a mathematics, animation or browser correctness proof.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

class HTMLAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags=[];self.script_inline=0;self.js_external=[];self.css_inline=0
        self.remote_resources=[];self.dom_controls=0;self.main_graphics=0
    def handle_starttag(self, tag, attrs):
        d=dict(attrs);self.tags.append(tag)
        for key in ('src','poster','data','background'):
            if key in d and re.match(r'^\s*(?:https?:)?//',d[key] or '',re.I):
                self.remote_resources.append(f'<{tag} {key}="{d[key]}">')
        if tag=='script':
            if d.get('src'):self.js_external.append(d['src'])
            else:self.script_inline+=1
        if tag=='style':self.css_inline+=1
        if tag=='link' and d.get('rel','').lower() in ('stylesheet','preload','modulepreload') and d.get('href'):
            self.remote_resources.append(f'<link rel={d.get("rel")} href={d["href"]}>')
        if tag=='iframe' and d.get('src'):self.remote_resources.append(f'<iframe src={d["src"]}>')
        if tag in ('canvas','svg'):self.main_graphics+=1
        if tag in ('button','input','select'):self.dom_controls+=1

def audit(file):
    s=file.read_text(encoding='utf-8-sig');p=HTMLAudit();p.feed(s)
    errors=[];warnings=[]
    if not s.lstrip().lower().startswith('<!doctype html'):
        warnings.append('Missing doctype declaration')
    if not all(x in p.tags for x in ('html','head','body')): errors.append('HTML structure missing html/head/body')
    if p.script_inline==0:errors.append('No inline JS: not self-contained or not interactive')
    if p.css_inline==0:errors.append('No inline CSS: styling may be missing')
    if p.js_external:errors.append('External <script src>: '+', '.join(p.js_external))
    if p.remote_resources:errors.append('Remote or external runtime assets: '+'; '.join(p.remote_resources))
    if re.search(r'@import\s+(?:url\s*\()?\s*[\'\"]?(?:https?:)?//',s,re.I):errors.append('Remote CSS @import')
    if re.search(r'url\s*\(\s*[\'\"]?(?:https?:)?//',s,re.I):errors.append('Remote resource in CSS url()')
    if re.search(r'\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(',s):warnings.append('Contains network API call; manual audit needed')
    if p.main_graphics==0:warnings.append('No canvas/svg found (may be valid for other visualizations)')
    if p.dom_controls==0:warnings.append('No native buttons/inputs/selects detected')
    if 'requestAnimationFrame' not in s:warnings.append('No requestAnimationFrame detected: check real animation timing')
    if not re.search(r'自动演示|播放演示|播放动画|play',s,re.I):warnings.append('No explicit auto-demo label detected')
    if not ('暂停' in s or 'pause' in s.lower()):warnings.append('No pause handling detected')
    if '<script type="module"' in s or "<script type='module'" in s:warnings.append('Inline ES module used; verify file:// browser compatibility')
    print(f'File: {file}\nBytes: {file.stat().st_size}\nInline JS: {p.script_inline}, inline CSS: {p.css_inline}, graphics: {p.main_graphics}, controls: {p.dom_controls}')
    for item in errors:print('ERROR:',item)
    for item in warnings:print('WARN:',item)
    print('STATIC RESULT:', 'FAIL' if errors else 'PASS (not a substitute for browser or mathematics testing)')
    return 1 if errors else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('file',type=Path);args=parser.parse_args()
    if not args.file.exists():print('ERROR: file does not exist',file=sys.stderr);sys.exit(2)
    sys.exit(audit(args.file))