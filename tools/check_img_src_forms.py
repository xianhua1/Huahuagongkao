# -*- coding: utf-8 -*-
"""检查题目中所有 img src 的形态：/exam-img/ 之外的引用（绝对 URL、其他路径等）"""
import os, re, subprocess

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'

def run(sql):
    return subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi', '-e', sql],
                          capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

rows = run("SELECT p.paper_code, q.id, q.stem, q.analysis FROM exam_question q JOIN exam_paper p ON p.id=q.paper_id")

other_refs = {}  # src 形态 -> [题目id]
no_img_ref = []  # has_image 无关：看看有没有 <img 但没有 src 的
for line in rows.splitlines():
    parts = line.split('\t')
    if len(parts) < 4:
        continue
    code, qid, stem, analysis = parts[0], parts[1], parts[2], parts[3]
    for html in (stem, analysis):
        for m in re.finditer(r'<img[^>]*>', html):
            tag = m.group(0)
            srcm = re.search(r'src=["\']([^"\']*)["\']', tag)
            if not srcm:
                no_img_ref.append((qid, tag[:80]))
                continue
            src = srcm.group(1)
            if not src.startswith('/exam-img/'):
                key = src[:80]
                other_refs.setdefault(key, []).append((qid, code))

print('=== 非 /exam-img/ 的 img src（含绝对URL、其他路径）===')
for k, v in sorted(other_refs.items(), key=lambda x: -len(x[1])):
    print(len(v), '处 |', k, '| 例题:', v[0])
print()
print('无 src 的 img 标签:', len(no_img_ref))
for qid, tag in no_img_ref[:5]:
    print('  qid', qid, '|', tag)
