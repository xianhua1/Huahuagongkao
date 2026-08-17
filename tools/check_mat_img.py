# -*- coding: utf-8 -*-
"""检查 exam_material 里的图片引用 + 有图但引用在其他字段的题"""
import os, re, subprocess

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'

def run(sql):
    return subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi', '-e', sql],
                          capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

# 1) material 中图片引用
rows = run("SELECT p.paper_code, m.content FROM exam_material m JOIN exam_paper p ON p.id=m.paper_id")
mat_refs = set()
mat_total = 0
for line in rows.splitlines():
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    code, content = parts[0], parts[1]
    refs = re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', content)
    if refs:
        mat_total += 1
        mat_refs.update(refs)
print('material 中含图:', mat_total, '条 | 唯一引用:', len(mat_refs))

missing = []
for code, name in sorted(mat_refs):
    if not os.path.exists(os.path.join(r'C:\Users\admin\DSH\data\images', code, name)):
        missing.append((code, name))
print('material 引用文件缺失:', len(missing), missing[:10])
print()

# 2) 前端做题页读取的字段：exam_question 里 stem/options/analysis + material
#    检查 options 里是否有图片
rows2 = run("SELECT p.paper_code, q.id, q.options FROM exam_question q JOIN exam_paper p ON p.id=q.paper_id WHERE q.options LIKE '%img%'")
opt_refs = set()
opt_count = 0
for line in rows2.splitlines():
    parts = line.split('\t')
    if len(parts) < 3:
        continue
    code, qid, opts = parts[0], parts[1], parts[2]
    refs = re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', opts)
    if refs:
        opt_count += 1
        opt_refs.update(refs)
print('options 含图题数:', opt_count, '| 唯一引用:', len(opt_refs))
missing2 = []
for code, name in sorted(opt_refs):
    if not os.path.exists(os.path.join(r'C:\Users\admin\DSH\data\images', code, name)):
        missing2.append((code, name))
print('options 引用文件缺失:', len(missing2), missing2[:10])
print()

# 3) 前端显示时可能找不到的卷：DB exam_paper.paper_code vs images 目录
rows3 = run("SELECT paper_code FROM exam_paper")
db_codes = set(rows3.split())
img_dirs = set(os.listdir(r'C:\Users\admin\DSH\data\images'))
no_dir = db_codes - img_dirs
extra_dir = img_dirs - db_codes
print('DB 卷数:', len(db_codes), '| images 目录数:', len(img_dirs))
print('DB 有但无目录:', len(no_dir), list(no_dir)[:10])
print('目录有但 DB 无:', len(extra_dir), list(extra_dir)[:10])
