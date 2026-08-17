# -*- coding: utf-8 -*-
"""解析国考申论真题 docx → JSON + SQL
结构：标题 / 注意事项 / 材料1..N / 作答要求(题目) / 参考答案
"""
import os, re, json, glob, html

SRC = r'C:\Users\admin\DSH\data\shenlun_docx'
OUT_DIR = r'C:\Users\admin\DSH\data\parsed_shenlun'
SQL_OUT = r'C:\Users\admin\DSH\data\sql\shenlun_data.sql'
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(SQL_OUT), exist_ok=True)

QNO_RE = re.compile(r'^([一二三四五六七八九十]+|\d{1,2})[、.]')
MAT_RE = re.compile(r'^(材料|资料|给定资料)\s*(\d+)\s*$')
SCORE_RE = re.compile(r'[（(]?\s*(\d{1,2})\s*分')
WORD_RE = re.compile(r'(?:不超过|控制在|左右)\s*(\d{3,4})\s*字|字数\s*(\d{3,4})\s*[-—至到]?\s*(\d{3,4})?\s*字|不少于\s*(\d{3,4})\s*字')

def read_docx(path):
    import docx
    d = docx.Document(path)
    return [p.text.strip() for p in d.paragraphs if p.text.strip()]

def paper_code(name):
    m = re.search(r'(20\d{2})', name)
    year = m.group(1) if m else '0000'
    v = 'fs' if '副省' in name else 'ds' if ('地市' in name or '市地' in name) else 'sb' if ('省部' in name or '省级' in name) else 'xzf' if '行政执法' in name else 'fy'
    return '%s-%s' % (year, v)

def parse(path):
    paras = read_docx(path)
    name = os.path.basename(path)
    code = paper_code(name)
    year = code.split('-')[0]
    version_map = {'fs': '副省级', 'ds': '地市级', 'sb': '省部级', 'xzf': '行政执法类', 'fy': '副省级'}
    version = version_map.get(code.split('-')[1], '')
    title = paras[0][:60] if paras else name
    print('==', code, title)

    # 定位关键节
    idx_q = None; idx_a = None
    for i, t in enumerate(paras):
        if idx_q is None and re.search(r'作答要求|申论要求|答题要求', t) and len(t) < 30:
            idx_q = i
        if idx_a is None and re.search(r'参考.?答案|参考答案及解析|答案详细解析|【参考答案】', t) and len(t) < 40 and i > (idx_q or 0):
            idx_a = i
    if idx_q is None:
        # 在答案区之前扫描题目起始行（中文或数字题号）
        end = idx_a if idx_a is not None else len(paras)
        for i in range(6, end):
            t = paras[i]
            m = QNO_RE.match(t)
            if m and (('分' in t) or ('要求' in t) or ('根据' in t) or ('概括' in t) or ('请用' in t)) and len(t) < 120:
                idx_q = i
                break
    if idx_a is None:
        for i, t in enumerate(paras):
            if t.strip() in ('参考答案', '参考答案及解析') or t.startswith('参考答案') or '答案详细解析' in t:
                idx_a = i
                break
    if idx_q is None or idx_a is None:
        print('  警告: 未定位 作答要求=%s 参考答案=%s' % (idx_q, idx_a))
        if idx_a is not None: idx_q = idx_a
        elif idx_q is not None: idx_a = len(paras)
        else: return None

    # 材料：作答要求之前的正文，跳过注意事项（标题段之后的"一、注意事项"起，到第一个非注意事项段）
    mat_raw = []
    in_note = True
    for t in paras[1:idx_q]:
        if in_note and re.search(r'注意事项|本题本由|考试时限|满分|作答参考时限', t) and len(t) < 60:
            continue
        if in_note and re.match(r'^[一二三四五六七八九十]+、', t) and len(t) < 30:
            continue
        in_note = False
        mat_raw.append(t)
    # 按材料标题切分
    materials = []
    cur = None
    for t in mat_raw:
        m = MAT_RE.match(t)
        if m and len(t) <= 12:
            if cur is not None: materials.append(cur)
            cur = {'no': int(m.group(2)), 'paras': []}
        else:
            if cur is None: cur = {'no': 1, 'paras': []}
            cur['paras'].append(t)
    if cur is not None: materials.append(cur)
    # 材料号重排（可能从2开始而缺1）
    materials.sort(key=lambda x: x['no'])
    for i, m in enumerate(materials):
        m['no'] = i + 1

    # 题目
    questions = []
    cur_q = None
    for t in paras[idx_q:idx_a]:
        m = QNO_RE.match(t)
        if m and len(t) < 200:
            if cur_q: questions.append(cur_q)
            cur_q = {'no': m.group(1), 'lines': [t]}
        elif cur_q is not None:
            cur_q['lines'].append(t)
    if cur_q: questions.append(cur_q)

    # 参考答案
    answers = []
    cur_a = None
    for t in paras[idx_a:]:
        if re.search(r'【参考答案】|参考答案[:：]', t) and len(t) < 20:
            continue
        m = QNO_RE.match(t)
        if m and len(t) < 60 and not re.match(r'^[一二三四五六七八九十\d]+[、.]\s*\d', t):
            if cur_a: answers.append(cur_a)
            cur_a = {'no': m.group(1), 'lines': [t]}
        elif cur_a is not None:
            cur_a['lines'].append(t)
    if cur_a: answers.append(cur_a)

    # 合并题目与答案
    def to_num(s):
        if s.isdigit():
            return int(s)
        zh = '一二三四五六七八九十'
        return zh.index(s) + 1 if s in zh else 0
    ans_map = {to_num(a['no']): '\n'.join(a['lines']) for a in answers}
    qlist = []
    for q in questions:
        qno = to_num(q['no'])
        if qno == 0:
            continue
        qtext = '\n'.join(q['lines'])
        score_m = SCORE_RE.search(qtext)
        word_m = WORD_RE.search(qtext)
        wl = 0
        if word_m:
            wl = int(next((g for g in (word_m.group(1), word_m.group(2), word_m.group(3), word_m.group(4)) if g), 0))
        qlist.append({
            'qno': qno,
            'title': qtext,
            'score': int(score_m.group(1)) if score_m else 0,
            'word_limit': wl,
            'ref_answer': ans_map.get(qno, '')
        })

    return {
        'paper_code': code, 'year': int(year), 'version': version, 'title': title,
        'materials': [{'no': m['no'], 'content': '\n'.join(m['paras'])} for m in materials],
        'questions': qlist
    }

def esc(s):
    return s.replace('\\', '\\\\').replace("'", "''")

def main():
    papers = []
    for f in sorted(glob.glob(os.path.join(SRC, '*.docx'))):
        try:
            p = parse(f)
            if p: papers.append(p)
        except Exception as e:
            print('  解析失败:', os.path.basename(f), e)

    with open(os.path.join(OUT_DIR, 'papers.json'), 'w', encoding='utf-8') as fh:
        json.dump(papers, fh, ensure_ascii=False, indent=1)

    # 生成 SQL
    lines = ['-- 申论题库数据', 'SET NAMES utf8mb4;', 'TRUNCATE TABLE shenlun_answer; TRUNCATE TABLE shenlun_question; TRUNCATE TABLE shenlun_material; TRUNCATE TABLE shenlun_paper;']
    pid = 1
    for p in papers:
        lines.append("INSERT INTO shenlun_paper (id, paper_code, title, year, version, question_count) VALUES (%d, '%s', '%s', %d, '%s', %d);" % (
            pid, esc(p['paper_code']), esc(p['title']), p['year'], esc(p['version']), len(p['questions'])))
        for m in p['materials']:
            lines.append("INSERT INTO shenlun_material (paper_id, m_no, title, content) VALUES (%d, %d, '材料%d', '%s');" % (
                pid, m['no'], m['no'], esc(m['content'].replace('\n', '\n'))))
        for q in p['questions']:
            lines.append("INSERT INTO shenlun_question (paper_id, qno, title, score, word_limit, ref_answer) VALUES (%d, %d, '%s', %d, %d, '%s');" % (
                pid, q['qno'], esc(q['title']), q['score'], q['word_limit'], esc(q['ref_answer'])))
        pid += 1
    with open(SQL_OUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    print('\n共解析 %d 套，SQL 输出: %s' % (len(papers), SQL_OUT))
    total_q = sum(len(p['questions']) for p in papers)
    total_m = sum(len(p['materials']) for p in papers)
    noans = sum(1 for p in papers for q in p['questions'] if not q['ref_answer'])
    print('题目 %d 道，材料 %d 段，缺参考答案 %d 道' % (total_q, total_m, noans))

if __name__ == '__main__':
    main()
