# -*- coding: utf-8 -*-
"""测试缺失图片的真实 URL 能否下载：查 DB 里的原始图片地址 → 直接请求"""
import os, re, subprocess, urllib.request, json

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'

# 1) 找一个缺失图片对应的题目，提取原图 URL
rows = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi',
                       '-e', "SELECT q.stem FROM exam_question q JOIN exam_paper p ON p.id=q.paper_id WHERE p.paper_code='2022-gk-xzf' AND q.stem LIKE '%img35.png%' LIMIT 1"],
                      capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
print('=== 题目 stem 片段 ===')
print(rows[:800])
print()

# 2) 提取所有外部图片 URL（fb.fenbike.cn 等）
urls = re.findall(r'https?://[^\s"\'<>]+?\.(?:png|jpg|jpeg|gif)', rows)
urls = [u.replace('&amp;', '&') for u in urls]
print('=== 提取到的图片 URL ===')
for u in urls[:5]:
    print(u)

# 3) 直接请求测试
if urls:
    u = urls[0]
    print()
    print('=== 请求测试:', u, '===')
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://www.saduck.top/'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
            print('HTTP', r.status, '| 内容长度', len(data), '| Content-Type:', r.headers.get('Content-Type'))
            print('前16字节:', data[:16].hex())
            if len(data) > 1000:
                fn = r'C:\Users\admin\DSH\data\images\2022-gk-xzf'
                os.makedirs(fn, exist_ok=True)
                with open(os.path.join(fn, 'img35.png'), 'wb') as f:
                    f.write(data)
                print('已保存 img35.png!')
    except Exception as e:
        print('请求失败:', repr(e))
        # 打印 HTTP 错误详情
        if hasattr(e, 'code'):
            print('HTTP code:', e.code)
            try:
                print('错误页内容:', e.read()[:300])
            except Exception:
                pass
