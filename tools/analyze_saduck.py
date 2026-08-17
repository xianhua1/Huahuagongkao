# -*- coding: utf-8 -*-
"""分析 saduck 题目 JSON 完整结构，对比我们的 exam_question 格式"""
import json

data = json.load(open(r'C:\Users\admin\DSH\data\saduck_sample_raw.json', encoding='utf-8'))
print('题目总数:', len(data))

# 字段全集
keys = set()
for q in data:
    keys.update(q.keys())
print('字段:', sorted(keys))

# 第一条完整样例（普通题）
q0 = data[0]
print('\n--- 普通题样例 ---')
print('title:', q0.get('title', '')[:120])
print('type:', q0.get('type'), '| correctAnswer:', q0.get('correctAnswer'), '| tag:', q0.get('tag'))
print('options:', q0.get('options', '')[:80])
print('analysis:', q0.get('analysis', '')[:80])

# 找材料题（有 material 字段的）
mat_qs = [q for q in data if q.get('material')]
print('\n材料题数量:', len(mat_qs))
if mat_qs:
    mq = mat_qs[0]
    print('材料题字段:', sorted(mq.keys()))
    print('material 前 200:', str(mq.get('material'))[:200])
    print('该题 title:', mq.get('title', '')[:100])

# 图片检查
img_qs = [q for q in data if '<img' in (q.get('title') or '') + (q.get('material') or '') + (q.get('analysis') or '')]
print('\n含图片的题:', len(img_qs))
if img_qs:
    import re
    imgs = re.findall(r'src="([^"]+)"', img_qs[0].get('title') or '')
    print('图片 src 样例:', imgs[:3])

# 答案格式统计（数字索引分布）
import collections
ans_cnt = collections.Counter(q.get('correctAnswer') for q in data)
print('\n答案值分布:', dict(ans_cnt))

# type 分布
type_cnt = collections.Counter(q.get('type') for q in data)
print('题型分布:', dict(type_cnt))

# 其他可能字段样例
for q in data[:3]:
    extra = {k: v for k, v in q.items() if k not in ('id', 'title', 'type', 'globalAccuracy', 'correctAnswer', 'options', 'analysis', 'source', 'tag', 'material')}
    if extra:
        print('\n额外字段:', extra)
        break
