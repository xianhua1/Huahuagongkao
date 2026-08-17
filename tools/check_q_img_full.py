# -*- coding: utf-8 -*-
"""全面检查题目与图片对应关系：
1) has_image=1 但 stem/analysis 无 /exam-img/ 引用的题
2) 有 /exam-img/ 引用但 has_image=0 的题
3) 引用路径 vs 实际文件（含相对/绝对路径、大小写）
4) 前端 URL 形态：/exam-img/... 的卷目录/文件是否存在
"""
import os, re, subprocess, sys

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
IMG_DIR = r'C:\Users\admin\DSH\data\images'

def run(sql):
    return subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi', '-e', sql],
                          capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

# 1) has_image=1 的题总数，以及其中无 /exam-img/ 引用的
rows = run("SELECT id, paper_id, has_image, stem, analysis FROM exam_question")
total = 0
flag_no_ref = []
ref_counts = {}
for line in rows.splitlines():
    parts = line.split('\t')
    if len(parts) < 5:
        continue
    qid, pid, has_img, stem, analysis = parts[0], parts[1], parts[2], parts[3], parts[4]
    refs = re.findall(r'/exam-img/[A-Za-z0-9\-]+/[A-Za-z0-9_\-\.]+', stem + analysis)
    if has_img == '1':
        total += 1
        if not refs:
            flag_no_ref.append(qid)
    else:
        if refs:
            ref_counts.setdefault('has0_with_ref', 0)
            ref_counts['has0_with_ref'] += 1
    ref_counts.setdefault('total_refs', 0)
    ref_counts['total_refs'] += len(refs)

print('总题数(含stem+analysis):', len(rows.splitlines()))
print('has_image=1 的题:', total)
print('has_image=1 但无 /exam-img/ 引用:', len(flag_no_ref), '->', flag_no_ref[:10])
print('has_image=0 但有 /exam-img/ 引用:', ref_counts.get('has0_with_ref', 0))
print()

# 2) 所有 /exam-img/ 引用：文件是否存在
rows2 = run("SELECT stem, analysis FROM exam_question WHERE has_image=1")
refs = set()
for line in rows2.splitlines():
    for p in line.split('\t'):
        refs.update(re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', p))
print('唯一 /exam-img/ 引用:', len(refs))
missing = {}
for code, name in sorted(refs):
    p = os.path.join(IMG_DIR, code, name)
    if not os.path.exists(p):
        missing.setdefault(code, []).append(name)
print('文件缺失引用:', sum(len(v) for v in missing.values()), '张 | 卷:', len(missing))
for code, names in sorted(missing.items())[:10]:
    print('  ', code, len(names), names[:5])
print()

# 3) 引用中的卷目录在 images 下存在吗（即使文件缺失）
dirs = set(c for c, n in refs)
missing_dirs = [c for c in dirs if not os.path.isdir(os.path.join(IMG_DIR, c))]
print('引用卷目录数:', len(dirs), '| 目录不存在:', len(missing_dirs), missing_dirs[:10])
