# -*- coding: utf-8 -*-
"""批量替换备考中心各页面头部为 PageHead 渐变组件"""
import re, io, os

DIR = r'C:\Users\admin\DSH\ruoyi\src\views\prep'
HEADS = {
    'daily.vue': ('edit', '每日一练', '每天 10 题（常识 2 + 言语 3 + 判断 2 + 数量 1 + 资料 2），10 分钟保持手感。错题自动进入错题本。'),
    'plan.vue': ('calendar', '90 天学习计划', '按《备考总纲》排好的完整计划，每天打卡，跟着走就不会迷茫。'),
    'chengyu.vue': ('reading', '高频成语积累', '共 {{ chengyu.length }} 个高频/易错/辨析成语，每天学 10 个，打卡式积累。'),
    'guifan.vue': ('notebook', '申论规范词库', '申论小题拿分关键：把材料里的“大白话”翻译成“机关语言”。共 {{ totalPairs }} 组。'),
    'shizheng.vue': ('clock', '时政速递', '实时新闻简讯（央视《新闻联播》+ 新华社评论员）+ 常考时政测验。热点看实时，考点看测验。'),
    'cards.vue': ('tickets', '速记卡片', '公式、口诀、考点闪卡：先想答案，再点卡片翻面核对。'),
    'sucai.vue': ('collection', '申论素材库', '金句 + 事例 + 高分范文（含亮点解析），按主题分类；还有大作文模板。'),
    'report.vue': ('trend', '学习报告', '刷题数据来自答题记录，学习进度来自备考中心各模块。知己知彼，才能有的放矢。'),
}

for f, (icon, title, desc) in HEADS.items():
    path = os.path.join(DIR, f)
    with io.open(path, 'r', encoding='utf-8') as fh:
        c = fh.read()
    # 替换 <div class="tab-head">...</div> 整块
    c2, n = re.subn(r'<div class="tab-head">.*?</div>\s*',
                    '<PageHead icon="%s" title="%s" desc="%s" />\n' % (icon, title, desc), c, count=1, flags=re.S)
    if n == 0:
        print('WARN no tab-head in', f)
    # 插入 import PageHead（在最后一个 import 之后）
    if "import PageHead from './PageHead.vue'" not in c2:
        lines = c2.split('\n')
        last_import = max(i for i, ln in enumerate(lines) if ln.strip().startswith('import '))
        lines.insert(last_import + 1, "import PageHead from './PageHead.vue'")
        c2 = '\n'.join(lines)
    # 移除残留 .tab-head 样式块
    c2 = re.sub(r'\.tab-head[^{]*\{[^}]*\}\s*', '', c2)
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(c2)
    print('done:', f)
