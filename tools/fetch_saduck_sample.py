# -*- coding: utf-8 -*-
"""抓取 2022 副省行测题目样本（sid=19515）"""
import urllib.request, json, base64, re

TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'

def post(url, body, headers=None):
    h = {'Content-Type': 'application/json', 'Referer': 'https://www.saduck.top/', 'User-Agent': 'Mozilla/5.0'}
    if headers: h.update(headers)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())

r = post('https://saduck.top/api/tk/sourceInfo', {'id': 19515}, {'token': TOKEN})
print('code:', r.get('code'), '| message:', r.get('message'))
res = r.get('result')
if res is None:
    print('无 result')
else:
    print('result 类型:', type(res).__name__, '长度:', len(res) if isinstance(res, str) else '?')
    s = res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
    open(r'C:\Users\admin\DSH\data\saduck_sample_raw.json', 'w', encoding='utf-8').write(s)
    print('前 800 字符:')
    print(s[:800])
