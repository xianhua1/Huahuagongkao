# -*- coding: utf-8 -*-
"""国考行测真题全量解析管线：docx -> 题目/材料 JSON + 图片；PDF -> 答案/解析；合并 -> SQL。
用法:
  python parse_all.py scan            # 扫描试卷清单
  python parse_all.py paper <paperId> # 只解析一套卷
  python parse_all.py all             # 解析全部
"""
import os
import re
import sys
import json
import shutil
import html as htmlmod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_parse import parse_blocks, block_text, block_imgs

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(BASE), 'data')
DOCX_DIR = os.path.join(DATA, 'xingce_docx')
ANSWER_DIR = r'D:\BaiduNetdiskDownload\国考2000-2022真题word 【赠送,供参考,不推荐使用】\国家行测2000年-2022年word版【赠送-供参考】\答案及解析'
OUT_DIR = os.path.join(DATA, 'parsed')
IMG_ROOT = os.path.join(DATA, 'images')
SQL_DIR = os.path.join(DATA, 'sql')

SECTION_ALIAS = {
    '常识判断': '常识判断',
    '言语理解': '言语理解与表达',
    '言语理解与表达': '言语理解与表达',
    '数量关系': '数量关系',
    '判断推理': '判断推理',
    '资料分析': '资料分析',
    '知觉速度与准确性': '知觉速度与准确性',
    '知觉速度': '知觉速度与准确性',
}
SECTION_ORDER = {'常识判断': 1, '言语理解与表达': 2, '数量关系': 3, '判断推理': 4, '资料分析': 5, '知觉速度与准确性': 0}

VERSION_ALIAS = {'市地级': ['市地级', '地市级'], '地市级': ['市地级', '地市级']}


def detect_paper_meta(fname):
    """从文件名提取 (year, version, title)。"""
    base = os.path.splitext(fname)[0]
    m = re.search(r'(19|20)\d{2}', base)
    year = int(m.group(0)) if m else 0
    version = '全国卷'
    for kw, v in [('行政执法', '行政执法类'), ('副省', '副省级'), ('省部级', '省部级'),
                  ('地市', '地市级'), ('市地', '市地级'), ('省级', '省级'),
                  ('A卷', 'A卷'), ('B卷', 'B卷'),
                  ('（一）', '卷一'), ('（二）', '卷二'), ('卷一', '卷一'), ('卷二', '卷二')]:
        if kw in base:
            version = v
            break
    return year, version, base


def scan_papers():
    """返回 [{'id','year','version','title','docx','pdf'}] 列表（按年份排序）。"""
    docs = {}
    for f in os.listdir(DOCX_DIR):
        if f.lower().endswith('.docx'):
            year, version, title = detect_paper_meta(f)
            docs.setdefault(year, []).append({'f': f, 'version': version, 'title': title})
    pdfs = {}
    if os.path.isdir(ANSWER_DIR):
        for f in os.listdir(ANSWER_DIR):
            if f.lower().endswith('.pdf'):
                year, version, _ = detect_paper_meta(f)
                pdfs.setdefault(year, []).append({'f': f, 'version': version})
    papers = []
    for year in sorted(docs):
        for d in sorted(docs[year], key=lambda x: x['version']):
            pid = '%d-%s' % (year, d['version'].replace('卷', ''))
            pid = pid.replace('省部级', 'sbj').replace('行政执法类', 'xzf') \
                     .replace('副省级', 'fsj').replace('地市级', 'dsj') \
                     .replace('市地级', 'sdj').replace('省级', 'sj') \
                     .replace('A卷', 'a').replace('B卷', 'b') \
                     .replace('卷一', 'y1').replace('卷二', 'y2').replace('全国卷', 'qg')
            pdf = None
            if year in pdfs:
                cands = [p for p in pdfs[year] if p['version'] == d['version']]
                if not cands:
                    aliases = VERSION_ALIAS.get(d['version'], [d['version']])
                    cands = [p for p in pdfs[year] if p['version'] in aliases]
                if cands:
                    pdf = cands[0]['f']
            papers.append({'id': pid, 'year': year, 'version': d['version'],
                           'title': d['title'], 'docx': d['f'], 'pdf': pdf})
    return papers


# ---------------- docx 解析 ----------------

def esc(s):
    return htmlmod.escape(s, quote=False)


def tokens_to_html(tokens, paper_id, in_table=False):
    out = []
    for kind, val in tokens:
        if kind == 't':
            t = val.replace('\u200b', '').replace('\u00a0', ' ')
            out.append(esc(t))
        elif kind == 'img':
            out.append('<img src="/exam-img/%s/%s" alt="图片"/>' % (paper_id, val))
    return ''.join(out)


def block_to_html(block, paper_id):
    kind, data = block
    if kind == 'p':
        txt = tokens_to_html(data, paper_id).strip()
        return '<p>%s</p>' % txt if txt else ''
    # table
    rows = []
    for row in data:
        tds = []
        for cell in row:
            inner = ''.join(block_to_html(b, paper_id) for b in cell).strip()
            tds.append('<td>%s</td>' % inner)
        rows.append('<tr>%s</tr>' % ''.join(tds))
    return '<table border="1" cellpadding="4" cellspacing="0">%s</table>' % ''.join(rows)


SUB_HEADER_RE = re.compile(r'^\s*[一二三四五六七八九十]{1,3}\s*[、．.]')
SECTION_RE = re.compile(r'^\s*第\s*[一二三四五六七八九十]{1,3}\s*部分\s*([^。\n]{2,14})')
SECTION_RE2 = re.compile(r'^\s*[一二三四五六七八九十]{1,3}\s*[、．.]\s*([^。，：\n]{2,12}?)(?:。|，|：|$)')
QNO_RE = re.compile(r'^\s*(\d{1,3})\s*(?:[．.、：]|\n|$)')
QNO_INLINE_RE = re.compile(r'(?<![\d.])(\d{1,3})\s*(?:[．.、：]|\n|$)')
QNO_SPACE_RE = re.compile(r'^\s*(\d{1,3})\s{2,}(\S)')
OPT_RE = re.compile(r'([A-H])\s*[．.、]')
JUNK_RE = re.compile(r'结束|请继续做|本部分|以下资料|请仔细|打开资料')
RULES_RE = re.compile(r'根据题目要求|本部分包括|所给出的图、表|参考时限|在这部分试题中|共\d+题|请根据题目要求')
GROUP_MARK_RE = re.compile(r'^\s*[（(]\s*[一二三四五六七八九十]+\s*[）)]\s*$')


def norm_section(name):
    name = name.strip()
    for k, v in SECTION_ALIAS.items():
        if k in name:
            return v
    return name


def parse_paper_docx(docx_path, paper_id):
    return parse_question_blocks(parse_blocks(docx_path), paper_id)


def qno_at_line_start(raw, pos):
    """题号候选是否处于行首（前面是换行/双全角空格/块开头），避免把选项里的数字当题号。"""
    if pos <= 0:
        return True
    return raw[pos - 1] == '\n' or raw[pos - 2:pos] == '\u3000\u3000'


def parse_question_blocks(blocks, paper_id):
    # 预扫描：找到第一个节标题的位置，跳过其前的标题/说明块
    first_section_idx = None
    has_part_style = False
    for i, b in enumerate(blocks):
        t = block_text(b).strip()
        m = SECTION_RE.match(t)
        m2 = SECTION_RE2.match(t) if not OPT_RE.match(t) else None
        if m:
            has_part_style = True
        if m or (m2 and norm_section(m2.group(1)) in SECTION_ALIAS.values()):
            first_section_idx = i
            break
    if first_section_idx is None:
        first_section_idx = 0

    materials = []          # {'id','section','title','html','order'}
    questions = []          # {'no','section','stem','options','answer','analysis','material','order'}
    section = None
    material = None
    material_open = False
    material_order = 0
    qorder = 0
    last_no = 0
    cur = None  # 当前题目 dict

    def close_question():
        nonlocal cur
        if cur:
            # 收尾待填充选项（散排字母块 + 图片/片段）
            if cur.get('_pending'):
                h = ''.join(cur.get('_pending_html') or [])
                if h:
                    cur['options'].append({'label': cur['_pending'][0], 'html': h})
                cur['_pending'] = None
            questions.append(cur)
            cur = None

    def process_block(block):
        nonlocal section, material, material_open, material_order, qorder, last_no, cur
        kind, data = block
        if kind == 'p':
            data_norm = [(k, v.replace('\u200b', '') if k == 't' else v) for k, v in data]
            raw = ''.join(v for k, v in data_norm if k == 't')
        else:
            data_norm = None
            raw = block_text(block).replace('\u200b', '')
        txt = raw.strip()
        imgs = block_imgs(block)
        if not txt and not imgs:
            return

        def process_remainder(pos):
            """把段落中标题之后的剩余部分当作新块继续处理（标题与正文同段时）。"""
            if data_norm is None or pos >= len(raw):
                return
            segs = split_tokens_by_positions(data_norm, [pos])
            for seg in segs[1:]:
                if any(t[1].strip() for t in seg if t[0] == 't'):
                    process_block(('p', seg))

        # 节标题
        m = SECTION_RE.match(raw)
        if m:
            close_question()
            section = norm_section(m.group(1))
            last_no = 0
            material = None
            material_open = False
            process_remainder(m.end())
            return
        m2 = SECTION_RE2.match(raw)
        if m2 and not OPT_RE.match(raw):
            cand = norm_section(m2.group(1))
            if cand in SECTION_ALIAS.values() and not (has_part_style and section is not None):
                close_question()
                section = cand
                last_no = 0
                material = None
                material_open = False
                process_remainder(m2.end())
                return
        # 材料组标记（一）（二）...
        if GROUP_MARK_RE.match(raw):
            close_question()
            material_order += 1
            material = {'id': '%s-m%d' % (paper_id, material_order),
                        'section': section or '', 'title': txt,
                        'html': '', 'order': material_order}
            materials.append(material)
            material_open = True
            return
        # 子标题（旧卷：一、数字推理：... / 一、请根据下图回答81～85题。)
        if SUB_HEADER_RE.match(raw) and not QNO_RE.match(raw) and len(txt) < 100:
            if '请根据' in txt or '根据所给' in txt or '根据以下' in txt or '根据下列' in txt:
                close_question()
                material_order += 1
                material = {'id': '%s-m%d' % (paper_id, material_order),
                            'section': section or '', 'title': txt,
                            'html': '<p>%s</p>' % esc(txt), 'order': material_order}
                materials.append(material)
                material_open = True
                process_remainder(m.end() if (m := SUB_HEADER_RE.match(raw)) else len(raw))
            else:
                close_question()
                material = None  # 规则说明，忽略
                material_open = False
                last_no = 0      # 旧卷子部分内重新编号
            return
        if JUNK_RE.search(txt) and len(txt) < 30:
            return
        # 段内嵌节标题（如选项尾接“三、数量关系。…”）-> 先切分再处理
        if kind == 'p' and data_norm is not None:
            sec_cuts = [m.start() for m in re.finditer(
                r'(?<![\d])[一二三四五六七八九十]{1,3}\s*[、．.]\s*([^。，：\n]{2,12}?)(?:。|，|：|$)', raw)
                if norm_section(m.group(1)) in SECTION_ALIAS.values()]
            sec_cuts += [m.start() for m in re.finditer(
                r'(?<![\d])第\s*[一二三四五六七八九十]{1,3}\s*部分', raw)]
            sec_cuts = sorted(set(sec_cuts))
            if sec_cuts and sec_cuts[0] > 0:
                segs = split_tokens_by_positions(data_norm, [sec_cuts[0]])
                for seg in segs:
                    if any(t[1].strip() for t in seg if t[0] == 't'):
                        process_block(('p', seg))
                return
        # 病态块：一段内合并多题（PDF 版面块/转换文档），按连续题号拆分
        if kind == 'p' and data_norm is not None:
            cands = [(m.start(), int(m.group(1))) for m in QNO_INLINE_RE.finditer(raw)]
            cands = [(pos, n) for pos, n in cands if n > 0 and qno_at_line_start(raw, pos)]
            bounds = []
            for pos, n in cands:
                if n == last_no + 1 or (bounds and n == bounds[-1] + 1):
                    bounds.append(n)
            sec_cuts = []
            for m in re.finditer(r'(?<![\d])[一二三四五六七八九十]{1,3}\s*[、．.]\s*([^。，：\n]{2,12}?)(?:。|，|：|$)', raw):
                if norm_section(m.group(1)) in SECTION_ALIAS.values():
                    sec_cuts.append(m.start())
            for m in re.finditer(r'(?<![\d])第\s*[一二三四五六七八九十]{1,3}\s*部分', raw):
                sec_cuts.append(m.start())
            first_pos = next((pos for pos, n in cands if n == bounds[0]), -1) if bounds else -1
            if bounds and (len(bounds) > 1 or first_pos > 0):
                bpos = sorted(set([p for p, n in cands if n in bounds] + sec_cuts))
                segs = split_tokens_by_positions(data_norm, bpos)
                for seg in segs:
                    if any(t[1].strip() for t in seg if t[0] == 't'):
                        process_block(('p', seg))
                return
        # 节内规则说明（每个部分的导语，如“根据题目要求…”“所给出的图、表…”）
        if RULES_RE.search(txt):
            return
        # 散排选项：独立字母块（“A.”）+ 后续图片/短文本片段 -> 待填充选项
        if cur is not None:
            stripped = raw.lstrip()
            m_letter = OPT_RE.match(stripped)
            is_letter_only = m_letter and m_letter.end() == len(stripped) and len(stripped) <= 3
            if is_letter_only:
                if cur.get('_pending'):
                    h = ''.join(cur.get('_pending_html') or [])
                    if h:
                        cur['options'].append({'label': cur['_pending'][0], 'html': h})
                cur['_pending'] = (m_letter.group(1),)
                cur['_pending_html'] = []
                return
            if cur.get('_pending'):
                is_fragment = imgs or (len(txt) < 40 and not QNO_INLINE_RE.match(raw.lstrip()))
                if is_fragment:
                    cur['_pending_html'].append(block_to_html(block, paper_id))
                    return
                # 非片段内容：关闭待填充，继续正常处理
                h = ''.join(cur.get('_pending_html') or [])
                if h:
                    cur['options'].append({'label': cur['_pending'][0], 'html': h})
                cur['_pending'] = None
                cur['_pending_html'] = []
        # 规则说明 / 例题（旧卷常见）
        if ('例题' in txt or '请开始答题' in txt or '参考时限' in txt or
                re.match(r'^\s*\(共\d+题', txt) or txt.startswith('解答：')):
            return
        # 题目
        mq = QNO_RE.match(raw)
        if not mq:
            # 数字后为空格（如“104    B超…”），仅接受与上一题号连续的，避免误判
            mq2 = QNO_SPACE_RE.match(raw)
            if mq2 and int(mq2.group(1)) == last_no + 1:
                mq = mq2
        if mq and not OPT_RE.match(raw.lstrip()):
            no = int(mq.group(1))
            if no != last_no and no > 0:
                # 题干段内嵌选项（如“2\n2021…\nA、①②③\nB、…”）-> 先切分
                mm = list(OPT_RE.finditer(raw))
                if len(mm) >= 2 and mm[0].start() > 0 and data_norm is not None:
                    segs = split_tokens_by_positions(data_norm, [mm[0].start()])
                    for seg in segs:
                        if any(t[1].strip() for t in seg if t[0] == 't'):
                            process_block(('p', seg))
                    return
                close_question()
                material_open = False  # 题目开始后材料不再累计
                qorder += 1
                cur = {'no': no, 'section': section or '', 'stem_html': '',
                       'stem_imgs': [], 'options': [], 'material': material,
                       'order': qorder}
                last_no = no
                cur['stem_html'] = block_to_html(block, paper_id)
                cur['stem_imgs'] = imgs
            return
        # 选项
        if cur is not None and OPT_RE.match(raw.lstrip()):
            mml = list(OPT_RE.finditer(raw.lstrip()))
            # 字母序列判定：字母间几乎无内容且末尾跟长句（如“G、M、R、S 是与…”）=> 非选项行
            gap_run = len(mml) > 1
            for a, b in zip(mml, mml[1:]):
                if b.start() - a.end() > 4:
                    gap_run = False
                    break
            tail_len = len(raw.lstrip()[mml[-1].end():])
            if gap_run and tail_len > 30:
                pass  # 落入下面的普通文本分支
            else:
                # 选项段内可能嵌入下一题题干（如“…方式的一种74.下列人员…”“D、4 项\n2\n2021…”）
                emb = [m for m in QNO_INLINE_RE.finditer(raw)
                       if int(m.group(1)) == last_no + 1
                       and qno_at_line_start(raw, m.start())]
                if emb and data_norm is not None:
                    segs = split_tokens_by_positions(data_norm, [emb[0].start()])
                    parse_options_block(('p', segs[0]), paper_id, cur)
                    process_block(('p', segs[1]))
                    return
                parse_options_block(block, paper_id, cur)
                return
        # 其它文本
        if cur is not None and cur['options']:
            # 选项续行（选项文本跨段）：短文本且上一选项未结束 -> 追加进最后一个选项
            last_h = cur['options'][-1]['html']
            if len(txt) < 60 and not imgs and not re.search(r'[。！？…”")】]\s*$', last_h):
                cur['options'][-1]['html'] += block_to_html(block, paper_id)
                return
            # 独立图片块：散排 PDF 的选项图，挂到最后一个选项（避免误成材料）
            if imgs and not txt:
                cur['options'][-1]['html'] += block_to_html(block, paper_id)
                return
            # 无题号的新题（题干+选项同段，如 PDF 缺题号）——推断题号
            mml2 = list(OPT_RE.finditer(raw))
            gap_run2 = len(mml2) > 1
            for a, b in zip(mml2, mml2[1:]):
                if b.start() - a.end() > 4:
                    gap_run2 = False
                    break
            tail_len2 = len(raw[mml2[-1].end():]) if mml2 else 0
            if len(mml2) >= 2 and not (gap_run2 and tail_len2 > 30) and data_norm is not None:
                close_question()
                qorder += 1
                no = last_no + 1
                cur = {'no': no, 'section': section or '', 'stem_html': '',
                       'stem_imgs': [], 'options': [], 'material': material,
                       'order': qorder}
                last_no = no
                if mml2[0].start() > 0:
                    segs = split_tokens_by_positions(data_norm, [mml2[0].start()])
                    stem_html = tokens_to_html(segs[0], paper_id).strip()
                    if stem_html:
                        cur['stem_html'] = '<p>%s</p>' % stem_html
                    cur['stem_imgs'].extend(block_imgs(('p', segs[0])))
                    process_block(('p', segs[1]))
                    return
                cur['stem_html'] = block_to_html(block, paper_id)
                return
            # 上一题选项已结束，出现新文本 -> 关闭上一题，作为新材料
            close_question()
        if cur is None:
            # 材料块：累计进当前材料
            # 例题/示例的选项行（cur 已关闭时）不是材料，直接跳过
            if OPT_RE.match(raw.lstrip()):
                mml0 = list(OPT_RE.finditer(raw.lstrip()))
                gap0 = len(mml0) > 1
                for a, b in zip(mml0, mml0[1:]):
                    if b.start() - a.end() > 4:
                        gap0 = False
                        break
                tail0 = len(raw.lstrip()[mml0[-1].end():]) if mml0 else 0
                if len(mml0) >= 2 and not (gap0 and tail0 > 30):
                    return
            h = block_to_html(block, paper_id)
            if material is None or not material_open:
                material_order += 1
                material = {'id': '%s-m%d' % (paper_id, material_order),
                            'section': section or '', 'title': '',
                            'html': '', 'order': material_order}
                materials.append(material)
                material_open = True
            material['html'] += h
        else:
            # 题干续行 / 题间图片
            # 若段内嵌选项行（如“雷达：天线：探测    B、相机…C、…”），按首个选项字母切分
            # （要求至少 2 个选项标记，避免把“G、M、R、S 是与…”这类句子误切）
            mm = list(OPT_RE.finditer(raw))
            if len(mm) >= 2 and mm[0].start() > 0 and data_norm is not None:
                segs = split_tokens_by_positions(data_norm, [mm[0].start()])
                stem_seg = segs[0]
                opt_seg = segs[1]
                stem_html = tokens_to_html(stem_seg, paper_id).strip()
                if stem_html:
                    cur['stem_html'] += '<p>%s</p>' % stem_html
                cur['stem_imgs'].extend(block_imgs(('p', stem_seg)))
                # 选项段递归处理（可能内嵌下一题题干）
                process_block(('p', opt_seg))
                return
            cur['stem_html'] += block_to_html(block, paper_id)
            cur['stem_imgs'].extend(imgs)

    for idx, block in enumerate(blocks):
        if idx < first_section_idx:
            continue
        kind, data = block
        txt = block_text(block).strip().replace('\u200b', '')
        imgs = block_imgs(block)
        if not txt and not imgs:
            continue
        # 病态文档：一个段落内合并多题（如 2022 地市级转换版），按题号拆分（保留图片位置）
        if kind == 'p':
            data_norm = [(k, v.replace('\u200b', '') if k == 't' else v) for k, v in data]
            raw = ''.join(v for k, v in data_norm if k == 't')
            cands = [(m.start(), int(m.group(1))) for m in QNO_INLINE_RE.finditer(raw)]
            cands = [(pos, n) for pos, n in cands if n > 0]
            # 只保留与上一题号连续的候选，过滤文本中的孤立数字（如 0.5、资料里的年份等）
            bounds = []
            for pos, n in cands:
                if n == last_no + 1 or (bounds and n == bounds[-1] + 1):
                    bounds.append(n)
            # 合并块内可能内嵌节标题（如“二、言语理解与表达，共40题”），一并切分
            sec_cuts = []
            for m in re.finditer(r'(?<![\d])[一二三四五六七八九十]{1,3}\s*[、．.]\s*([^。，：\n]{2,12}?)(?:。|，|：|$)', raw):
                if norm_section(m.group(1)) in SECTION_ALIAS.values():
                    sec_cuts.append(m.start())
            for m in re.finditer(r'(?<![\d])第\s*[一二三四五六七八九十]{1,3}\s*部分', raw):
                sec_cuts.append(m.start())
            if len(bounds) > 1:
                bpos = sorted(set([p for p, n in cands if n in bounds] + sec_cuts))
                segs = split_tokens_by_positions(data_norm, bpos)
                for seg in segs:
                    if any(t[1].strip() for t in seg if t[0] == 't'):
                        process_block(('p', seg))
                continue
        process_block(block)
    close_question()
    return {'materials': materials, 'questions': questions}


def split_tokens_by_positions(tokens, boundaries):
    """按字符偏移把 token 流切成多段；图片 token 归属其所在段。"""
    # 计算每个 token 在拼接文本中的起点
    pos = 0
    tpos = []  # (token_index, start, end or None for img)
    for i, (k, v) in enumerate(tokens):
        if k == 't':
            tpos.append((i, pos, pos + len(v)))
            pos += len(v)
        else:
            tpos.append((i, pos, None))
    cuts = [0] + sorted(boundaries) + [pos]
    segs = []
    for a, b in zip(cuts, cuts[1:]):
        seg = []
        for i, s, e in tpos:
            if e is None:
                # 图片：归属其位置所在段（左开右闭：紧跟选项字母+分隔符后的图属于该选项）
                if (a < s <= b) or (s == a and a == b):
                    seg.append(tokens[i])
            else:
                if s >= b:
                    continue
                if e <= a:
                    continue
                lo = max(s, a) - s
                hi = min(e, b) - s
                if hi > lo:
                    seg.append(('t', tokens[i][1][lo:hi]))
        segs.append(seg)
    return segs


def parse_options_block(block, paper_id, cur):
    kind, data = block
    if kind == 'p':
        toks = [(k, v.replace('\u200b', '') if k == 't' else v) for k, v in data]
    else:
        toks = [('t', block_text(block).replace('\u200b', ''))]
    raw = ''.join(v for k, v in toks if k == 't')
    matches = list(OPT_RE.finditer(raw))
    if not matches:
        return
    # 按选项字母位置切分 token 流（字母与分隔符可能分属不同 run）
    positions = [m.start() for m in matches]
    segs = split_tokens_by_positions(toks, positions)
    labels = [m.group(1) for m in matches]
    strip_label = re.compile(r'^\s*[A-H]\s*[．.、]\s*')
    for label, seg in zip(labels, segs[1:]):
        h = tokens_to_html(seg, paper_id).strip()
        h = strip_label.sub('', h, count=1)
        if h:
            cur['options'].append({'label': label, 'html': h})


# ---------------- 答案 PDF 解析 ----------------

def parse_answers_pdf(pdf_path):
    """合并 pdfminer 与 pypdf 两种提取结果（pdfminer 对损坏 xref 更全，pypdf 对旧版式更准）。
    若存在 OCR 缓存文本（data/ocr_texts/<名>.txt）则优先使用。"""
    texts = []
    cache = os.path.join(DATA, 'ocr_texts', os.path.splitext(os.path.basename(pdf_path))[0] + '.txt')
    if os.path.exists(cache):
        with open(cache, encoding='utf-8') as f:
            t = f.read()
        if len(t) > 200:
            texts.append(t)
    try:
        from pdfminer.high_level import extract_text
        t = extract_text(pdf_path) or ''
        if len(t) > 200:
            texts.append(t)
    except Exception:
        pass
    import pypdf
    try:
        reader = pypdf.PdfReader(pdf_path)
        t = '\n'.join((p.extract_text() or '') for p in reader.pages)
        if len(t) > 200:
            texts.append(t)
    except Exception:
        pass
    result = {}
    for text in texts:
        parsed = _parse_answer_text(text)
        for k, v in parsed.items():
            result.setdefault(k, v)
    # 顺序兜底：题目编号完全缺失时（如扫描版），按解析块顺序编号
    if not result and texts:
        for text in texts:
            chunks = re.split(r'\n\s*解析\s*\n', text)
            if len(chunks) > 2:
                for idx, chunk in enumerate(chunks[1:], start=1):
                    am = None
                    for pat in MARKERS:
                        mm = pat.search(chunk)
                        if mm:
                            am = mm.group(1)
                            break
                    if am:
                        result.setdefault((None, idx), {'answer': am, 'analysis': chunk.strip()})
                break
    return result


MARKERS = [
    re.compile(r'故正确答案为\s*([A-H])'),
    re.compile(r'正确答案[是为:：]\s*([A-H])'),
    re.compile(r'正确答案\s*[【［]\s*([A-H])\s*[】］]'),
    re.compile(r'答案[是为:：]\s*([A-H])'),
    re.compile(r'答案是\s*([A-H])'),
    re.compile(r'答案选\s*([A-H])'),
    re.compile(r'[【［]\s*答案\s*[】］]\s*([A-H])'),
    re.compile(r'故选\s*([A-H])'),
    re.compile(r'应选\s*([A-H])'),
    re.compile(r'选择\s*([A-H])\s*选项'),
    re.compile(r'因此，?选\s*([A-H])\s*项'),
]


def _parse_answer_text(text, prefer='auto'):
    text = text.replace('\u200b', '')
    # 按节标题切分
    sections = []  # [(section_name_or_None, text)]
    cur_name = None
    cur_buf = []
    for line in text.split('\n'):
        m = SECTION_RE.match(line.strip())
        if m:
            sections.append((cur_name, '\n'.join(cur_buf)))
            cur_name = norm_section(m.group(1))
            cur_buf = []
        else:
            cur_buf.append(line)
    sections.append((cur_name, '\n'.join(cur_buf)))

    STYLE_A = re.compile(r'(?<![\d.])(\d{1,3})\s*[．.、]\s*([A-H])\s*[【［]\s*解析\s*[】］]')
    STYLE_KEY = re.compile(r'(?<![\d.])(\d{1,3})\s*[【［]\s*答案\s*[】］]\s*([A-H])')
    # 事业单位解析：编号独占一行后接解析正文（“本题考查/第一空/题干…等”）
    STYLE_D = re.compile(r'(?:^|\n)\s*(\d{1,3})\s*\n\s*(?=\S)')
    # 事业单位解析：第【N】题 + 正确答案【X】
    STYLE_E = re.compile(r'第\s*[【［]\s*(\d{1,3})\s*[】］]\s*题')

    result = {}  # (section, no) -> {'answer','analysis','seq'}
    seq = 0
    total_style = 0
    for name, stext in sections:
        found = False
        # 风格A: N.A【解析】 / N.A［解析］ / N.A 【 解析 】
        amatches = list(STYLE_A.finditer(stext))
        if amatches:
            for i, m in enumerate(amatches):
                no = int(m.group(1))
                ans = m.group(2)
                body_end = amatches[i + 1].start() if i + 1 < len(amatches) else len(stext)
                body = stext[m.end():body_end].strip()
                seq += 1
                result[(name, no)] = {'answer': ans, 'analysis': body, 'seq': seq}
            found = True
        else:
            # 风格KEY: N【答案】X
            kmatches = list(STYLE_KEY.finditer(stext))
            if kmatches:
                for i, m in enumerate(kmatches):
                    no = int(m.group(1))
                    ans = m.group(2)
                    body_end = kmatches[i + 1].start() if i + 1 < len(kmatches) else len(stext)
                    body = stext[m.end():body_end].strip()
                    seq += 1
                    result[(name, no)] = {'answer': ans, 'analysis': body, 'seq': seq}
                found = True
            else:
                # 依次尝试 E / D / B 三种编号风格，取命中最多的一种
                best = {}

                def _run_style(style):
                    out = {}
                    if style == 'E':
                        dmatches = list(STYLE_E.finditer(stext))
                        for i, m in enumerate(dmatches):
                            no = int(m.group(1))
                            body_end = dmatches[i + 1].start() if i + 1 < len(dmatches) else len(stext)
                            body = stext[m.end():body_end]
                            am = None
                            for pat in MARKERS:
                                mm = pat.search(body)
                                if mm:
                                    am = mm.group(1)
                                    break
                            if am:
                                out[(name, no)] = {'answer': am, 'analysis': body.strip()}
                    elif style == 'D':
                        dmatches = list(STYLE_D.finditer(stext))
                        for i, m in enumerate(dmatches):
                            no = int(m.group(1))
                            body_end = dmatches[i + 1].start() if i + 1 < len(dmatches) else len(stext)
                            body = stext[m.end():body_end]
                            am = None
                            for pat in MARKERS:
                                mm = pat.search(body)
                                if mm:
                                    am = mm.group(1)
                                    break
                            if am:
                                out[(name, no)] = {'answer': am, 'analysis': body.strip()}
                    else:
                        candidates = list(re.finditer(r'(?<![\d.])(\d{1,3})\s*[、.．]', stext))
                        for i, m in enumerate(candidates):
                            no = int(m.group(1))
                            body_end = candidates[i + 1].start() if i + 1 < len(candidates) else len(stext)
                            body = stext[m.end():body_end]
                            am = None
                            for pat in MARKERS:
                                mm = pat.search(body)
                                if mm:
                                    am = mm.group(1)
                                    break
                            if am:
                                out[(name, no)] = {'answer': am, 'analysis': body.strip()}
                    return out

                for style in (['E', 'D', 'B'] if prefer == 'D' else ['E', 'B', 'D']):
                    cand_res = _run_style(style)
                    if len(cand_res) > len(best):
                        best = cand_res
                for k, v in best.items():
                    seq += 1
                    result[k] = dict(v, seq=seq)
                found = bool(result)
        total_style += 1 if found else 0
    # 顺序兜底：题目编号完全缺失时（如 2021 副省答案卷），按解析块顺序编号
    if not result and total_style == 0:
        chunks = re.split(r'\n\s*解析\s*\n', text)
        if len(chunks) > 2:
            for idx, chunk in enumerate(chunks[1:], start=1):
                am = None
                for pat in MARKERS:
                    mm = pat.search(chunk)
                    if mm:
                        am = mm.group(1)
                        break
                if am:
                    seq += 1
                    result[(None, idx)] = {'answer': am, 'analysis': chunk.strip(), 'seq': seq}
    return result


def match_answers(questions, answers):
    """把答案合并进题目。返回 (matched_count, unmatched_questions)。"""
    if not answers:
        return 0, [(q['section'], q['no'], q['order']) for q in questions]
    keys = list(answers.keys())
    none_ratio = sum(1 for k in keys if k[0] is None) / len(keys)
    global_numbered = none_ratio >= 0.8
    # 部分旧卷 PDF 分节重新编号：统计各节在试卷中的最小题号作为偏移基准
    sec_min = {}
    for q in questions:
        sec_min.setdefault(q['section'], q['no'])
        sec_min[q['section']] = min(sec_min[q['section']], q['no'])
    matched = 0
    unmatched = []
    if global_numbered:
        # 试卷是否全卷连续编号
        nos = [q['no'] for q in questions]
        continuous = all(nos[i] < nos[i + 1] for i in range(len(nos) - 1))
        if not continuous:
            # 分节编号的旧卷：按出现顺序配对
            ans_by_seq = sorted(answers.values(), key=lambda v: v.get('seq', 0))
            qs_sorted = sorted(questions, key=lambda q: q['order'])
            for q, a in zip(qs_sorted, ans_by_seq):
                q['answer'] = a['answer']
                q['analysis'] = a.get('analysis', '')
                matched += 1
            for q in qs_sorted[len(ans_by_seq):]:
                unmatched.append((q['section'], q['no'], q['order']))
            return matched, unmatched
    for q in questions:
        if global_numbered:
            key = (None, q['no'])
        else:
            key = (q['section'], q['no'])
        if key in answers:
            q['answer'] = answers[key]['answer']
            q['analysis'] = answers[key].get('analysis', '')
            matched += 1
            continue
        if not global_numbered:
            # 尝试分节偏移（PDF 该节从 1 编号，试卷从 sec_min 编号）
            base = sec_min.get(q['section'])
            if base and base > 1:
                alt = (q['section'], q['no'] - base + 1)
                if alt in answers:
                    q['answer'] = answers[alt]['answer']
                    q['analysis'] = answers[alt].get('analysis', '')
                    matched += 1
                    continue
        unmatched.append((q['section'], q['no'], q['order']))
    return matched, unmatched


# ---------------- 主流程 ----------------

def export_paper(paper, papers_all):
    docx_path = os.path.join(DOCX_DIR, paper['docx'])
    parsed = parse_paper_docx(docx_path, paper['id'])
    # 图片复制
    img_dir = os.path.join(IMG_ROOT, paper['id'])
    os.makedirs(img_dir, exist_ok=True)
    used = set()
    for m in parsed['materials']:
        for f in re.findall(r'/exam-img/%s/([^"]+)' % paper['id'], m['html']):
            used.add(f)
    for q in parsed['questions']:
        for f in re.findall(r'/exam-img/%s/([^"]+)' % paper['id'], q['stem_html']):
            used.add(f)
        for o in q['options']:
            for f in re.findall(r'/exam-img/%s/([^"]+)' % paper['id'], o['html']):
                used.add(f)
    import zipfile
    with zipfile.ZipFile(docx_path) as z:
        for f in used:
            src = 'word/media/' + f
            try:
                data = z.read(src)
                with open(os.path.join(img_dir, f), 'wb') as fh:
                    fh.write(data)
            except KeyError:
                pass
    # 答案合并
    answers = {}
    if paper['pdf']:
        pdf_path = os.path.join(ANSWER_DIR, paper['pdf'])
        if os.path.exists(pdf_path):
            answers = parse_answers_pdf(pdf_path)
    matched, unmatched = match_answers(parsed['questions'], answers)
    out = {
        'id': paper['id'], 'year': paper['year'], 'version': paper['version'],
        'title': paper['title'], 'docx': paper['docx'], 'pdf': paper['pdf'],
        'materials': parsed['materials'], 'questions': parsed['questions'],
        'stats': {'questions': len(parsed['questions']),
                  'materials': len(parsed['materials']),
                  'matched_answers': matched,
                  'unmatched': unmatched[:20]},
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, paper['id'] + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def main():
    papers = scan_papers()
    if len(sys.argv) < 2 or sys.argv[1] == 'scan':
        print(json.dumps([{'id': p['id'], 'year': p['year'], 'version': p['version'],
                           'title': p['title'], 'pdf': p['pdf']} for p in papers],
                         ensure_ascii=False, indent=1))
        return
    if sys.argv[1] == 'paper':
        pid = sys.argv[2]
        paper = next((p for p in papers if p['id'] == pid), None)
        if not paper:
            print('paper not found:', pid)
            return
        out = export_paper(paper, papers)
        print(json.dumps(out['stats'], ensure_ascii=False))
        return
    if sys.argv[1] == 'all':
        total = {'questions': 0, 'materials': 0, 'matched': 0}
        for p in papers:
            try:
                out = export_paper(p, papers)
                st = out['stats']
                total['questions'] += st['questions']
                total['materials'] += st['materials']
                total['matched'] += st['matched_answers']
                print('%s Q=%d M=%d 答案=%d/%d %s' % (
                    p['id'], st['questions'], st['materials'], st['matched_answers'],
                    st['questions'], ('UNMATCHED:' + str(st['unmatched'][:3])) if st['unmatched'] else 'OK'))
            except Exception as e:
                print('%s ERROR: %s' % (p['id'], e))
        print('TOTAL', total)


if __name__ == '__main__':
    main()
