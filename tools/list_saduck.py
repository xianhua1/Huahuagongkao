# -*- coding: utf-8 -*-
"""列出 saduck 全部题库清单"""
import urllib.request, json, base64
from Crypto.Cipher import AES

KEY_LIST = '7SyqrN6925ZYb636'

def aes_decrypt(enc, key):
    t = enc.replace('-', '+').replace('_', '/')
    t += '=' * (-len(t) % 4)
    pt = AES.new(key.encode(), AES.MODE_ECB).decrypt(base64.b64decode(t))
    return pt[: -pt[-1]].decode('utf-8')

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
      headers={'Content-Type': 'application/json', 'Referer': 'https://www.saduck.top/', 'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())

# type=1 行测历年试卷
r = post('https://saduck.top/api/tk/itemizes?type=1', {})
data = json.loads(aes_decrypt(r['result'], KEY_LIST))
total = 0
for g in data:
    n = len(g.get('tkSources', []))
    total += n
    print('%s: %d 套' % (g.get('title'), n))
print('行测历年总套数:', total)

# 其他 type（2=专项？3=申论？）
for t in [2, 3, 4]:
    try:
        r2 = post('https://saduck.top/api/tk/itemizes?type=%d' % t, {})
        if r2.get('code') == 0 and r2.get('result'):
            d2 = json.loads(aes_decrypt(r2['result'], KEY_LIST))
            t2 = sum(len(g.get('tkSources', [])) for g in d2)
            print('type=%d: %d 套, 分类: %s' % (t, t2, ', '.join(g.get('title', '') for g in d2)[:100]))
    except Exception as e:
        print('type=%d 失败: %s' % (t, e))
