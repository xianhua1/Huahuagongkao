# -*- coding: utf-8 -*-
"""补爬缺失图片的卷：删库 → 重爬（import crawl_all 的函数）"""
import os, re, subprocess, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawl_all import (TOKEN, KEY_LIST, KEY_ENC, IMG_DIR, MYSQL, crawl_paper, import_sql, aes_decrypt, post, code_of)

# 1) 缺失图片的卷 code
rows = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi',
                       '-e', "SELECT stem, analysis FROM exam_question WHERE has_image=1"],
                      capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
refs = set()
for line in rows.splitlines():
    if not line.strip():
        continue
    for p in line.split('\t'):
        refs.update(re.findall(r'/exam-img/([A-Za-z0-9\-]+)/([A-Za-z0-9_\-\.]+)', p))
missing_codes = {}
for code, name in sorted(refs):
    if not os.path.exists(os.path.join(IMG_DIR, code, name)):
        missing_codes.setdefault(code, []).append(name)
print('缺失图片卷数:', len(missing_codes), '| 缺失图:', sum(len(v) for v in missing_codes.values()))

# 2) 清单
r = post('https://saduck.top/api/tk/itemizes?type=1', {})
data = json.loads(aes_decrypt(r['result'], KEY_LIST))
jobs = {}
for g in data:
    cat = g.get('title')
    for s in g.get('tkSources', []):
        m = re.search(r'(20\d{2})', s.get('source', ''))
        year = m.group(1) if m else '2000'
        code = code_of(s['source'], year, cat)
        try:
            model = json.loads(s.get('model') or '[]')
        except Exception:
            model = []
        jobs[code] = (s['sid'], s['source'], cat, model)

ok = 0
fail = []
for code, missing in missing_codes.items():
    if code not in jobs:
        fail.append(code + ' (清单无匹配)')
        continue
    sid, source, cat, model = jobs[code]
    # 删库重爬
    subprocess.run([MYSQL, '-u', 'root', '-p123456', '--default-character-set=utf8mb4', 'ruoyi',
                    '-e', "DELETE q FROM exam_question q JOIN exam_paper p ON p.id=q.paper_id WHERE p.paper_code='%s'; DELETE m FROM exam_material m JOIN exam_paper p ON p.id=m.paper_id WHERE p.paper_code='%s'; DELETE FROM exam_paper WHERE paper_code='%s';" % (code, code, code)],
                   capture_output=True, text=True)
    # 清掉旧图片目录
    imgdir = os.path.join(IMG_DIR, code)
    if os.path.isdir(imgdir):
        for f in os.listdir(imgdir):
            os.remove(os.path.join(imgdir, f))
    try:
        res = crawl_paper(sid, source, cat, model)
        if res is None:
            fail.append(source)
            continue
        sql, nq, nm, ni, nf = res
        if import_sql(sql):
            ok += 1
            print('OK %s | %d题 %d图(失败%d)' % (source, nq, ni, nf))
        else:
            fail.append(source + ' (导入失败)')
    except Exception as e:
        fail.append(source + ' (' + str(e)[:60] + ')')
        print('异常', source, str(e)[:80])
    time.sleep(0.5)

print('\n补爬完成: 成功 %d, 失败 %d' % (ok, len(fail)))
for f in fail:
    print(' FAIL:', f)
