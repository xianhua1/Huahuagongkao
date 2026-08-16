# -*- coding: utf-8 -*-
"""验证：自定义新增试卷 -> 往新试卷加题 -> 清理"""
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

# 1) 新建自定义试卷
r = http('POST', '/exam/paper', t, {'title': '2026年自定义模拟卷', 'year': 2026, 'subject': '行测', 'version': '自定义'})
new_id = r['data']
print('add paper:', r['code'], 'new id =', new_id)

# 2) 往新试卷加一道题
r2 = http('POST', '/exam/question', t, {
    'paperId': new_id, 'section': '常识判断', 'stem': '<p>自定义卷测试题</p>',
    'options': '[{"label":"A","html":"对"},{"label":"B","html":"错"}]',
    'answer': 'A', 'analysis': '解析'})
print('add question:', r2['code'])

# 3) 校验
print('db:', mysql("SELECT p.title, q.qorder, LEFT(q.stem,20) FROM exam_question q "
                   "JOIN exam_paper p ON p.id=q.paper_id WHERE q.paper_id=" + str(new_id)))

# 4) 清理
mysql("DELETE FROM exam_question WHERE paper_id=" + str(new_id) +
      "; DELETE FROM exam_paper WHERE id=" + str(new_id) + ";")
print('cleaned')
