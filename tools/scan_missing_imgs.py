# -*- coding: utf-8 -*-
"""检查当前缺失图片的卷（不重爬，仅报告）"""
import os, re, subprocess, sys

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
IMG_DIR = r'C:\Users\admin\DSH\data\images'

rows = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi',
                       '-e', "SELECT stem, analysis FROM exam_question WHERE has_image=1"],
                      capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
refs = set()
for line in rows.splitlines():
    for p in line.split('\t'):
        refs.update(re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', p))
missing = {}
for code, name in sorted(refs):
    if not os.path.exists(os.path.join(IMG_DIR, code, name)):
        missing.setdefault(code, []).append(name)
print('引用的卷数:', len(set(c for c, n in refs)))
print('仍缺图卷数:', len(missing))
total_missing = sum(len(v) for v in missing.values())
print('总缺图数:', total_missing)
for code, names in sorted(missing.items()):
    print(' ', code, len(names), '张')
