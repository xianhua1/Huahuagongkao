# -*- coding: utf-8 -*-
"""检查 material 缺失图片的卷，并验证申论卷图片（sl-* 目录）引用情况"""
import os, re, subprocess

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
IMG_DIR = r'C:\Users\admin\DSH\data\images'

def run(sql):
    return subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi', '-e', sql],
                          capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

# 1) 缺失的 9 张：确认是哪个卷的 material，并检查该卷是否在 DB
miss = [('2026-ah-fy', 'img20.png'), ('2026-cq-fy', 'img24.png'), ('2026-hb-fy', 'img26.png'),
        ('2026-he-fy', 'img18.png'), ('2026-hn-fy', 'img20.png'), ('2026-jx-fy', 'img17.png'),
        ('2026-qh-fy', 'img18.png'), ('2026-sn-fy', 'img21.png'), ('2026-sx-fy', 'img21.png')]
for code, name in miss:
    p = os.path.join(IMG_DIR, code, name)
    exists = os.path.exists(p)
    nfiles = len(os.listdir(os.path.join(IMG_DIR, code))) if os.path.isdir(os.path.join(IMG_DIR, code)) else 0
    print(f'{code}/{name}: 存在={exists} 目录文件数={nfiles}')

print()
# 这些卷 material 里的图片引用总数（哪些引用了但缺）
rows = run("SELECT p.paper_code, m.content FROM exam_material m JOIN exam_paper p ON p.id=m.paper_id WHERE p.paper_code IN ('2026-ah-fy','2026-cq-fy','2026-hb-fy','2026-he-fy','2026-hn-fy','2026-jx-fy','2026-qh-fy','2026-sn-fy','2026-sx-fy')")
for line in rows.splitlines():
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    code, content = parts[0], parts[1]
    refs = sorted(set(re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', content)))
    missing = [r for r in refs if not os.path.exists(os.path.join(IMG_DIR, r[0], r[1]))]
    if missing:
        print(code, '引用', len(refs), '缺', len(missing), ':', [m[1] for m in missing])

print()
# 2) 申论卷目录 sl-* 的图片：shenlun_material 里有 img 引用吗
rows2 = run("SELECT p.paper_code, COUNT(*) FROM shenlun_material m JOIN shenlun_paper p ON p.id=m.paper_id WHERE m.content LIKE '%<img%' GROUP BY p.paper_code LIMIT 20")
print('申论 material 含 img 的卷:')
print(rows2[:1000] if rows2 else '(无)')

# 申论 question/answer 里呢
rows3 = run("SELECT COUNT(*) FROM shenlun_question WHERE title LIKE '%<img%' OR ref_answer LIKE '%<img%'")
print('申论题目含 img:', rows3.strip())
