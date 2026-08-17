# -*- coding: utf-8 -*-
"""诊断 v2：先列出清单里所有含 2022 国考的卷名"""
import os, sys, json, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawl_all import KEY_LIST, aes_decrypt, post

r = post('https://saduck.top/api/tk/itemizes?type=1', {})
data = json.loads(aes_decrypt(r['result'], KEY_LIST))
for g in data:
    cat = g.get('title')
    for s in g.get('tkSources', []):
        src = s.get('source', '')
        if '2022' in src and '国考' in src:
            print(cat, '|', src, '| sid:', s['sid'])
