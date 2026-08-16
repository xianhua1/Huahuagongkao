# -*- coding: utf-8 -*-
"""事业单位联考职测真题解析入库管线。
来源：D:\\BaiduNetdiskDownload\\事业单位\\渠道一/二/三
- 题本 PDF：pymupdf 按版面顺序提取文本块与图片 -> 复用 parse_all 的题目解析
- 解析 PDF：复用 parse_answers_pdf
输出：data/parsed_sydw/<code>.json + data/images_sydw/<code>/
用法：
  python parse_sydw.py scan       # 打印清单
  python parse_sydw.py paper <code>
  python parse_sydw.py all
"""
import os
import re
import sys
import json
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse_all as P

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(BASE), 'data')
ROOT = r'D:\BaiduNetdiskDownload\事业单位'
OUT_DIR = os.path.join(DATA, 'parsed_sydw')
IMG_ROOT = os.path.join(DATA, 'images_sydw')

CATS = ['A类', 'B类', 'C类', 'D类', 'E类']


def find_files():
    """扫描三个渠道，返回 [(code, year, cat, title, 题本, 解析, source)]，按渠道优先级去重。"""
    found = {}

    def add(cat, year, mday, title, tiben, jiexi, src, adir=None):
        key = (cat, year, mday)
        if key in found:
            return  # 优先渠道二（先扫描渠道二）
        code = 'sydw-%s-%d-%02d' % (cat.replace('类', ''), year, mday)
        found[key] = {'code': code, 'year': year, 'cat': cat, 'title': title,
                      'tiben': tiben, 'jiexi': jiexi, 'src': src, 'adir': adir}

    def ymday(name):
        """从文件名提取 (year, mday)。"""
        m = re.search(r'(20\d{2})', name)
        year = int(m.group(1)) if m else 0
        m2 = re.search(r'(\d{1,2})月(\d{1,2})日', name)
        if m2:
            return year, int(m2.group(1)) * 100 + int(m2.group(2))
        if '上半年' in name:
            return year, 1
        if '下半年' in name:
            return year, 2
        return year, 99

    # 渠道二：优先
    for cat in CATS:
        q2 = os.path.join(ROOT, '渠道二', '%s类真题' % cat)
        if not os.path.isdir(q2):
            # 匹配形如 "3.全国事业单位联考C类真题35套（2015-2024）"
            cand = [d for d in os.listdir(os.path.join(ROOT, '渠道二'))
                    if cat in d and os.path.isdir(os.path.join(ROOT, '渠道二', d))]
            q2 = os.path.join(ROOT, '渠道二', cand[0]) if cand else None
        if not q2 or not os.path.isdir(q2):
            continue
        for d1 in os.listdir(q2):
            p1 = os.path.join(q2, d1)
            if not os.path.isdir(p1) or ('职测' not in d1 and '职业能力' not in d1):
                continue
            tdir = os.path.join(p1, '题目')
            adir = os.path.join(p1, '答案解析')
            if not os.path.isdir(tdir):
                continue
            for f in sorted(os.listdir(tdir)):
                if not f.lower().endswith(('.pdf', '.docx')):
                    continue
                if '职测' not in f and '职业能力' not in f:
                    continue
                year, mday = ymday(f)
                base = re.sub(r'（.*?）|\(.*?\)|《.*?》', '', f)
                title = os.path.splitext(f)[0]
                jiexi = None
                if os.path.isdir(adir):
                    # 找同名解析：比对年月
                    for af in sorted(os.listdir(adir)):
                        ay, am = ymday(af)
                        if ay == year and am == mday and '答案' in af:
                            jiexi = os.path.join(adir, af)
                            break
                add(cat, year, mday, title, os.path.join(tdir, f), jiexi, '渠道二', adir)

    # 渠道三：补齐
    for cat in CATS:
        q3 = os.path.join(ROOT, '渠道三', '联考' + cat)
        if not os.path.isdir(q3):
            continue
        for f in sorted(os.listdir(q3)):
            if '职业能力' not in f or not f.lower().endswith('.pdf'):
                continue
            if '默写' in f or '公共基础' in f:
                continue
            year, mday = ymday(f)
            if (cat, year, mday) in found:
                continue
            title = os.path.splitext(f)[0]
            jiexi = None
            for af in sorted(os.listdir(q3)):
                if af == f or '职业能力' not in af:
                    continue
                ay, am = ymday(af)
                if ay == year and am == mday and ('解析' in af or '答案' in af):
                    jiexi = os.path.join(q3, af)
                    break
            add(cat, year, mday, title, os.path.join(q3, f), jiexi, '渠道三')

    # 渠道一：补齐
    for cat in CATS:
        q1 = os.path.join(ROOT, '渠道一', cat, cat + '职测')
        if not os.path.isdir(q1):
            continue
        tiben = None
        jiexi = None
        for f in sorted(os.listdir(q1)):
            if not f.lower().endswith('.pdf'):
                continue
            if '解析' in f:
                jiexi = os.path.join(q1, f)
            else:
                tiben = os.path.join(q1, f)
        if not tiben:
            continue
        year, mday = ymday(os.path.basename(tiben))
        if (cat, year, mday) in found:
            continue
        add(cat, year, mday, os.path.splitext(os.path.basename(tiben))[0], tiben, jiexi, '渠道一')

    return sorted(found.values(), key=lambda p: (p['year'], p['cat'], p['code']))


def pdf_blocks(path, img_dir, code):
    """pymupdf 按版面顺序提取文本块与图片 -> parse_all 的 block 结构。"""
    import pymupdf
    doc = pymupdf.open(path)
    blocks = []
    img_idx = 0
    seen_xref = {}
    for pno in range(doc.page_count):
        page = doc[pno]
        ph = page.rect.height
        items = []
        d = page.get_text('dict')
        for b in d.get('blocks', []):
            if b.get('type') != 0:
                continue
            # 行间保留换行（题号常独占一行）
            txt = '\n'.join(
                ''.join(s['text'] for s in l.get('spans', []))
                for l in b.get('lines', []))
            txt = txt.strip().replace('\u200b', '')
            if not txt:
                continue
            # 页边纯数字（页码）跳过；页面中间的独立数字多为题号
            if re.match(r'^\d{1,3}$', txt):
                y0, y1 = b['bbox'][1], b['bbox'][3]
                if y0 > ph * 0.9 or y1 < ph * 0.1:
                    continue
            if '上岸' in txt or 'saztk' in txt or '更多真题' in txt or 'www.' in txt:
                continue
            items.append((b['bbox'][1], b['bbox'][0], 'text', txt))
        for img in page.get_images(full=True):
            xref = img[0]
            rects = page.get_image_rects(xref)
            if not rects:
                continue
            bbox = rects[0]
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w < 8 or h < 8:
                continue
            if xref in seen_xref:
                fname = seen_xref[xref]
            else:
                img_idx += 1
                fname = '%s-p%02d-i%02d.png' % (code, pno + 1, img_idx)
                try:
                    # 用渲染方式提取，保证颜色/透明度正确（直接取流可能颜色反转）
                    from PIL import Image
                    pix = page.get_pixmap(clip=bbox, matrix=pymupdf.Matrix(3, 3))
                    mode = 'RGBA' if pix.n == 4 else 'RGB'
                    im = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
                    im.save(os.path.join(img_dir, fname))
                    seen_xref[xref] = fname
                except Exception:
                    fname = None
            if fname:
                items.append((bbox[1], bbox[0], 'img', fname))
        items.sort(key=lambda x: (x[0], x[1]))
        for _, _, kind, val in items:
            if kind == 'text':
                blocks.append(('p', [('t', val)]))
            else:
                blocks.append(('p', [('img', val)]))
    doc.close()
    return blocks


def pdf_text_filtered(path):
    """pymupdf 提取全文，过滤页边页码与水印，行间保留换行。"""
    import pymupdf
    doc = pymupdf.open(path)
    out = []
    for pno in range(doc.page_count):
        page = doc[pno]
        ph = page.rect.height
        d = page.get_text('dict')
        page_lines = []
        for b in d.get('blocks', []):
            if b.get('type') != 0:
                continue
            txt = '\n'.join(
                ''.join(s['text'] for s in l.get('spans', []))
                for l in b.get('lines', []))
            txt = txt.strip().replace('\u200b', '')
            if not txt:
                continue
            if re.match(r'^\d{1,3}$', txt):
                y0, y1 = b['bbox'][1], b['bbox'][3]
                if y0 > ph * 0.9 or y1 < ph * 0.1:
                    continue
            if '上岸' in txt or 'saztk' in txt or '更多真题' in txt or 'www.' in txt:
                continue
            page_lines.append(txt)
        out.append('\n'.join(page_lines))
    doc.close()
    return '\n'.join(out)


def export_paper(paper):
    code = paper['code']
    img_dir = os.path.join(IMG_ROOT, code)
    os.makedirs(img_dir, exist_ok=True)
    if paper['tiben'].lower().endswith('.docx'):
        # 复用 docx 管线（自动提取图片到 images/）
        import shutil
        docx_dir = os.path.join(DATA, 'sydw_docx')
        os.makedirs(docx_dir, exist_ok=True)
        tmp = os.path.join(docx_dir, code + '.docx')
        shutil.copy(paper['tiben'], tmp)
        parsed = P.parse_paper_docx(tmp, code)
        # 复制图片
        import zipfile
        used = set(re.findall(r'/exam-img/%s/([^"]+)' % code, json.dumps(parsed, ensure_ascii=False)))
        with zipfile.ZipFile(tmp) as z:
            for f in used:
                f = f.replace('\\', '')
                try:
                    with open(os.path.join(img_dir, f), 'wb') as fh:
                        fh.write(z.read('word/media/' + f))
                except KeyError:
                    pass
    else:
        parsed = P.parse_question_blocks(pdf_blocks(paper['tiben'], img_dir, code), code)
        # 把图片引用统一为 /exam-img/<code>/...
        def fix_html(h):
            return re.sub(r'/exam-img/[^/]+/([^"]+)', r'/exam-img/%s/\1' % code, h or '')
        for m in parsed['materials']:
            m['html'] = fix_html(m['html'])
        for q in parsed['questions']:
            q['stem_html'] = fix_html(q['stem_html'])
            for o in q['options']:
                o['html'] = fix_html(o['html'])
    answers = {}
    if paper.get('jiexi') and os.path.exists(paper['jiexi']):
        # 优先用可提取出文本的解析文件（同名文件可能有的扫描版、有的文字版）
        jiexi_files = [paper['jiexi']]
        if paper.get('adir') and os.path.isdir(paper['adir']):
            for af in sorted(os.listdir(paper['adir'])):
                p = os.path.join(paper['adir'], af)
                if p not in jiexi_files and af.lower().endswith('.pdf') and '答案' in af:
                    jiexi_files.append(p)
        chosen = None
        for jf in jiexi_files:
            try:
                if jf.lower().endswith('.pdf') and len(pdf_text_filtered(jf)) > 200:
                    chosen = jf
                    break
            except Exception:
                continue
        if chosen is None:
            chosen = paper['jiexi']
        if chosen:
            if chosen.lower().endswith('.pdf'):
                answers = P._parse_answer_text(pdf_text_filtered(chosen), prefer='D')
            else:
                answers = P.parse_answers_pdf(chosen)
    matched, unmatched = P.match_answers(parsed['questions'], answers)
    out = {
        'id': code, 'year': paper['year'], 'cat': paper['cat'], 'title': paper['title'],
        'src': paper['src'],
        'materials': parsed['materials'], 'questions': parsed['questions'],
        'stats': {'questions': len(parsed['questions']), 'materials': len(parsed['materials']),
                  'matched': matched, 'unmatched': unmatched[:10]},
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, code + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def main():
    papers = find_files()
    if len(sys.argv) < 2 or sys.argv[1] == 'scan':
        print(json.dumps([{'code': p['code'], 'year': p['year'], 'cat': p['cat'],
                           'src': p['src'], 'jiexi': bool(p['jiexi']),
                           'title': p['title'][:40]} for p in papers], ensure_ascii=False, indent=1))
        return
    if sys.argv[1] == 'paper':
        code = sys.argv[2]
        p = next((x for x in papers if x['code'] == code), None)
        if not p:
            print('not found:', code)
            return
        out = export_paper(p)
        print(json.dumps(out['stats'], ensure_ascii=False))
        return
    if sys.argv[1] == 'all':
        ok = 0
        for p in papers:
            try:
                out = export_paper(p)
                st = out['stats']
                print('%s %s %s Q=%d M=%d 答案=%d/%d %s' % (
                    p['code'], p['cat'], p['src'], st['questions'], st['materials'],
                    st['matched'], st['questions'],
                    ('UNMATCHED:' + str(st['unmatched'][:3])) if st['unmatched'] else 'OK'))
                ok += 1
            except Exception as e:
                print('%s ERROR: %s' % (p['code'], e))
        print('DONE', ok, '/', len(papers))


if __name__ == '__main__':
    main()
