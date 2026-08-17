# -*- coding: utf-8 -*-
"""全面检查申论表（material/question/ref_answer）的图片引用 vs 文件"""
import os, re, subprocess

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
IMG_DIR = r'C:\Users\admin\DSH\data\images'

def run(sql):
    return subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi', '-e', sql],
                          capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

# 收集所有申论图片引用（material.content + question.title + ref_answer）
refs = set()
for sql in [
    "SELECT content FROM shenlun_material",
    "SELECT title FROM shenlun_question",
    "SELECT ref_answer FROM shenlun_question"
]:
    rows = run(sql)
    for line in rows.splitlines():
        refs.update(re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', line))

print('申论唯一图片引用:', len(refs))
missing = {}
for code, name in sorted(refs):
    if not os.path.exists(os.path.join(IMG_DIR, code, name)):
        missing.setdefault(code, []).append(name)
print('申论图片缺失:', sum(len(v) for v in missing.values()), '张 | 卷:', len(missing))
for code, names in sorted(missing.items())[:15]:
    print('  ', code, len(names), names[:8])

# 也检查申论引用是否指向非 sl- 目录（异常路径）
non_sl = [c for c, n in refs if not c.startswith('sl-')]
print()
print('申论引用非 sl- 前缀的卷:', len(set(non_sl)), list(set(non_sl))[:10])
