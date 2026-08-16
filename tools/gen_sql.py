# -*- coding: utf-8 -*-
"""把 parsed/*.json 生成为 exam_*.sql 导入文件。"""
import os
import json
import glob

BASE = os.path.dirname(os.path.abspath(__file__))
PARSED = os.path.join(os.path.dirname(BASE), 'data', 'parsed')
OUT = os.path.join(os.path.dirname(BASE), 'data', 'sql')
os.makedirs(OUT, exist_ok=True)

SECTION_ORDER = {'常识判断': 1, '言语理解与表达': 2, '数量关系': 3, '判断推理': 4, '资料分析': 5, '知觉速度与准确性': 0}

def esc(v):
    if v is None:
        return 'NULL'
    return "'" + str(v).replace('\\', '\\\\').replace("'", "''") + "'"


def main():
    papers = []
    for base in ('parsed', 'parsed_sydw'):
        for f in sorted(glob.glob(os.path.join(os.path.dirname(BASE), 'data', base, '*.json'))):
            with open(f, encoding='utf-8') as fh:
                papers.append(json.load(fh))
    papers.sort(key=lambda p: (p.get('subject', '行测') != '行测', p['year'], p.get('cat', p.get('version', ''))))

    lines = []
    lines.append('-- 国考行测 2000-2022 + 事业单位职测 真题题库导入脚本')
    lines.append('SET NAMES utf8mb4;')
    lines.append('SET FOREIGN_KEY_CHECKS=0;')
    lines.append('TRUNCATE TABLE exam_record;')
    lines.append('TRUNCATE TABLE exam_question;')
    lines.append('TRUNCATE TABLE exam_material;')
    lines.append('TRUNCATE TABLE exam_paper;')

    paper_id_map = {}
    for p in papers:
        pid = len(paper_id_map) + 1
        paper_id_map[p['id']] = pid
        subject = '职测' if p.get('cat') else '行测'
        version = p.get('cat') or p.get('version', '')
        lines.append("INSERT INTO exam_paper (id, paper_code, title, year, version, subject, question_count) VALUES "
                     "(%d, %s, %s, %d, %s, %s, %d);" % (
                         pid, esc(p['id']), esc(p['title']), p.get('year', 0), esc(version),
                         esc(subject), len(p['questions'])))
    lines.append('')

    mat_id_map = {}
    for p in papers:
        pid = paper_id_map[p['id']]
        for m in p['materials']:
            if not m['html'].strip() and not m['title']:
                continue
            mid = len(mat_id_map) + 1
            mat_id_map[m['id']] = mid
            content = m['html']
            title = m['title'] or ''
            lines.append("INSERT INTO exam_material (id, paper_id, section, title, content, sort_order) VALUES "
                         "(%d, %d, %s, %s, %s, %d);" % (
                             mid, pid, esc(m['section']), esc(title), esc(content), m['order']))
    lines.append('')

    qid = 0
    for p in papers:
        pid = paper_id_map[p['id']]
        for q in p['questions']:
            qid += 1
            mid = mat_id_map.get(q['material']['id']) if q.get('material') else None
            if mid is None:
                mid = 'NULL'
            options = json.dumps(q['options'], ensure_ascii=False)
            has_img = 1 if ('<img' in q['stem_html'] or any('<img' in o['html'] for o in q['options'])) else 0
            lines.append("INSERT INTO exam_question (id, paper_id, material_id, section, qno, qorder, stem, options, answer, analysis, has_image) VALUES "
                         "(%d, %d, %s, %s, %d, %d, %s, %s, %s, %s, %d);" % (
                             qid, pid, mid, esc(q['section']), q['no'], q['order'],
                             esc(q['stem_html']), esc(options),
                             esc(q.get('answer', '')), esc(q.get('analysis', '')), has_img))
    lines.append('')
    lines.append('SET FOREIGN_KEY_CHECKS=1;')

    with open(os.path.join(OUT, 'exam_data.sql'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    print('papers:', len(papers), 'materials:', len(mat_id_map), 'questions:', qid)
    print('written:', os.path.join(OUT, 'exam_data.sql'))


if __name__ == '__main__':
    main()
