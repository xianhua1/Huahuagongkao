# -*- coding: utf-8 -*-
"""批量爬取 saduck 全部行测卷 → 图片落地 → SQL → 自动导入 MySQL
用法: python crawl_all.py
"""
import urllib.request, json, base64, re, os, sys, time, html as htmllib
from concurrent.futures import ThreadPoolExecutor
from Crypto.Cipher import AES

TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'
KEY_LIST = '7SyqrN6925ZYb636'
KEY_ENC = 'kxZ17XQ8z6957n3S'

IMG_DIR = r'C:\Users\admin\DSH\data\images'
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0', 'Referer': 'https://www.saduck.top/'}
MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
SECTION_MAP = {'政治理论': '常识判断', '言语理解': '言语理解与表达'}

def aes_decrypt(enc, key):
    t = enc.replace('-', '+').replace('_', '/')
    t += '=' * (-len(t) % 4)
    pt = AES.new(key.encode(), AES.MODE_ECB).decrypt(base64.b64decode(t))
    return pt[: -pt[-1]].decode('utf-8')

def aes_encrypt(plain, key):
    c = AES.new(key.encode(), AES.MODE_ECB)
    pt = plain.encode()
    pad = 16 - len(pt) % 16
    pt += bytes([pad]) * pad
    return base64.b64encode(c.encrypt(pt)).decode()

def post(url, body, headers=None):
    h = dict(HDRS)
    h['Content-Type'] = 'application/json'
    if headers: h.update(headers)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())

def download(url, path):
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            data = urllib.request.urlopen(req, timeout=30).read()
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

def code_of(name, year, cat):
    """生成 paper_code：年份-省份-版本-类别，避免 B/C/D/E 类冲突"""
    v = 'fs' if '副省' in name or '省部' in name else 'ds' if ('地市' in name or '市地' in name) else 'xzf' if '行政执法' in name else 'fy'
    p = {'国考': 'gk', '安徽': 'ah', '福建': 'fj', '甘肃': 'gs', '广东': 'gd', '广西': 'gx', '贵州': 'gz', '海南': 'hi',
         '河北': 'he', '河南': 'ha', '黑龙江': 'hlj', '湖北': 'hb', '湖南': 'hn', '吉林': 'jl', '江苏': 'js',
         '江西': 'jx', '辽宁': 'ln', '内蒙古': 'nmg', '宁夏': 'nx', '青海': 'qh', '山东': 'sd', '山西': 'sx',
         '陕西': 'sn', '四川': 'sc', '新疆': 'xj', '云南': 'yn', '浙江': 'zj', '北京市': 'bj', '上海市': 'sh',
         '天津市': 'tj', '重庆市': 'cq', '深圳市': 'sz', '事业编': 'syb', '福建2026.4.25事业单位统考': 'fj'}.get(cat, 'qk')
    # 类别后缀（B类/C类/D类/E类/乡镇/县级/公安/选调/特招等）
    cls = ''
    for k in ['B类', 'C类', 'D类', 'E类', 'A类', '乡镇', '县级', '公安', '选调', '党政机关', '素质测试']:
        if k in name:
            cls = '-' + {'B类': 'b', 'C类': 'c', 'D类': 'd', 'E类': 'e', 'A类': 'a', '乡镇': 'xz',
                          '县级': 'xj', '公安': 'ga', '选调': 'xd', '党政机关': 'dz', '素质测试': 'sz'}[k]
            break
    return '%s-%s-%s%s' % (year, p, v, cls)

def crawl_paper(sid, source, cat, model):
    """爬取一套卷，返回 SQL 字符串与统计；失败返回 None"""
    enc_id = aes_encrypt(str(sid), KEY_ENC)
    r = post('https://saduck.top/api/tk/sourceInfo', {'id': enc_id}, {'token': TOKEN})
    if r.get('code') != 0:
        print('  [失败] %s: %s' % (source, r.get('message')))
        return None
    questions = r['result']
    if not questions:
        print('  [失败] %s: 空' % source)
        return None
    m = re.search(r'(20\d{2})', source)
    year = m.group(1) if m else '2000'
    code = code_of(source, year, cat)
    img_dir = os.path.join(IMG_DIR, code)
    os.makedirs(img_dir, exist_ok=True)

    seen_img = {}
    img_lock = __import__('threading').Lock()

    def rewrite_imgs(html):
        def rep(match):
            tag = match.group(0)
            srcm = re.search(r'src=["\']([^"\']+)["\']', tag)
            if not srcm:
                return tag
            src = srcm.group(1)
            # 解码 HTML 实体（&amp; → &），否则公式图 URL 参数错误返回 400
            src = htmllib.unescape(src)
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://saduck.top' + src
            with img_lock:
                if src not in seen_img:
                    name = 'img%d.png' % (len(seen_img) + 1)
                    seen_img[src] = name
                else:
                    return tag.replace(srcm.group(0), 'src="/exam-img/%s/%s"' % (code, seen_img[src]))
            return tag.replace(srcm.group(0), 'src="/exam-img/%s/%s"' % (code, seen_img[src]))
        return re.sub(r'<img[^>]*>', rep, html)

    section_of = {}
    for mm in model:
        for n in range(mm['snum'], mm['enum'] + 1):
            section_of[n] = SECTION_MAP.get(mm['name'], mm['name'])

    materials = []
    mat_map = {}
    qrows = []
    for idx, q in enumerate(questions, start=1):
        title = rewrite_imgs(q.get('title') or '')
        analysis = rewrite_imgs(q.get('analysis') or '')
        mat_html = rewrite_imgs(q.get('material') or '')
        mat_idx = None
        if mat_html:
            if mat_html not in mat_map:
                mat_map[mat_html] = len(materials)
                materials.append(mat_html)
            mat_idx = mat_map[mat_html]
        opts = [o.strip() for o in (q.get('options') or '').split('#') if o.strip()]
        labels = 'ABCDEFGH'
        opt_list = [{'label': labels[i], 'html': o} for i, o in enumerate(opts)]
        # 答案：可能多选（'1,3'）或异常（'34%'），提取数字索引拼字母
        ans_raw = str(q.get('correctAnswer') or '0')
        nums = re.findall(r'\d+', ans_raw)
        ans_chars = []
        for n in nums:
            v = int(n)
            if 0 <= v < len(labels) and labels[v] not in ans_chars:
                ans_chars.append(labels[v])
        answer = ''.join(ans_chars) if ans_chars else 'A'
        qrows.append({
            'qno': idx, 'section': section_of.get(idx, '常识判断'), 'stem': title,
            'options': json.dumps(opt_list, ensure_ascii=False),
            'answer': answer, 'analysis': analysis, 'mat_idx': mat_idx
        })

    # 并发下载图片（降并发防限流）
    urls = list(seen_img.keys())
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(download, u, os.path.join(img_dir, seen_img[u])): u for u in urls}
        for f in futures:
            f.result()
    failed = sum(1 for f in futures if not f.result())

    # SQL
    title_sql = source
    lines = []
    lines.append("SET NAMES utf8mb4;")
    lines.append("INSERT INTO exam_paper (paper_code, title, year, version, subject, question_count) VALUES ('%s', '%s', %s, '%s', '行测', %d);" % (
        code, esc(title_sql), year, cat, len(qrows)))
    lines.append("SET @pid = LAST_INSERT_ID();")
    for mi, m in enumerate(materials):
        lines.append("INSERT INTO exam_material (paper_id, section, title, content, sort_order) VALUES (@pid, '%s', '材料%d', '%s', %d);" % (
            esc(qrows[[q['mat_idx'] for q in qrows].index(mi)]['section']) if mi in [q['mat_idx'] for q in qrows] else '常识判断',
            mi + 1, esc(m), mi + 1))
    lines.append("SET @mid_1 = LAST_INSERT_ID() - %d;" % (len(materials) - 1))
    for q in qrows:
        mid = 'NULL'
        if q['mat_idx'] is not None:
            mid = '(@mid_1 + %d)' % q['mat_idx']
        lines.append("INSERT INTO exam_question (paper_id, material_id, section, qno, qorder, stem, options, answer, analysis, has_image) VALUES (@pid, %s, '%s', %d, %d, '%s', '%s', '%s', '%s', %d);" % (
            mid, esc(q['section']), q['qno'], q['qno'], esc(q['stem']), esc(q['options']), q['answer'], esc(q['analysis']),
            1 if '<img' in q['stem'] or '<img' in q['analysis'] else 0))
    return '\n'.join(lines), len(qrows), len(materials), len(seen_img), failed

def import_sql(sql):
    import subprocess, tempfile
    # SQL 可能很大，写入临时文件后用 source 导入（避免命令行长度限制）
    tmp = os.path.join(tempfile.gettempdir(), 'crawl_tmp.sql')
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

def main():
    # 1) 清单
    r = post('https://saduck.top/api/tk/itemizes?type=1', {})
    data = json.loads(aes_decrypt(r['result'], KEY_LIST))
    jobs = []
    for g in data:
        cat = g.get('title')
        for s in g.get('tkSources', []):
            try:
                model = json.loads(s.get('model') or '[]')
            except Exception:
                model = []
            m = re.search(r'(20\d{2})', s.get('source', ''))
            year = m.group(1) if m else '2000'
            code = code_of(s['source'], year, cat)
            jobs.append((s['sid'], s['source'], cat, model, code))
    # 断点续爬：跳过已入库的卷
    import subprocess
    p = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', 'ruoyi',
                        '-e', "SELECT paper_code FROM exam_paper WHERE subject='行测'"],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    existing = set(p.stdout.split())
    jobs = [j for j in jobs if j[4] not in existing]
    print('共 %d 套待爬取（已跳过 %d 套已入库）' % (len(jobs), 161 - len(jobs)))

    ok = 0
    fail = []
    for i, (sid, source, cat, model, code) in enumerate(jobs, start=1):
        try:
            res = crawl_paper(sid, source, cat, model)
            if res is None:
                fail.append(source)
                continue
            sql, nq, nm, ni, nf = res
            if import_sql(sql):
                ok += 1
                print('[%d/%d] OK %s | %d题 %d材料 %d图(失败%d)' % (i, len(jobs), source, nq, nm, ni, nf))
            else:
                fail.append(source + ' (导入失败)')
                print('[%d/%d] 导入失败 %s' % (i, len(jobs), source))
        except Exception as e:
            fail.append(source + ' (' + str(e)[:50] + ')')
            print('[%d/%d] 异常 %s: %s' % (i, len(jobs), source, str(e)[:80]))
        time.sleep(0.5)
    print('\n完成: 成功 %d, 失败 %d' % (ok, len(fail)))
    for f in fail:
        print('  FAIL:', f)

if __name__ == '__main__':
    main()
