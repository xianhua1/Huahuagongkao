# -*- coding: utf-8 -*-
"""验证：材料详情接口 + 编辑题目全字段（题干/选项/材料/答案/解析）+ 还原"""
import json
import subprocess
import urllib.request

BASE = 'http://127.0.0.1:8090/prod-api'
MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'


def http(method, path, token=None, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    data = json.dumps(body).encode() if body is not None else None
    if data:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, data=data, timeout=30) as r:
        return json.loads(r.read().decode())


def mysql(sql):
    r = subprocess.run([MYSQL, '-u', 'root', '-p123456', '--default-character-set=utf8mb4',
                        'ruoyi', '-N', '-e', sql], capture_output=True, text=True)
    return r.stdout.strip()


t = http('POST', '/login', body={'username': 'admin', 'password': 'admin123'})['token']

# 1) 材料详情接口
d = http('GET', '/exam/paper/42', t)
q = next(x for x in d['data']['questions'] if x['materialId'])
mat = http('GET', '/exam/material/' + str(q['materialId']), t)
print('material get:', mat['code'], 'len:', len(mat['data']['content']))

# 2) 编辑题目（全字段）
qid = q['id']
upd = http('PUT', '/exam/question', t, {
    'id': qid, 'section': q['section'], 'stem': '<p>测试编辑题干</p>',
    'options': json.dumps([{'label': 'A', 'html': '新A'}, {'label': 'B', 'html': '新B'}]),
    'answer': 'B', 'analysis': '测试编辑解析',
    'materialId': q['materialId'], 'materialContent': '<p>测试编辑材料</p>', 'materialTitle': ''
})
print('update:', upd['code'])

# 3) 校验
print('db:', mysql('SELECT LEFT(stem,15), answer, has_image FROM exam_question WHERE id=' + str(qid) +
                  '; SELECT LEFT(content,15) FROM exam_material WHERE id=' + str(q['materialId']) + ';')
      .replace('\n', ' | '))

# 4) 还原原题
d2 = http('GET', '/exam/paper/42', t)
q2 = next(x for x in d2['data']['questions'] if x['id'] == qid)
http('PUT', '/exam/question', t, {
    'id': qid, 'section': q2['section'], 'stem': q2['stem'], 'options': q2['options'],
    'answer': q2['answer'], 'analysis': q2['analysis'],
    'materialId': q['materialId'], 'materialContent': mat['data']['content'], 'materialTitle': ''
})
print('restored')
