# 导出申论全量数据为 SQL（爬取完成后生成备份入库文件）
import subprocess, os, sys, datetime

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
OUT = r'C:\Users\admin\DSH\data\sql\shenlun_data_full.sql'

def run(sql):
    p = subprocess.run([MYSQL, '-uroot', '-p123456', '--default-character-set=utf8mb4', 'ruoyi', '-N', '-B', '-e', sql],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode != 0:
        print('ERR:', p.stderr[:500])
        return None
    return p.stdout

def q(s):
    return "'" + str(s).replace('\\', '\\\\').replace("'", "''") + "'"

print('reading tables...')
papers = run('SELECT id, paper_code, title, version, year, question_count FROM shenlun_paper ORDER BY id')
materials = run('SELECT id, paper_id, m_no, title, content FROM shenlun_material ORDER BY id')
questions = run('SELECT id, paper_id, qno, title, score, word_limit, ref_answer FROM shenlun_question ORDER BY id')

if papers is None or materials is None or questions is None:
    print('FAILED to read')
    sys.exit(1)

rows_p = papers.strip().splitlines()
rows_m = materials.strip().splitlines()
rows_q = questions.strip().splitlines()
print(f'papers={len(rows_p)} materials={len(rows_m)} questions={len(rows_q)}')

lines = []
lines.append('-- 申论题库全量数据（saduck 爬取）导出时间 ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
lines.append('SET NAMES utf8mb4;')
lines.append('')

if rows_p:
    lines.append('INSERT INTO shenlun_paper (id, paper_code, title, version, year, question_count) VALUES')
    vals = []
    for r in rows_p:
        c = r.split('\t')
        while len(c) < 6:
            c.append('')
        vals.append('(%s,%s,%s,%s,%s,%s)' % (q(c[0]), q(c[1]), q(c[2]), q(c[3]), q(c[4]), q(c[5])))
    lines.append(',\n'.join(vals) + ';')
    lines.append('')

if rows_m:
    lines.append('INSERT INTO shenlun_material (id, paper_id, m_no, title, content) VALUES')
    vals = []
    for r in rows_m:
        c = r.split('\t')
        while len(c) < 5:
            c.append('')
        vals.append('(%s,%s,%s,%s,%s)' % (q(c[0]), q(c[1]), q(c[2]), q(c[3]), q(c[4])))
    lines.append(',\n'.join(vals) + ';')
    lines.append('')

if rows_q:
    lines.append('INSERT INTO shenlun_question (id, paper_id, qno, title, score, word_limit, ref_answer) VALUES')
    vals = []
    for r in rows_q:
        c = r.split('\t')
        while len(c) < 7:
            c.append('')
        vals.append('(%s,%s,%s,%s,%s,%s,%s)' % (q(c[0]), q(c[1]), q(c[2]), q(c[3]), q(c[4]), q(c[5]), q(c[6])))
    lines.append(',\n'.join(vals) + ';')
    lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('WROTE', OUT, round(os.path.getsize(OUT) / 1024 / 1024, 2), 'MB')
