# -*- coding: utf-8 -*-
"""抓词语辨析数据 + 尝试解密高频词语"""
import urllib.request, json, base64, re
from Crypto.Cipher import AES

TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'

def post(url, body, extra=None):
    h = {'Content-Type': 'application/json', 'Referer': 'https://www.saduck.top/', 'User-Agent': 'Mozilla/5.0'}
    if extra: h.update(extra)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())

# 1) 词语辨析数据
r = post('https://saduck.top/api/analyze/getBxCy', {}, {'token': TOKEN})
print('辨析 code:', r.get('code'), '| result 类型:', type(r.get('result')).__name__)
res = r.get('result')
s = res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
print('长度:', len(s))
print(s[:800])
if s and s != 'null':
    open(r'C:\Users\admin\DSH\data\saduck_bxcy.json', 'w', encoding='utf-8').write(s)

# 2) 高频词语解密尝试
raw = open(r'C:\Users\admin\DSH\data\saduck_hword_raw.txt', encoding='utf-8').read()
d = json.loads(raw)
hw = d['result']['hword']
print('\nhword 长度:', len(hw))
keys = ['kxZ17XQ8z6957n3S', '7SyqrN6925ZYb636']
for k in keys:
    try:
        t = hw.replace('-', '+').replace('_', '/')
        t += '=' * (-len(t) % 4)
        pt = AES.new(k.encode(), AES.MODE_ECB).decrypt(base64.b64decode(t))
        plain = pt[: -pt[-1]].decode('utf-8')
        print('密钥', k, '解密成功, 前200:', plain[:200])
        open(r'C:\Users\admin\DSH\data\saduck_hword.json', 'w', encoding='utf-8').write(plain)
        break
    except Exception as e:
        print('密钥', k, '失败:', str(e)[:60])
