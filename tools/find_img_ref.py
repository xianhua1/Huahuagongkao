# -*- coding: utf-8 -*-
"""找到缺失图片的完整引用上下文：输出含 img35.png 的 stem/analysis 片段"""
import os, re, subprocess

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'

rows = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi',
                       '-e', "SELECT p.paper_code, q.stem, q.analysis FROM exam_question q JOIN exam_paper p ON p.id=q.paper_id WHERE (q.stem LIKE '%2022-gk-xzf/img35%' OR q.analysis LIKE '%2022-gk-xzf/img35%') LIMIT 3"],
                      capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
print('rows:', rows[:1500] if rows else '(空)')
print()

# 也可能引用的 URL 是绝对路径形式，全表搜 img35
rows2 = subprocess.run([MYSQL, '-u', 'root', '-p123456', '-N', '-B', '--default-character-set=utf8mb4', 'ruoyi',
                        '-e', "SELECT p.paper_code, LEFT(q.stem, 300) FROM exam_question q JOIN exam_paper p ON p.id=q.paper_id WHERE q.stem LIKE '%img35%' LIMIT 5"],
                       capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
print('img35 出现处:')
print(rows2[:2000] if rows2 else '(空)')
