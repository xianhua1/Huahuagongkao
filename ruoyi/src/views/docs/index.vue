<template>
  <div class="docs-page">
    <!-- 左侧目录 -->
    <aside class="docs-toc">
      <div class="toc-head">
        <el-icon color="#409eff"><Reading /></el-icon>
        <span>知识点目录</span>
      </div>
      <el-input v-model="keyword" size="small" placeholder="搜索知识点" clearable style="margin-bottom: 10px">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <div v-for="g in filteredGroups" :key="g.cat" class="toc-group">
        <div class="toc-cat">{{ g.cat }}</div>
        <div
          v-for="item in g.items"
          :key="item.id"
          class="toc-item"
          :class="{ active: current && current.id === item.id }"
          @click="select(item)"
        >
          {{ item.title }}
        </div>
      </div>
      <el-empty v-if="!filteredGroups.length" description="无匹配内容" :image-size="60" />
    </aside>

    <!-- 右侧内容 -->
    <main class="docs-main">
      <div v-if="current" class="doc-wrap">
        <h2 class="doc-title">{{ current.title }}</h2>
        <div class="doc-body" v-html="html"></div>
      </div>
      <div v-else class="doc-empty">
        <div class="doc-empty-icon">
          <el-icon :size="46" color="#409eff"><Reading /></el-icon>
        </div>
        <h3>选择左侧知识点开始学习</h3>
        <p>国考行测与事业单位职测的每一个模块知识点，都整理在这里。</p>
      </div>
    </main>

    <!-- 悬浮返回顶部 -->
    <el-backtop target=".docs-main" :bottom="56" :right="28" :visibility-height="320" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Reading, Search } from '@element-plus/icons-vue'
import { docs } from './knowledge'

const current = ref(null)
const keyword = ref('')

const allItems = computed(() => docs.flatMap(g => g.items))

function select(item) {
  current.value = item
  if (item && location.hash !== '#' + item.id) {
    history.replaceState(null, '', '#' + item.id)
  }
}

function applyHash() {
  const h = String(location.hash || '').replace(/^#\/?/, '')
  if (!h) return
  const hit = allItems.value.find(i => i.id === h)
  if (hit) current.value = hit
}

onMounted(() => {
  applyHash()
  // 支持首页搜索跳转携带关键词（?kw=xxx）
  const q = new URLSearchParams(location.search).get('kw')
  if (q) keyword.value = q
  window.addEventListener('hashchange', applyHash)
})
onBeforeUnmount(() => window.removeEventListener('hashchange', applyHash))

const filteredGroups = computed(() => {
  const kw = keyword.value.trim()
  if (!kw) return docs
  return docs
    .map(g => ({ ...g, items: g.items.filter(i => i.title.includes(kw) || i.md.includes(kw)) }))
    .filter(g => g.items.length)
})

const html = computed(() => (current.value ? md2html(current.value.md) : ''))

// ---------- 轻量 markdown 渲染 ----------
function inline(s) {
  return String(s)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
}

function md2html(md) {
  const lines = String(md || '').split('\n')
  let out = ''
  let list = null // null | 'ul' | 'ol'
  let tableRows = []

  const closeList = () => {
    if (list) {
      out += list === 'ol' ? '</ol>' : '</ul>'
      list = null
    }
  }
  const flushTable = () => {
    if (tableRows.length) {
      out += '<table><tbody>' + tableRows
        .map(r => '<tr>' + r.map(c => '<td>' + inline(c) + '</td>').join('') + '</tr>')
        .join('') + '</tbody></table>'
      tableRows = []
    }
  }

  for (const raw of lines) {
    const t = raw.trim()
    if (t.startsWith('|')) {
      closeList()
      const cells = t.split('|').slice(1, -1).map(s => s.trim())
      // 表头行做加粗；分隔行跳过
      if (!/^[\s:|-]+$/.test(cells.join(''))) {
        tableRows.push(cells.map(c => (tableRows.length === 0 ? '**' + c + '**' : c)))
      }
      continue
    }
    flushTable()
    if (!t) { closeList(); continue }
    if (t.startsWith('### ')) { closeList(); out += '<h4>' + inline(t.slice(4)) + '</h4>' }
    else if (t.startsWith('## ')) { closeList(); out += '<h3>' + inline(t.slice(3)) + '</h3>' }
    else if (t.startsWith('# ')) { closeList(); out += '<h2>' + inline(t.slice(2)) + '</h2>' }
    else if (t.startsWith('> ')) { closeList(); out += '<blockquote>' + inline(t.slice(2)) + '</blockquote>' }
    else if (/^!\[([^\]]*)\]\(([^)]+)\)/.test(t)) {
      closeList()
      out += t.replace(/^!\[([^\]]*)\]\(([^)]+)\)/, '<img class="doc-img" src="$2" alt="$1" />')
    }
    else if (/^[-*] /.test(t)) {
      if (list !== 'ul') { closeList(); out += '<ul>'; list = 'ul' }
      out += '<li>' + inline(t.slice(2)) + '</li>'
    }
    else if (/^\d+\. /.test(t)) {
      if (list !== 'ol') { closeList(); out += '<ol>'; list = 'ol' }
      out += '<li>' + inline(t.replace(/^\d+\. /, '')) + '</li>'
    }
    else if (t === '---') { closeList(); out += '<hr/>' }
    else { closeList(); out += '<p>' + inline(t) + '</p>' }
  }
  closeList()
  flushTable()
  return out
}
</script>

<style scoped>
.docs-page {
  display: flex;
  gap: 18px;
  height: calc(100vh - 84px);
  min-height: 0;
}
.docs-toc {
  width: 260px;
  flex-shrink: 0;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 16px 14px;
  overflow-y: auto;
}
.toc-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
}
.toc-group { margin-bottom: 14px; }
.toc-cat {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
  border-radius: 6px;
  padding: 4px 10px;
  margin-bottom: 6px;
}
.toc-item {
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--el-text-color-regular);
  transition: all .15s;
  line-height: 1.4;
}
.toc-item:hover { background: var(--el-fill-color-light); }
.toc-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: 600;
}
.docs-main {
  flex: 1;
  min-width: 0;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  overflow-y: auto;
  padding: 26px 34px 40px;
}
.doc-title {
  margin: 0 0 18px;
  font-size: 24px;
  padding-bottom: 14px;
  border-bottom: 2px solid var(--el-color-primary);
  display: inline-block;
}
.doc-body { max-width: 860px; }
.doc-body :deep(h2) {
  font-size: 22px;
  margin: 30px 0 12px;
  padding: 10px 14px;
  border-left: 5px solid var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  border-radius: 0 8px 8px 0;
  line-height: 1.4;
}
.doc-body :deep(h3) {
  font-size: 18px;
  margin: 26px 0 12px;
  padding-left: 10px;
  border-left: 4px solid var(--el-color-primary);
  line-height: 1.4;
}
.doc-body :deep(h4) { font-size: 16px; margin: 20px 0 8px; }
.doc-body :deep(p) { font-size: 15px; line-height: 1.9; margin: 10px 0; color: var(--el-text-color-regular); }
.doc-body :deep(b) { color: var(--el-color-primary); }
.doc-body :deep(blockquote) {
  margin: 14px 0;
  padding: 12px 16px;
  background: var(--el-color-warning-light-9);
  border-left: 4px solid #e6a23c;
  border-radius: 0 8px 8px 0;
  font-size: 15px;
  line-height: 1.8;
  color: #8a5a00;
}
.doc-body :deep(code) {
  background: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 13px;
  color: #e6a23c;
}
.doc-body :deep(a) {
  color: var(--el-color-primary);
  text-decoration: none;
  border-bottom: 1px dashed var(--el-color-primary);
}
.doc-body :deep(a:hover) { border-bottom-style: solid; }
.doc-body :deep(.doc-img) {
  display: block;
  max-width: 92%;
  margin: 16px auto;
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
}
.doc-body :deep(ul), .doc-body :deep(ol) { padding-left: 22px; margin: 10px 0; }
.doc-body :deep(li) { font-size: 15px; line-height: 1.9; color: var(--el-text-color-regular); }
.doc-body :deep(table) {
  border-collapse: collapse;
  margin: 14px 0;
  width: 100%;
  font-size: 14px;
}
.doc-body :deep(td) {
  border: 1px solid var(--el-border-color);
  padding: 8px 12px;
  line-height: 1.7;
}
.doc-body :deep(tr:first-child td) {
  background: var(--el-fill-color-light);
  font-weight: 600;
}
.doc-body :deep(hr) { border: none; border-top: 1px dashed var(--el-border-color); margin: 20px 0; }
.doc-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
}
.doc-empty-icon { width: 92px; height: 92px; border-radius: 24px; background: var(--el-color-primary-light-9); display: flex; align-items: center; justify-content: center; margin-bottom: 6px; }
.doc-empty h3 { margin: 0; }
.doc-empty p { margin: 0; font-size: 13px; }
@media (max-width: 900px) {
  .docs-page { flex-direction: column; height: auto; }
  .docs-toc { width: 100%; max-height: 260px; }
}
</style>
