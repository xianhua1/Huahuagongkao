# -*- coding: utf-8 -*-
"""沙盒拉取 vs 本地提交源 vs 真实运行代码 的一致性哈希对比"""
import os, hashlib, sys

def tree_hash(root):
    m = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, root).replace('\\', '/')
            with open(p, 'rb') as fh:
                m[rel] = hashlib.sha1(fh.read()).hexdigest()
    return m

sandbox = r'C:\Users\admin\DSH\verify-clone'
source = r'C:\Users\admin\DSH\Huahuagongkao'

# 第1步：GitHub 拉取 vs 本地提交源
a = tree_hash(sandbox)
b = tree_hash(source)
diff = []
for k in a:
    if k not in b: diff.append('仅沙盒有: ' + k)
    elif a[k] != b[k]: diff.append('内容不同: ' + k)
for k in b:
    if k not in a: diff.append('仅本地提交源有: ' + k)
print('【第1步】GitHub拉取 vs 本地提交源: 共 %d 个文件' % len(a))
if diff:
    for d in diff[:15]: print('  !', d)
else:
    print('  ✓ 100% 一致，无任何差异')

# 第2步：本地提交源 vs 真实运行代码
checks = [
    ('ruoyi/src', r'C:\Users\admin\DSH\ruoyi\src'),
    ('ruoyi/public/docs', r'C:\Users\admin\DSH\ruoyi\public\docs'),
    ('ruoyi/server.cjs', r'C:\Users\admin\DSH\ruoyi\server.cjs'),
    ('ruoyi/vite.config.js', r'C:\Users\admin\DSH\ruoyi\vite.config.js'),
    ('ruoyi/package.json', r'C:\Users\admin\DSH\ruoyi\package.json'),
    ('ruoyi/index.html', r'C:\Users\admin\DSH\ruoyi\index.html'),
    ('ruoyi/.env.production', r'C:\Users\admin\DSH\ruoyi\.env.production'),
    ('ruoyi-backend/ruoyi-admin/src', r'C:\Users\admin\DSH\ruoyi-backend\ruoyi-admin\src'),
    ('ruoyi-backend/ruoyi-system/src', r'C:\Users\admin\DSH\ruoyi-backend\ruoyi-system\src'),
    ('ruoyi-backend/ruoyi-framework/src', r'C:\Users\admin\DSH\ruoyi-backend\ruoyi-framework\src'),
    ('ruoyi-backend/pom.xml', r'C:\Users\admin\DSH\ruoyi-backend\pom.xml'),
    ('tools', r'C:\Users\admin\DSH\tools'),
    ('data/sql', r'C:\Users\admin\DSH\data\sql'),
    ('start-all.bat', r'C:\Users\admin\DSH\start-all.bat'),
]
print('【第2步】本地提交源 vs 真实运行代码:')
for rel, real in checks:
    sp = os.path.join(source, rel)
    if os.path.isdir(sp):
        m1 = tree_hash(sp)
        m2 = tree_hash(real) if os.path.isdir(real) else {}
        bad = [k for k in m1 if k not in m2 or m2[k] != m1[k]] + [k for k in m2 if k not in m1]
        if bad:
            print('  ! %s: %d 处差异' % (rel, len(bad)))
            for x in bad[:3]: print('      -', x)
        else:
            print('  OK %s: 一致 (%d 文件)' % (rel, len(m1)))
    else:
        h1 = hashlib.sha1(open(sp, 'rb').read()).hexdigest()
        h2 = hashlib.sha1(open(real, 'rb').read()).hexdigest()
        print('  OK %s: 一致' % rel if h1 == h2 else '  ! %s: 内容不同!' % rel)
