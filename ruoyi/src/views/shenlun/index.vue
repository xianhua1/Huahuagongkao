<template>
  <div class="sl-page">
    <!-- 试卷列表 -->
    <div v-if="!paper" class="sl-list">
      <div class="sl-head">
        <h2>申论刷题</h2>
        <p>国考申论真题（2000-2022），阅读材料 + 格子答题卡作答，交卷后由 AI 大模型参考标准答案评分分析。</p>
      </div>
      <div class="sl-filters">
        <el-input v-model="kw" placeholder="搜索试卷标题/年份" clearable size="small" style="width: 220px" />
        <el-button size="small" @click="loadPapers">刷新</el-button>
      </div>
      <div class="sl-cards">
        <div v-for="p in filtered" :key="p.id" class="sl-card" @click="openPaper(p)">
          <div class="sl-card-year">{{ p.year }}</div>
          <div class="sl-card-body">
            <div class="sl-card-title">{{ p.title }}</div>
            <div class="sl-card-meta">{{ p.version }} · {{ p.questionCount }} 题</div>
          </div>
          <el-button size="small" type="primary" plain>开始作答 →</el-button>
        </div>
      </div>
      <el-empty v-if="!filtered.length" description="暂无试卷" />
    </div>

    <!-- 作答页 -->
    <div v-else class="sl-work">
      <div class="sl-work-head">
        <el-button size="small" @click="back">← 返回列表</el-button>
        <div class="sl-work-title">{{ paper.title }}</div>
        <el-tag size="small">{{ paper.year }} · {{ paper.version }}</el-tag>
      </div>

      <div class="sl-layout">
        <!-- 左：材料（支持选择标注） -->
        <div class="sl-materials">
          <div class="sl-panel-title">
            📄 给定资料
            <span class="sl-mark-hint">选中文字可下划线 / 删除线 / 高亮标注（退出后不保留）</span>
          </div>
          <div v-for="m in materials" :key="m.id" class="sl-material">
            <div class="sl-material-title">
              {{ m.title || '材料' + m.mNo }}
              <el-button v-if="(anns[m.id] || []).length" size="small" text type="danger" @click="clearMarks(m.id)">清除标注</el-button>
            </div>
            <div
              class="sl-material-full"
              v-html="markedHtml(m)"
              @mouseup="onMatMouseUp($event, m)"
            ></div>
          </div>
        </div>

        <!-- 标注工具条 -->
        <div v-if="tb.show" class="mark-toolbar" :style="{ left: tb.x + 'px', top: tb.y + 'px' }">
          <button class="mt-btn" title="下划线" @mousedown.prevent="applyMark('u')">U</button>
          <button class="mt-btn" title="删除线" @mousedown.prevent="applyMark('s')">S̶</button>
          <button class="mt-color" title="黄色高亮" style="background:#fff59d" @mousedown.prevent="applyMark('y')"></button>
          <button class="mt-color" title="绿色高亮" style="background:#c8e6c9" @mousedown.prevent="applyMark('g')"></button>
          <button class="mt-color" title="红色高亮" style="background:#ffcdd2" @mousedown.prevent="applyMark('r')"></button>
          <button class="mt-btn mt-clear" title="清除选中区域标注" @mousedown.prevent="clearSel">✕</button>
        </div>

        <!-- 右：题目与答题卡 -->
        <div class="sl-questions">
          <div class="sl-panel-title">✍️ 作答区（一字一格 · 共 {{ totalCells }} 格）</div>
          <div v-for="(q, qi) in questions" :key="q.id" class="sl-question">
            <div class="sl-q-head">
              <span class="sl-q-no">第 {{ q.qno }} 题</span>
              <span class="sl-q-score">{{ q.score }} 分</span>
              <span class="sl-q-limit">限 {{ q.wordLimit }} 字</span>
              <span class="sl-q-count">{{ countChar(qnoKey(q)) }}/{{ q.wordLimit }}</span>
            </div>
            <div class="sl-q-title">{{ q.title }}</div>
            <ShenLunCard
              :model-value="answers[qnoKey(q)] || ''"
              :word-limit="q.wordLimit"
              @update:model-value="v => (answers[qnoKey(q)] = v)"
            />
            <div class="count-info">
              已写 <b>{{ countChar(qnoKey(q)) }}</b> 字 / 共 {{ gridSize(q) }} 格
              <span v-if="overLimit(q)" class="over">⚠️ 超过字数限制</span>
            </div>
          </div>

          <!-- 交卷操作 -->
          <div class="sl-submit">
            <el-button type="primary" size="large" :loading="grading" @click="submit(false)">✉️ 交卷保存</el-button>
            <el-button type="success" size="large" :loading="grading" @click="submit(true)">🤖 交卷并 AI 评分</el-button>
            <span class="sl-submit-tip">AI 评分由服务器端大模型完成（环境变量配置），参考标准答案逐题打分并给出分析建议</span>
          </div>

          <!-- 评分结果 -->
          <div v-if="gradeResult" class="sl-grade">
            <div class="sl-grade-head">
              <span class="sl-grade-total">总分：<b>{{ gradeResult.totalScore }}</b> / {{ gradeResult.maxScore }}</span>
              <el-button size="small" @click="gradeResult = null">收起</el-button>
            </div>
            <div v-for="g in gradeResult.grades" :key="g.qno" class="sl-grade-item">
              <div class="sl-grade-q">第 {{ g.qno }} 题：<b>{{ g.score }}</b> / {{ g.maxScore }} 分</div>
              <div class="sl-grade-analysis">📊 得分分析：{{ g.analysis }}</div>
              <div class="sl-grade-suggest">💡 改进建议：{{ g.suggestions }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI 评分说明（配置在服务器环境变量，不在此设置） -->
    <el-dialog v-model="llmShow" title="🤖 AI 评分说明" width="460px">
      <div class="llm-tip">
        AI 评分由服务器端调用大模型完成，密钥通过服务器环境变量配置（<code>DEEPSEEK_API_KEY</code> / <code>DEEPSEEK_BASE_URL</code> / <code>DEEPSEEK_MODEL</code>），不会在页面中暴露。
      </div>
      <template #footer>
        <el-button type="primary" @click="llmShow = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import ShenLunCard from './ShenLunCard.vue'

const papers = ref([])
const kw = ref('')
const paper = ref(null)
const materials = ref([])
const questions = ref([])
const answers = ref({})
const grading = ref(false)
const gradeResult = ref(null)
const llmShow = ref(false)

// 每行 20 格（与答题卡组件一致，用于 gridSize 计算）
const PER_ROW = 20

function gridSize(q) {
  const lim = q.wordLimit || 400
  return Math.max(PER_ROW, Math.ceil(lim / PER_ROW) * PER_ROW)
}

// ---------- 材料标注（仅本次会话，退出不保留） ----------
const anns = ref({}) // matId -> [{ s, e, style }]
const tb = ref({ show: false, x: 0, y: 0, matId: null, s: 0, e: 0 })

const MARK_TAGS = {
  u: '<span style="text-decoration:underline">',
  s: '<span style="text-decoration:line-through">',
  y: '<span style="background:#fff59d">',
  g: '<span style="background:#c8e6c9">',
  r: '<span style="background:#ffcdd2">'
}
const MARK_ORDER = ['u', 's', 'y', 'g', 'r']

function esc(t) {
  return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function markedHtml(m) {
  const text = m.content
  const list = (anns.value[m.id] || []).filter(a => a.s < a.e)
  if (!list.length) {
    // 先转义，再换行 → <br/>（顺序不能反，否则 <br/> 会被转义成字面量）
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br/>')
  }
  // 含图片等 HTML 标签的材料不做标注渲染（原样显示）
  if (text.includes('<img')) {
    return text.replace(/\n/g, '<br/>')
  }
  const stylesAt = {}
  list.forEach(a => {
    for (let p = a.s; p < a.e; p++) {
      if (p >= 0 && p < text.length) (stylesAt[p] = stylesAt[p] || new Set()).add(a.style)
    }
  })
  let out = ''
  let open = []
  for (let i = 0; i < text.length; i++) {
    const st = stylesAt[i] || new Set()
    for (let k = open.length - 1; k >= 0; k--) {
      if (!st.has(open[k])) {
        out += '</span>'
        open.splice(k, 1)
      }
    }
    MARK_ORDER.forEach(s => {
      if (st.has(s) && !open.includes(s)) {
        out += MARK_TAGS[s]
        open.push(s)
      }
    })
    const ch = text[i]
    if (ch === '\n') {
      out += '<br/>'
    } else {
      out += esc(ch)
    }
  }
  while (open.length) {
    out += '</span>'
    open.pop()
  }
  return out
}

// 计算 DOM 选区在材料纯文本中的字符偏移（\n 按 1 字符计入，与 content 索引一致）
function offsetIn(root, node, off) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT)
  let total = 0
  let br = 0
  let n
  while ((n = walker.nextNode())) {
    if (n.nodeType === Node.TEXT_NODE) {
      if (n === node) return total + off + br
      total += n.textContent.length
    } else if (n.nodeName === 'BR') {
      if (n === node) return total + br + 1
      br++
    } else if (n === node && n.nodeType === Node.ELEMENT_NODE) {
      // 选区边界落在元素上：累计其前 offset 个子节点的长度
      let sub = 0
      const kids = n.childNodes
      for (let i = 0; i < off && i < kids.length; i++) {
        const k = kids[i]
        if (k.nodeType === Node.TEXT_NODE) sub += k.textContent.length
        else if (k.nodeName === 'BR') sub += 1
        else sub += k.textContent.length
      }
      return total + br + sub
    }
  }
  return 0
}

function onMatMouseUp(e, m) {
  const container = e.currentTarget // 事件对象属性在异步回调中会失效，先缓存
  // 等选区稳定
  setTimeout(() => {
    const sel = window.getSelection()
    if (!sel || sel.isCollapsed || !sel.rangeCount) {
      tb.value.show = false
      return
    }
    const range = sel.getRangeAt(0)
    if (!container || !container.contains(range.commonAncestorContainer)) {
      tb.value.show = false
      return
    }
    const s = offsetIn(container, range.startContainer, range.startOffset)
    const e2 = offsetIn(container, range.endContainer, range.endOffset)
    if (s === e2) {
      tb.value.show = false
      return
    }
    const rect = range.getBoundingClientRect()
    tb.value = {
      show: true,
      x: Math.min(rect.left + rect.width / 2 - 120, window.innerWidth - 260),
      y: Math.max(rect.bottom + 6, 8),
      matId: m.id,
      s: Math.min(s, e2),
      e: Math.max(s, e2)
    }
  }, 30)
}

function applyMark(style) {
  const list = anns.value[tb.value.matId] || []
  list.push({ s: tb.value.s, e: tb.value.e, style })
  anns.value = { ...anns.value, [tb.value.matId]: list }
  tb.value.show = false
}

function clearSel() {
  const list = (anns.value[tb.value.matId] || []).filter(a => !(a.s === tb.value.s && a.e === tb.value.e))
  anns.value = { ...anns.value, [tb.value.matId]: list }
  tb.value.show = false
}

function clearMarks(matId) {
  anns.value = { ...anns.value, [matId]: [] }
}

const filtered = computed(() => {
  const k = kw.value.trim()
  if (!k) return papers.value
  return papers.value.filter(p => p.title.includes(k) || String(p.year).includes(k))
})
const totalCells = computed(() => questions.value.reduce((n, q) => n + (q.wordLimit || 0), 0) + 400)

function qnoKey(q) {
  return String(q.qno)
}
function countChar(k) {
  return (answers.value[k] || '').length
}
function overLimit(q) {
  const lim = q.wordLimit || 0
  return lim > 0 && countChar(qnoKey(q)) > lim
}

async function loadPapers() {
  const res = await request.get('/shenlun/paper/list')
  papers.value = res.data || []
}
async function openPaper(p) {
  const res = await request.get('/shenlun/paper/' + p.id)
  paper.value = res.data.paper
  materials.value = res.data.materials || []
  questions.value = res.data.questions || []
  answers.value = {}
  gradeResult.value = null
}
function back() {
  paper.value = null
  loadPapers()
}

async function submit(withGrade) {
  const empty = questions.value.filter(q => !(answers.value[qnoKey(q)] || '').trim())
  if (empty.length) {
    const ok = await ElMessageBox.confirm('还有 ' + empty.length + ' 道题未作答，确认交卷？', '提示', { type: 'warning' }).catch(() => false)
    if (!ok) return
  }
  grading.value = true
  try {
    const payload = { paperId: paper.value.id, content: JSON.stringify(answers.value) }
    if (withGrade) {
      const res = await request.post('/shenlun/answer/grade', payload)
      const d = res.data || {}
      if (d.success) {
        gradeResult.value = d.grade
        ElMessage.success('评分完成！总分 ' + d.grade.totalScore + '/' + d.grade.maxScore)
      } else {
        ElMessage.error(d.msg || '评分失败')
      }
    } else {
      await request.post('/shenlun/answer/submit', payload)
      ElMessage.success('已保存作答')
    }
  } catch (e) {
    ElMessage.error('操作失败：' + (e.message || '网络异常'))
  } finally {
    grading.value = false
  }
}

function showLlmTip() {
  llmShow.value = true
}

onMounted(loadPapers)
</script>

<style scoped>
.sl-page { min-height: 400px; }
.sl-head h2 { margin: 0 0 6px; font-size: 22px; }
.sl-head p { margin: 0 0 16px; font-size: 13px; color: var(--el-text-color-secondary); }
.sl-filters { display: flex; gap: 10px; margin-bottom: 16px; }
.sl-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 14px; }
.sl-card {
  display: flex; align-items: center; gap: 14px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px; padding: 14px 16px; cursor: pointer;
  transition: all .18s; background: var(--el-bg-color);
}
.sl-card:hover { border-color: var(--el-color-primary); box-shadow: 0 4px 14px rgba(64,158,255,.18); transform: translateY(-2px); }
.sl-card-year {
  flex-shrink: 0; width: 56px; height: 56px; border-radius: 12px;
  background: linear-gradient(135deg, #409eff, #36cfc9);
  color: #fff; font-size: 17px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}
.sl-card-body { flex: 1; min-width: 0; }
.sl-card-title { font-size: 14px; font-weight: 600; line-height: 1.5; }
.sl-card-meta { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }

/* 作答页 */
.sl-work-head { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.sl-work-title { flex: 1; font-size: 17px; font-weight: 700; }
.sl-layout { display: flex; gap: 16px; align-items: flex-start; }
@media (max-width: 1000px) { .sl-layout { flex-direction: column; } }
.sl-materials { width: 44%; flex-shrink: 0; max-height: calc(100vh - 180px); overflow-y: auto; }
@media (max-width: 1000px) { .sl-materials { width: 100%; max-height: none; } }
.sl-questions { flex: 1; min-width: 0; }
.sl-panel-title {
  font-size: 15px; font-weight: 700; color: var(--el-color-primary);
  margin-bottom: 12px; padding-left: 8px; border-left: 3px solid var(--el-color-primary);
  display: flex; align-items: center; gap: 10px;
}
.sl-mark-hint { font-size: 11px; font-weight: 400; color: var(--el-text-color-secondary); }
.sl-material { border: 1px solid var(--el-border-color-light); border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; background: var(--el-bg-color); }
.sl-material-title { font-size: 13px; font-weight: 700; margin-bottom: 6px; color: var(--el-text-color-primary); display: flex; align-items: center; justify-content: space-between; }
.sl-material-full { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.9; white-space: pre-wrap; user-select: text; }

/* 标注工具条 */
.mark-toolbar {
  position: fixed;
  z-index: 3000;
  display: flex;
  align-items: center;
  gap: 4px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 4px 6px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, .15);
}
.mt-btn {
  width: 26px; height: 26px;
  border: 1px solid #d9d9d9; border-radius: 5px;
  background: #fff; cursor: pointer;
  font-size: 13px; font-weight: 700; color: #333;
  display: flex; align-items: center; justify-content: center;
}
.mt-btn:hover { border-color: var(--el-color-primary); color: var(--el-color-primary); }
.mt-color {
  width: 24px; height: 24px; border-radius: 50%;
  border: 2px solid #fff; cursor: pointer;
  box-shadow: 0 0 0 1px #d9d9d9;
}
.mt-color:hover { transform: scale(1.15); }
.mt-clear { color: #f56c6c; }

.sl-question { border: 1px solid var(--el-border-color-light); border-radius: 12px; padding: 14px 16px; margin-bottom: 14px; background: var(--el-bg-color); }
.sl-q-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.sl-q-no { font-size: 14px; font-weight: 700; color: var(--el-color-primary); }
.sl-q-score { font-size: 12px; color: #fff; background: #e6a23c; border-radius: 8px; padding: 1px 8px; }
.sl-q-limit { font-size: 12px; color: var(--el-text-color-secondary); }
.sl-q-count { margin-left: auto; font-size: 12px; color: var(--el-text-color-secondary); }
.sl-q-title { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.8; white-space: pre-wrap; margin-bottom: 10px; }

.count-info {
  margin-top: 8px;
  text-align: right;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.count-info b { color: var(--el-color-primary); }
.count-info .over { color: #f56c6c; margin-left: 8px; }
.sl-submit { display: flex; align-items: center; gap: 12px; margin: 18px 0; flex-wrap: wrap; }
.sl-submit-tip { font-size: 12px; color: var(--el-text-color-secondary); }
.sl-grade { border: 1px solid #b3e19d; background: #f0f9eb; border-radius: 12px; padding: 16px 18px; }
.sl-grade-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.sl-grade-total { font-size: 16px; }
.sl-grade-total b { font-size: 24px; color: #67c23a; }
.sl-grade-item { border-top: 1px dashed #b3e19d; padding: 12px 0; }
.sl-grade-q { font-size: 14px; font-weight: 700; }
.sl-grade-q b { color: #67c23a; }
.sl-grade-analysis { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.8; margin-top: 6px; }
.sl-grade-suggest { font-size: 13px; color: #e6a23c; line-height: 1.8; margin-top: 4px; }
.llm-tip { font-size: 12px; color: var(--el-text-color-secondary); line-height: 1.7; }
</style>
