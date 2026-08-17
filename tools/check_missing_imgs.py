# -*- coding: utf-8 -*-
"""统计缺失的题目图片文件"""
import re, os, subprocess

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
IMG_ROOT = r'C:\Users\admin\DSH\data\images'

rows = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi',
                       '-e', "SELECT stem, analysis FROM exam_question WHERE has_image=1"],
                      capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

refs = set()
for line in rows.splitlines():
    if not line.strip():
        continue
    parts = line.split('\t')
    for p in parts:
        refs.update(re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', p))

missing = []
for code, name in sorted(refs):
    p = os.path.join(IMG_ROOT, code, name)
    if not os.path.exists(p):
        missing.append((code, name))
print('图片引用总数:', len(refs), '| 缺失:', len(missing))
for c, n in missing[:30]:
    print(' ', c, n)
