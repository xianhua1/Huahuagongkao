# -*- coding: utf-8 -*-
"""从题库中提取各知识点教学例题，输出 JSON 供资料文档使用。"""
import subprocess, json, re, os

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'
OUT = r'C:\Users\admin\DSH\tools\data\doc_examples.json'

def q(alias_sql):
    cmd = [MYSQL, '-u', 'root', '-p123456', '--default-character-set=utf8mb4', '-N', '-B', 'ruoyi', '-e', alias_sql]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.stdout

def rows(sql):
    out = q(sql)
    lines = [l for l in out.splitlines() if l.strip()]
    return [l.split('\t') for l in lines]

def clean(s):
    if s is None: return ''
    s = re.sub(r'<img[^>]*>', '【图】', s)
    s = re.sub(r'<[^>]+>', '', s)
    return s.strip()

def fetch(topic, cond, limit=2, order='RAND()'):
    sql = ("SELECT p.paper_code, q.qno, q.section, q.stem, q.options, q.answer, q.analysis "
           "FROM exam_question q JOIN exam_paper p ON p.id=q.paper_id "
           "WHERE p.subject='行测' AND q.answer<>'' AND CHAR_LENGTH(q.analysis)>40 AND %s "
           "ORDER BY %s LIMIT %d") % (cond, order, limit)
    res = []
    for r in rows(sql):
        if len(r) < 7: continue
        paper, qno, section, stem, options, ans, ana = r[:7]
        try:
            raw_opts = json.loads(options) if options else []
        except Exception:
            raw_opts = []
        opt_map = {}
        if isinstance(raw_opts, dict):
            opt_map = {k: clean(v) for k, v in raw_opts.items()}
        elif isinstance(raw_opts, list):
            for o in raw_opts:
                if isinstance(o, dict) and 'label' in o:
                    opt_map[str(o['label'])] = clean(o.get('html', ''))
        res.append({
            'paper': paper, 'qno': qno, 'section': section,
            'stem': clean(stem), 'options': opt_map,
            'answer': ans, 'analysis': clean(ana)
        })
    return res

def fetch_material(paper_code, section):
    sql = ("SELECT m.content FROM exam_material m JOIN exam_paper p ON p.id=m.paper_id "
           "WHERE p.paper_code='%s' AND m.section LIKE '%%%s%%' LIMIT 1") % (paper_code, section)
    out = q(sql)
    return clean(out)

data = {
 'shuliang_gongcheng': fetch('工程', "q.section='数量关系' AND (q.stem LIKE '%工程%' OR q.stem LIKE '%效率%' OR q.stem LIKE '%工作量%')"),
 'shuliang_xingcheng': fetch('行程', "q.section='数量关系' AND (q.stem LIKE '%追上%' OR q.stem LIKE '%相遇%' OR q.stem LIKE '%速度%')"),
 'shuliang_rongchi': fetch('容斥', "q.section='数量关系' AND (q.stem LIKE '%至少%' OR q.stem LIKE '%两种%' OR q.stem LIKE '%都参加%')"),
 'shuliang_lirun': fetch('利润', "q.section='数量关系' AND (q.stem LIKE '%利润%' OR q.stem LIKE '%折扣%' OR q.stem LIKE '%售价%')"),
 'shuliang_pailie': fetch('排列组合', "q.section='数量关系' AND (q.stem LIKE '%多少种%' OR q.stem LIKE '%种安排%' OR q.stem LIKE '%种方式%')"),
 'shuliang_gailv': fetch('概率', "q.section='数量关系' AND q.stem LIKE '%概率%'"),
 'shuliang_jihe': fetch('几何', "q.section='数量关系' AND (q.stem LIKE '%面积%' OR q.stem LIKE '%周长%' OR q.stem LIKE '%体积%' OR q.stem LIKE '%半径%')"),
 'shuliang_hechabei': fetch('和差倍比', "q.section='数量关系' AND (q.stem LIKE '%倍%' OR q.stem LIKE '%比%多%')"),
 'yanyu_zhongxin': fetch('中心理解', "q.section='言语理解与表达' AND (q.stem LIKE '%主旨%' OR q.stem LIKE '%意在%' OR q.stem LIKE '%主要说明%' OR q.stem LIKE '%概括最%')"),
 'yanyu_tiankong': fetch('逻辑填空', "q.section='言语理解与表达' AND (q.stem LIKE '%填入%最恰当%' OR q.stem LIKE '%依次填入%')"),
 'yanyu_paixu': fetch('语句排序', "q.section='言语理解与表达' AND (q.stem LIKE '%语序%' OR q.stem LIKE '%排列最%')"),
 'yanyu_xijie': fetch('细节判断', "q.section='言语理解与表达' AND (q.stem LIKE '%正确的一项是%' OR q.stem LIKE '%符合文意%' OR q.stem LIKE '%可以推出%')"),
 'panduan_tuxing': fetch('图形推理', "q.section='判断推理' AND q.stem LIKE '%规律%'"),
 'panduan_dingyi': fetch('定义判断', "q.section='判断推理' AND (q.stem LIKE '%属于%' OR q.stem LIKE '%符合%定义%')"),
 'panduan_leibi': fetch('类比推理', "q.section='判断推理' AND (q.stem LIKE '%最为相似%' OR q.stem LIKE '%之于%')"),
 'panduan_jiaqiang': fetch('加强', "q.section='判断推理' AND (q.stem LIKE '%最能加强%' OR q.stem LIKE '%最能支持%')"),
 'panduan_xueruo': fetch('削弱', "q.section='判断推理' AND q.stem LIKE '%最能削弱%'"),
 'panduan_tuili': fetch('翻译推理', "q.section='判断推理' AND (q.stem LIKE '%可以推出%' OR q.stem LIKE '%由此可以%')"),
 'changshi_falv': fetch('常识法律', "q.section='常识判断' AND (q.stem LIKE '%法律%' OR q.stem LIKE '%宪法%' OR q.stem LIKE '%民法%' OR q.stem LIKE '%刑法%')"),
 'changshi_keji': fetch('常识科技', "q.section='常识判断' AND (q.stem LIKE '%卫星%' OR q.stem LIKE '%科技%' OR q.stem LIKE '%物理%' OR q.stem LIKE '%化学%')"),
 'changshi_lishi': fetch('常识历史', "q.section='常识判断' AND (q.stem LIKE '%朝代%' OR q.stem LIKE '%战役%' OR q.stem LIKE '%历史%' OR q.stem LIKE '%古代%')"),
 'ziliao_analysis': fetch('资料分析', "q.section='资料分析' AND (q.stem LIKE '%增长%' OR q.stem LIKE '%同比%' OR q.stem LIKE '%比重%')", limit=4),
}

# 资料分析配套材料（用有材料的试卷）
mat_paper = None
for ex in data['ziliao_analysis']:
    m = fetch_material(ex['paper'], '资料分析')
    if m and len(m) > 40:
        mat_paper = ex['paper']
        data['ziliao_material'] = {'paper': mat_paper, 'content': m[:600]}
        break
if 'ziliao_material' not in data:
    data['ziliao_material'] = {'paper': None, 'content': ''}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print('keys:', list(data.keys()))
print('counts:', {k: len(v) for k, v in data.items() if isinstance(v, list)})
