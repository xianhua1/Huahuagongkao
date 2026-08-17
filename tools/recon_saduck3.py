# -*- coding: utf-8 -*-
"""抓取 saduck API 结构"""
import urllib.request, ssl, json, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}

def get(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=timeout, context=ctx).read()

# 1) 试卷列表
try:
    raw = get('https://saduck.top/api/tk/itemizes?type=1').decode('utf-8', 'ignore')
    print('itemizes 返回长度:', len(raw))
    print(raw[:600])
except Exception as e:
    print('itemizes 失败:', e)
