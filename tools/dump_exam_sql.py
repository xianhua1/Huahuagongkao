# -*- coding: utf-8 -*-
"""导出当前行测题库全量数据为 SQL（用户拉库后一键导入用）"""
import subprocess, os, sys, datetime

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
OUT = r'C:\Users\admin\DSH\data\sql\exam_data_full.sql'

def run(sql):
    p = subprocess.run([MYSQL, '-uroot', '-p123456', '--default-character-set=utf8mb4', 'ruoyi', '-N', '-B', '-e', sql],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode != 0:
        print('ERR:', p.stderr[:300])
        return None
    return p.stdout

def q(s):
    return "'" + str(s).replace('\\', '\\\\').replace("'", "''") + "'"

print('reading...')
papers = run('SELECT id, paper_code, title, year, version, subject, question_count FROM exam_paper ORDER BY id')
materials = run('SELECT id, paper_id, title, content FROM exam_material ORDER BY id')
questions = run('SELECT id, paper_id, material_id, section, qno, qorder, stem, options, answer, analysis, has_image FROM exam_question ORDER BY id')

if papers is None or materials is None or questions is None:
    sys.exit(1)

rp, rm, rq = papers.strip().splitlines(), materials.strip().splitlines(), questions.strip().splitlines()
print(f'papers={len(rp)} materials={len(rm)} questions={len(rq)}')

lines = []
lines.append('-- 行测题库全量数据导出时间 ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
lines.append('SET NAMES utf8mb4;')
lines.append('')

if rp:
    lines.append('INSERT INTO exam_paper (id, paper_code, title, year, version, subject, question_count) VALUES')
    vals = []
    for r in rp:
        c = r.split('\t')
        while len(c) < 7:
            c.append('')
        vals.append('(%s,%s,%s,%s,%s,%s,%s)' % tuple(q(x) for x in c[:7]))
    lines.append(',\n'.join(vals) + ';')
    lines.append('')

if rm:
    lines.append('INSERT INTO exam_material (id, paper_id, title, content) VALUES')
    vals = []
    for r in rm:
        c = r.split('\t')
        while len(c) < 4:
            c.append('')
        vals.append('(%s,%s,%s,%s)' % tuple(q(x) for x in c[:4]))
    lines.append(',\n'.join(vals) + ';')
    lines.append('')

if rq:
    lines.append('INSERT INTO exam_question (id, paper_id, material_id, section, qno, qorder, stem, options, answer, analysis, has_image) VALUES')
    vals = []
    for r in rq:
        c = r.split('\t')
        while len(c) < 11:
            c.append('')
        vals.append('(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % tuple(q(x) for x in c[:11]))
    lines.append(',\n'.join(vals) + ';')
    lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('WROTE', OUT, round(os.path.getsize(OUT) / 1024 / 1024, 2), 'MB')
