# -*- coding: utf-8 -*-
"""爬取 saduck 行测卷 → 转换 → 图片下载 → 生成 SQL 入库
用法: python crawl_saduck.py <sid> <paper_code> <year> <version> <model_json>
"""
import urllib.request, json, base64, re, os, sys, time
from Crypto.Cipher import AES

TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ2aXBFbmRUaW1lIjoiMTc4NDg3NDU0MDAwMCIsInNpZ24iOiIwNzMxNjA0NTkxIiwidmlwVHlwZSI6IjAiLCJ2aXBTdGFydFRpbWUiOiIxNzg0NjE1MzQwMDAwIiwiayI6IiIsImtGIjoiIiwiZXhwIjoxNzg4NzA1MzI4LCJlbWFpbCI6IjEzNzc4MTAxNDdAcXEuY29tIn0.UtmrtXi-VNnGAWGqm2JuWOOSbpjjwb3HD5iY4knund8'
KEY_LIST = '7SyqrN6925ZYb636'
KEY_ENC = 'kxZ17XQ8z6957n3S'

IMG_DIR = r'C:\Users\admin\DSH\data\images'
HDRS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0', 'Referer': 'https://www.saduck.top/'}

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

def download(url, path, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            data = urllib.request.urlopen(req, timeout=30).read()
            with open(path, 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            if i == retry - 1:
                print('  图片下载失败:', url, e)
            time.sleep(1)
    return False

def esc(s):
    return s.replace('\\', '\\\\').replace("'", "''")

MODELS = {
    '2026-fs': [{"name": "政治理论", "snum": 1, "enum": 20}, {"name": "常识判断", "snum": 21, "enum": 35},
                {"name": "言语理解", "snum": 36, "enum": 65}, {"name": "数量关系", "snum": 66, "enum": 80},
                {"name": "判断推理", "snum": 81, "enum": 115}, {"name": "资料分析", "snum": 116, "enum": 135}],
}

def main():
    sid, code, year, version, model_json = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    if model_json in MODELS:
        model = MODELS[model_json]
    else:
        model = json.loads(model_json)  # [{name, snum, enum}]

    # 1) 抓题
    enc_id = aes_encrypt(str(sid), KEY_ENC)
    r = post('https://saduck.top/api/tk/sourceInfo', {'id': enc_id}, {'token': TOKEN})
    if r.get('code') != 0:
        print('抓取失败:', r.get('message'))
        return
    questions = r['result']
    print('抓取题目:', len(questions))

    # 2) 图片下载目录
    img_dir = os.path.join(IMG_DIR, code)
    os.makedirs(img_dir, exist_ok=True)

    def rewrite_imgs(html, seen):
        """下载图片并替换 src → /exam-img/code/xxx.png"""
        def rep(m):
            tag = m.group(0)
            srcm = re.search(r'src=["\']([^"\']+)["\']', tag)
            if not srcm:
                return tag
            src = srcm.group(1)
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://saduck.top' + src
            if src not in seen:
                name = 'img%d.png' % (len(seen) + 1)
                seen[src] = name
                download(src, os.path.join(img_dir, name))
            name = seen[src]
            return tag.replace(srcm.group(0), 'src="/exam-img/%s/%s"' % (code, name))
        return re.sub(r'<img[^>]*>', rep, html)

    # 3) 处理题目与材料
    section_of = {}
    for m in model:
        for n in range(m['snum'], m['enum'] + 1):
            section_of[n] = SECTION_MAP.get(m['name'], m['name'])

    materials = []  # [{content, ids: []}]
    mat_map = {}
    seen_img = {}
    qrows = []
    for idx, q in enumerate(questions, start=1):
        title = rewrite_imgs(q.get('title') or '', seen_img)
        analysis = rewrite_imgs(q.get('analysis') or '', seen_img)
        mat_html = rewrite_imgs(q.get('material') or '', seen_img)
        # 材料去重
        material_id = 'NULL'
        if mat_html:
            key = mat_html
            if key not in mat_map:
                mat_map[key] = len(materials)
                materials.append({'content': mat_html, 'ids': []})
            mi = mat_map[key]
            materials[mi]['ids'].append(idx)
            material_id = None  # 稍后填
        # 选项
        opts = q.get('options') or ''
        opt_parts = [o.strip() for o in opts.split('#') if o.strip()]
        labels = 'ABCDEFGH'
        opt_list = []
        for i, o in enumerate(opt_parts):
            opt_list.append({'label': labels[i], 'html': o})
        # 答案
        ans_idx = int(q.get('correctAnswer') or 0)
        answer = labels[ans_idx] if ans_idx < len(labels) else 'A'
        section = section_of.get(idx, '常识判断')
        qrows.append({
            'qno': idx, 'section': section, 'stem': title,
            'options': json.dumps(opt_list, ensure_ascii=False),
            'answer': answer, 'analysis': analysis, 'mat_idx': mat_map.get(mat_html) if mat_html else None
        })

    # 4) 生成 SQL
    title = '%s年国家公务员录用考试《行测》（%s）' % (year, version)
    lines = []
    lines.append("SET NAMES utf8mb4;")
    lines.append("INSERT INTO exam_paper (paper_code, title, year, version, subject, question_count) VALUES ('%s', '%s', %s, '%s', '行测', %d);" % (
        code, esc(title), year, version, len(qrows)))
    lines.append("SET @pid = LAST_INSERT_ID();")
    # 材料
    for mi, m in enumerate(materials):
        lines.append("INSERT INTO exam_material (paper_id, section, title, content, sort_order) VALUES (@pid, '%s', '材料%d', '%s', %d);" % (
            esc(qrows[m['ids'][0] - 1]['section']), mi + 1, esc(m['content']), mi + 1))
    lines.append("SET @mid_1 = LAST_INSERT_ID() - %d;" % (len(materials) - 1))
    # 题目（材料 id = @mid_1 + mat_idx）
    for q in qrows:
        mid = 'NULL'
        if q['mat_idx'] is not None:
            mid = '(@mid_1 + %d)' % q['mat_idx']
        lines.append("INSERT INTO exam_question (paper_id, material_id, section, qno, qorder, stem, options, answer, analysis, has_image) VALUES (@pid, %s, '%s', %d, %d, '%s', '%s', '%s', '%s', %d);" % (
            mid, esc(q['section']), q['qno'], q['qno'], esc(q['stem']), esc(q['options']), q['answer'], esc(q['analysis']),
            1 if q['stem'].count('<img') or q['analysis'].count('<img') else 0))

    sql = '\n'.join(lines)
    sql_path = r'C:\Users\admin\DSH\data\sql\saduck_%s.sql' % code
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(sql)
    print('SQL 输出:', sql_path, '| 图片下载:', len(seen_img), '| 材料:', len(materials))

if __name__ == '__main__':
    main()
