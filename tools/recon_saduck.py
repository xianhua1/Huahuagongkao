# -*- coding: utf-8 -*-
"""侦察 saduck 题库页面结构"""
import urllib.request, ssl, re, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}

def get(url, timeout=20):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=timeout, context=ctx).read()

try:
    html = get('https://www.saduck.top/questionBank/overTheYears.html').decode('utf-8', 'ignore')
    print('页面大小:', len(html))
    print('--- 标题/框架线索 ---')
    m = re.findall(r'<title>(.*?)</title>', html, re.S)
    print('title:', m)
    # 是否 SPA（vue/react 标记）
    for marker in ['id="app"', '__INITIAL_STATE__', '__NUXT__', 'window.__DATA__', 'axios', 'vue', 'react', 'questionBank']:
        if marker in html:
            print('标记:', marker)
    # 找 API 地址线索
    apis = re.findall(r'["\'](/[a-zA-Z0-9_\-/]+(?:api|Api|API)[a-zA-Z0-9_\-/]*)["\']', html)
    print('API 线索:', apis[:10])
    # 找内嵌 JSON 数据
    jm = re.findall(r'window\.\w+\s*=\s*(\{.*?\});', html, re.S)
    print('内嵌JSON块:', len(jm))
    # 直接包含题目文本？
    if '题' in html:
        print('页面含"题"字样，样例:')
        idx = html.find('题')
        print(html[max(0, idx-100):idx+150].replace('\n', ' ')[:250])
except Exception as e:
    print('请求失败:', type(e).__name__, e)
