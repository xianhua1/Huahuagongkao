# -*- coding: utf-8 -*-
"""批量爬取 saduck 申论题库 → 入库 shenlun 表"""
import urllib.request, json, re, os, sys, time, subprocess, html as htmllib

TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'
IMG_DIR = r'C:\Users\admin\DSH\data\images'
MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0', 'Referer': 'https://www.saduck.top/questionBank/slItem.html'}

def post(url, body, headers=None):
    h = dict(HDRS)
    h['Content-Type'] = 'application/json'
    if headers: h.update(headers)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())

def download(url, path):
    for i in range(5):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=30).read()
            if len(data) < 100:
                time.sleep(1.5)
                continue
            with open(path, 'wb') as f:
                f.write(data)
            return True
        except Exception:
            time.sleep(2)
    return False

def esc(s):
    return s.replace('\\', '\\\\').replace("'", "''")

def import_sql(sql):
    tmp = os.path.join(os.environ.get('TEMP', '.'), 'crawl_sl_tmp.sql')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(sql)
    p = subprocess.run([MYSQL, '-u', 'root', '-p123456', '--default-character-set=utf8mb4', 'ruoyi',
                        '-e', 'source %s' % tmp.replace('\\', '/')],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        os.remove(tmp)
    except Exception:
        pass
    if p.returncode != 0:
        print('  导入错误:', (p.stderr or '')[-200:])
    return p.returncode == 0

def crawl(sl_id, test_name, type_name):
    r = post('https://saduck.top/api/sl/getSlContextNew?id=%s' % sl_id, {}, {'token': TOKEN})
    if r.get('code') != 0:
        return None, r.get('message')
    d = r['result']
    questions = d.get('questions') or []
    materials = d.get('expandedMaterials') or []
    if not questions:
        return None, '空题目'

    m = re.search(r'(20\d{2})', test_name)
    year = m.group(1) if m else '0'
    code = 'sl-' + sl_id
    img_dir = os.path.join(IMG_DIR, code)
    os.makedirs(img_dir, exist_ok=True)
    seen = {}

    def rewrite(html):
        def rep(mt):
            tag = mt.group(0)
            srcm = re.search(r'src=["\']([^"\']+)["\']', tag)
            if not srcm:
                return tag
            src = srcm.group(1)
            src = htmllib.unescape(src)  # 解码 &amp; → &，公式图 URL 才能下载
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://saduck.top' + src
            if src not in seen:
                name = 'img%d.png' % (len(seen) + 1)
                seen[src] = name
                download(src, os.path.join(img_dir, name))
            return tag.replace(srcm.group(0), 'src="/exam-img/%s/%s"' % (code, seen[src]))
        return re.sub(r'<img[^>]*>', rep, html)

    mat_html = []
    for mm in materials:
        h = rewrite(str(mm))
        mat_html.append(re.sub(r'<p[^>]*>|</p>', '', h).replace('&emsp;', '').strip())

    qrows = []
    for idx, q in enumerate(questions, start=1):
        content = rewrite(str(q.get('content') or ''))
        require = rewrite(str(q.get('require') or ''))
        title = content + ('\n' + require if require else '')
        score_m = re.search(r'[（(]?\s*(\d{1,2})\s*分', content)
        word_m = re.search(r'(?:不超过|控制在|左右|不少于)\s*(\d{3,4})\s*字', require + content)
        # 参考答案：优先粉笔，其次华图，再第一个
        ans = ''
        for a in q.get('answers') or []:
            organ = str(a.get('organ') or '')
            if '粉笔' in organ:
                ans = a.get('answer') or ''
                break
        if not ans and (q.get('answers') or []):
            ans = q['answers'][0].get('answer') or ''
        ans = rewrite(ans)
        qrows.append({
            'qno': idx, 'title': title,
            'score': int(score_m.group(1)) if score_m else 0,
            'word_limit': int(word_m.group(1)) if word_m else 0,
            'ref_answer': ans
        })

    lines = ["SET NAMES utf8mb4;"]
    lines.append("INSERT INTO shenlun_paper (paper_code, title, year, version, question_count) VALUES ('%s', '%s', %s, '%s', %d);" % (
        code, esc(test_name), year, esc(type_name), len(qrows)))
    lines.append("SET @pid = LAST_INSERT_ID();")
    for i, mh in enumerate(mat_html):
        lines.append("INSERT INTO shenlun_material (paper_id, m_no, title, content) VALUES (@pid, %d, '材料%d', '%s');" % (i + 1, i + 1, esc(mh)))
    for q in qrows:
        lines.append("INSERT INTO shenlun_question (paper_id, qno, title, score, word_limit, ref_answer) VALUES (@pid, %d, '%s', %d, %d, '%s');" % (
            q['qno'], esc(q['title']), q['score'], q['word_limit'], esc(q['ref_answer'])))
    return '\n'.join(lines), None

def main():
    lst = json.load(open(r'C:\Users\admin\DSH\data\saduck_sl_list.json', encoding='utf-8'))
    jobs = [(s['id'], s['testName'], g['typeName']) for g in lst for s in g.get('list', [])]
    # 断点：跳过已入库
    p = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', 'ruoyi', '-e', "SELECT paper_code FROM shenlun_paper"],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    existing = set(p.stdout.split())
    jobs = [j for j in jobs if 'sl-' + j[0] not in existing]
    print('待爬申论: %d 套（已跳过 %d）' % (len(jobs), 697 - len(jobs)))

    ok = 0
    fail = []
    for i, (sl_id, name, tname) in enumerate(jobs, start=1):
        try:
            sql, err = crawl(sl_id, name, tname)
            if sql is None:
                fail.append(name + ' (' + str(err) + ')')
                print('[%d/%d] 失败 %s: %s' % (i, len(jobs), name, err))
                continue
            if import_sql(sql):
                ok += 1
                print('[%d/%d] OK %s' % (i, len(jobs), name))
            else:
                fail.append(name + ' (导入失败)')
        except Exception as e:
            fail.append(name + ' (' + str(e)[:50] + ')')
            print('[%d/%d] 异常 %s: %s' % (i, len(jobs), name, str(e)[:80]))
        time.sleep(0.3)
    print('\n申论爬取完成: 成功 %d, 失败 %d' % (ok, len(fail)))
    for f in fail[:20]:
        print(' FAIL:', f)

if __name__ == '__main__':
    main()
