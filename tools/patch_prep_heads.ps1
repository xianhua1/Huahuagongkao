# 批量替换备考中心各页面头部为 PageHead 渐变组件
$ErrorActionPreference = 'Stop'
$dir = 'C:\Users\admin\DSH\ruoyi\src\views\prep'
$heads = @{
  'daily.vue'    = @('edit', '每日一练', '每天 10 题（常识 2 + 言语 3 + 判断 2 + 数量 1 + 资料 2），10 分钟保持手感。错题自动进入错题本。')
  'plan.vue'     = @('calendar', '90 天学习计划', '按《备考总纲》排好的完整计划，每天打卡，跟着走就不会迷茫。')
  'chengyu.vue'  = @('reading', '高频成语积累', '共 {{ chengyu.length }} 个高频/易错/辨析成语，每天学 10 个，打卡式积累。')
  'guifan.vue'   = @('notebook', '申论规范词库', '申论小题拿分关键：把材料里的“大白话”翻译成“机关语言”。共 {{ totalPairs }} 组。')
  'shizheng.vue' = @('clock', '时政速递', '实时新闻简讯（央视《新闻联播》+ 新华社评论员）+ 常考时政测验。热点看实时，考点看测验。')
  'cards.vue'    = @('tickets', '速记卡片', '公式、口诀、考点闪卡：先想答案，再点卡片翻面核对。')
  'sucai.vue'    = @('collection', '申论素材库', '金句 + 事例 + 高分范文（含亮点解析），按主题分类；还有大作文模板。')
  'report.vue'   = @('trend', '学习报告', '刷题数据来自答题记录，学习进度来自备考中心各模块。知己知彼，才能有的放矢。')
}

foreach ($f in $heads.Keys) {
  $path = Join-Path $dir $f
  $c = Get-Content $path -Raw -Encoding UTF8
  $icon = $heads[$f][0]
  $title = $heads[$f][1]
  $desc = $heads[$f][2]
  # 替换 <div class="tab-head">...</div> 整块
  $pattern = '(?s)<div class="tab-head">.*?</div>\s*'
  $replacement = '<PageHead icon="' + $icon + '" title="' + $title + '" desc="' + $desc + '" />' + "`r`n"
  $c2 = [regex]::Replace($c, $pattern, $replacement, 1)
  # 插入 import（在最后一个 import 行后）
  if ($c2 -notmatch "import PageHead from './PageHead.vue'") {
    $c2 = $c2 -replace "(import[^\r\n]*\r?\n)(?=[^i]|i(?!mport))", "`$1import PageHead from './PageHead.vue'`r`n", 1
  }
  # 移除残留 .tab-head 样式块
  $c2 = [regex]::Replace($c2, '(?s)\.tab-head[^{]*\{[^}]*\}\s*', '')
  [IO.File]::WriteAllText($path, $c2, [Text.Encoding]::UTF8)
  Write-Output "done: $f"
}
