# -*- coding: utf-8 -*-
"""深入侦察 saduck 题目数据源"""
import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}

def get(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=timeout, context=ctx).read()

html = get('https://www.saduck.top/questionBank/overTheYears.html').decode('utf-8', 'ignore')

# 1) 页面里是否有真题内容特征
for kw in ['作答要求', '给定资料', '材料一', '单选题', '参考答案', '解析']:
    print(kw, ':', html.count(kw))

# 2) 引用哪些 JS chunk
js = re.findall(r'src="(/assets/[^"]+\.js)"', html)
print('JS chunks:', js[:8])

# 3) 页面是否引用了数据文件（json/md）
datas = re.findall(r'["\']([^"\']+\.(?:json|md))["\']', html)
print('数据文件引用:', datas[:10])

# 4) 抓取第一个 JS 找 API 端点线索
if js:
    try:
        code = get('https://www.saduck.top' + js[0]).decode('utf-8', 'ignore')
        endpoints = re.findall(r'["\'](/[a-zA-Z0-9_\-/]{3,60}(?:json|api|data|md)[a-zA-Z0-9_\-/\.]*)["\']', code)
        print('JS内端点:', list(dict.fromkeys(endpoints))[:15])
    except Exception as e:
        print('JS 抓取失败:', e)
