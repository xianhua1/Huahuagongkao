# -*- coding: utf-8 -*-
"""端到端验证：上传图片 -> 新增题目（含材料+图片）-> 校验 -> 清理"""
import json
import uuid
import urllib.request

BASE = 'http://127.0.0.1:8090/prod-api'


def http(method, path, token=None, body=None, ctype='application/json'):
    req = urllib.request.Request(BASE + path, method=method)
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    data = None
    if body is not None:
        data = body if isinstance(body, bytes) else json.dumps(body).encode('utf-8')
        req.add_header('Content-Type', ctype)
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')


# 1) 登录
st, resp = http('POST', '/login', body={'username': 'admin', 'password': 'admin123'})
token = json.loads(resp)['token']
print('login ok')

# 2) 上传图片（multipart）
import base64
png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
boundary = uuid.uuid4().hex
parts = []
parts.append(('--%s\r\nContent-Disposition: form-data; name="file"; filename="t.png"\r\n'
              'Content-Type: image/png\r\n\r\n' % boundary).encode())
parts.append(png)
parts.append(('\r\n--%s--\r\n' % boundary).encode())
mp_body = b''.join(parts)
st, resp = http('POST', '/common/upload', token, mp_body, 'multipart/form-data; boundary=' + boundary)
up = json.loads(resp)
url = up.get('fileName')
print('upload:', st, url)

# 3) 新增题目（题干/选项/材料/解析都带图）
payload = {
    'paperId': 1, 'section': '常识判断',
    'stem': '<p>测试题：图片上传验证</p><img src="%s"/>' % url,
    'options': json.dumps([{'label': 'A', 'html': '正确'}, {'label': 'B', 'html': '错误'}]),
    'answer': 'A',
    'analysis': '测试解析<img src="%s"/>' % url,
    'materialContent': '<p>测试材料内容</p><img src="%s"/>' % url,
    'materialTitle': '',
}
st, resp = http('POST', '/exam/question', token, payload)
print('add:', st, resp[:80])

# 4) 校验：题目与材料
import subprocess
q = subprocess.run([r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe', '-u', 'root', '-p123456',
                    '--default-character-set=utf8mb4', 'ruoyi', '-N', '-e',
                    "SELECT q.id, q.material_id, m.id FROM exam_question q LEFT JOIN exam_material m ON m.id=q.material_id WHERE q.stem LIKE '%图片上传验证%';"],
                   capture_output=True, text=True)
print('db check:', q.stdout.strip())

# 5) 图片可访问
st, resp = http('GET', url)
print('img via proxy:', st, len(resp))

# 6) 清理
subprocess.run([r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe', '-u', 'root', '-p123456', 'ruoyi', '-e',
                "DELETE q FROM exam_question q WHERE q.stem LIKE '%图片上传验证%';"
                "DELETE m FROM exam_material m WHERE m.content LIKE '%测试材料内容%';"],
               capture_output=True, text=True)
print('cleaned')
