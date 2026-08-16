# -*- coding: utf-8 -*-
"""测试新华社评论数据源。"""
import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}

def get(url, timeout=15):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=timeout, context=ctx).read()

urls = [
    'http://www.xinhuanet.com/comment/',
    'https://www.news.cn/comment/',
    'https://www.news.cn/',
    'http://www.news.cn/',
]
for u in urls:
    try:
        raw = get(u)
        html = raw.decode('utf-8', 'ignore')
        # 提取含"新华时评/新华网评/评论"的链接
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{6,50})</a>', html)
        hits = [(t.strip(), l) for l, t in links if re.search(r'(时评|网评|评论|观点)', t)]
        print('==', u, 'len', len(html), 'comment-links', len(hits))
        for t, l in hits[:6]:
            print('   -', t, '|', l[:90])
        if not hits:
            # 随便看几个链接
            anyl = [l for l, t in links[:8] if 'news.cn' in l or 'xinhuanet.com' in l]
            print('   sample:', anyl[:4])
    except Exception as e:
        print('==', u, 'ERR', type(e).__name__, str(e)[:60])
