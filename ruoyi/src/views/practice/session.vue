<template>
  <div class="app-container session-page">
    <div class="session-top">
      <div class="session-top-left">
        <el-button link type="primary" @click="goBack">← 返回</el-button>
        <span class="paper-title">{{ paperTitle }}</span>
        <el-tag size="small" type="info">{{ current.section }}</el-tag>
      </div>
      <div class="session-top-right">
        <span class="progress-text">已答 {{ answeredCount }}/{{ questions.length }}</span>
        <el-button size="small" @click="showCard = true">答题卡</el-button>
      </div>
    </div>

    <div v-loading="loading" class="session-body" :class="{ 'with-material': hasMaterial }">
      <div v-if="hasMaterial" class="material-panel">
        <div class="material-head">
          <el-icon><Document /></el-icon>
          <span>{{ materialTitle || '阅读材料' }}</span>
        </div>
        <div class="material-content" v-html="materialHtml"></div>
      </div>

      <div class="question-panel">
        <div class="q-head">
          <span class="q-no">第 {{ current.qorder }} 题</span>
          <el-tag v-if="current.hasImage" size="small" type="warning">含图片</el-tag>
          <el-tag v-if="answeredMap[current.id] && answeredMap[current.id].isCorrect === 1" size="small" type="success">已答对</el-tag>
          <el-tag v-else-if="answeredMap[current.id]" size="small" type="danger">已答错</el-tag>
        </div>
        <div class="q-stem" v-html="current.stem"></div>

        <div v-if="optionsList.length" class="q-options">
          <div
            v-for="opt in optionsList"
            :key="opt.label"
            class="q-option"
            :class="optionClass(opt.label)"
            @click="pick(opt.label)"
          >
            <span class="opt-label">{{ opt.label }}</span>
            <span class="opt-html" v-html="opt.html"></span>
            <el-icon v-if="shown && current.answer === opt.label" class="opt-flag ok"><CircleCheckFilled /></el-icon>
            <el-icon v-else-if="shown && selected === opt.label" class="opt-flag no"><CircleCloseFilled /></el-icon>
          </div>
        </div>

        <div v-if="shown" class="q-result" :class="resultOk ? 'ok' : 'no'">
          <div class="result-line">
            <template v-if="!hasAnswer">
              <el-icon><WarningFilled /></el-icon> 本题暂无答案（可在题库管理中补充）
            </template>
            <template v-else-if="resultOk">
              <el-icon><CircleCheckFilled /></el-icon> 回答正确！
            </template>
            <template v-else>
              <el-icon><CircleCloseFilled /></el-icon> 回答错误，正确答案：{{ current.answer }}
            </template>
          </div>
          <div v-if="result.analysis" class="q-analysis" v-html="analysisHtml"></div>
        </div>

        <div class="q-nav">
          <el-button :disabled="idx === 0" @click="prev">上一题</el-button>
          <el-button v-if="idx < questions.length - 1" type="primary" @click="next">下一题</el-button>
          <el-button v-else type="success" @click="finish">完成练习</el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="showCard" title="答题卡" width="640px">
      <div class="card-grid">
        <div
          v-for="(q, i) in questions"
          :key="q.id"
          class="card-cell"
          :class="cardClass(q)"
          @click="jump(i)"
        >{{ q.qorder }}</div>
      </div>
      <div class="card-legend">
        <span class="dot green"></span>答对 <span class="dot red"></span>答错 <span class="dot gray"></span>未答
      </div>
      <template #footer>
        <el-button type="primary" @click="showCard = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showFinish" title="练习完成" width="420px">
      <div class="finish-stats">
        <div class="finish-num">{{ correctCount }}</div>
        <div class="finish-label">答对</div>
        <el-progress :percentage="accuracy" :stroke-width="12" />
      </div>
      <template #footer>
        <el-button @click="goBack">返回列表</el-button>
        <el-button type="primary" @click="restart">再来一轮</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, CircleCheckFilled, CircleCloseFilled, WarningFilled } from '@element-plus/icons-vue'
import { getPaperDetail, randomQuestions, saveRecord, recordAnswered } from '@/api/exam'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const paperTitle = ref('')
const questions = ref([])
const materialsMap = ref({})
const answeredMap = ref({})
const idx = ref(0)
const selected = ref('')
const shown = ref(false)
const result = ref({})
const showCard = ref(false)
const showFinish = ref(false)

const current = computed(() => questions.value[idx.value] || { stem: '', options: '[]' })
const optionsList = computed(() => {
  try {
    const arr = JSON.parse(current.value.options || '[]')
    return Array.isArray(arr) ? arr : []
  } catch (e) {
    return []
  }
})
const hasMaterial = computed(() => current.value.materialId && materialsMap.value[current.value.materialId])
const materialHtml = computed(() => hasMaterial.value ? materialsMap.value[current.value.materialId].content : '')
const materialTitle = computed(() => hasMaterial.value ? materialsMap.value[current.value.materialId].title : '')
const answeredCount = computed(() => Object.keys(answeredMap.value).length)
const resultOk = computed(() => result.value.correct === true)
const hasAnswer = computed(() => result.value.hasAnswer !== false)
const correctCount = computed(() => Object.values(answeredMap.value).filter(r => r.isCorrect === 1).length)
const accuracy = computed(() => answeredCount.value ? Math.round(correctCount.value * 100 / answeredCount.value) : 0)
const analysisHtml = computed(() => {
  const a = result.value.analysis || ''
  return String(a).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br/>')
})

async function load() {
  loading.value = true
  try {
    if (route.query.mode === 'random') {
      const res = await randomQuestions({ section: route.query.section || '', count: route.query.count || 10 })
      questions.value = res.questions || []
      const mm = {}
      ;(res.materials || []).forEach(m => { mm[m.id] = m })
      materialsMap.value = mm
      paperTitle.value = '随机练习 · ' + (route.query.section || '全部题型')
    } else {
      const paperId = route.query.paperId
      if (!paperId) {
        ElMessage.error('缺少试卷参数，请从试卷列表进入')
        router.replace('/practice/papers')
        return
      }
      const res = await getPaperDetail(paperId)
      questions.value = res.questions || []
      const mm = {}
      ;(res.materials || []).forEach(m => { mm[m.id] = m })
      materialsMap.value = mm
      paperTitle.value = res.paper ? res.paper.title : ''
      const recs = await recordAnswered(paperId)
      const am = {}
      recs.forEach(r => { am[r.questionId] = r })
      answeredMap.value = am
      // 定位到第一道未答题
      const firstUn = questions.value.findIndex(q => !am[q.id])
      idx.value = firstUn >= 0 ? firstUn : 0
    }
  } catch (e) {
    ElMessage.error('加载失败：' + (e.msg || e.message))
  } finally {
    loading.value = false
  }
}

function optionClass(label) {
  const cls = []
  if (selected.value === label) cls.push('selected')
  if (shown.value) {
    if (current.value.answer === label) cls.push('correct')
    else if (selected.value === label) cls.push('wrong')
  }
  return cls
}

async function pick(label) {
  if (shown.value || loading.value) return
  selected.value = label
  shown.value = true
  try {
    const res = await saveRecord({ questionId: current.value.id, userAnswer: label })
    result.value = res
    answeredMap.value[current.value.id] = {
      userAnswer: label,
      isCorrect: res.correct ? 1 : 0
    }
    if (res.correct === false) {
      const m = ElMessage({ type: 'warning', message: '答错了，正确答案：' + res.rightAnswer, duration: 2500 })
      setTimeout(() => m.close(), 2500)
    }
  } catch (e) {
    ElMessage.error('提交失败：' + (e.msg || e.message))
  }
}

function prev() { if (idx.value > 0) { idx.value--; resetView() } }
function next() { if (idx.value < questions.value.length - 1) { idx.value++; resetView() } }
function jump(i) { idx.value = i; resetView(); showCard.value = false }
function resetView() {
  selected.value = ''
  shown.value = false
  result.value = {}
}
function finish() {
  showFinish.value = true
}
function restart() {
  showFinish.value = false
  if (route.query.mode === 'random') {
    load()
  } else {
    idx.value = 0
    resetView()
  }
}
function goBack() {
  router.push(route.query.mode === 'random' ? '/practice/random' : '/practice/papers')
}
function cardClass(q) {
  const r = answeredMap.value[q.id]
  if (!r) return 'gray'
  return r.isCorrect === 1 ? 'green' : 'red'
}

function onKey(e) {
  if (e.key === 'ArrowLeft') prev()
  if (e.key === 'ArrowRight') next()
}

onMounted(() => {
  load()
  window.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.session-page {
  padding: 12px 16px;
  height: calc(100vh - 84px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.session-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
}
.session-top-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.paper-title { font-size: 16px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 40vw; }
.session-top-right { display: flex; align-items: center; gap: 10px; }
.progress-text { color: var(--el-text-color-secondary); font-size: 13px; }
.session-body {
  flex: 1;
  display: flex;
  gap: 14px;
  margin-top: 12px;
  min-height: 0;
}
.session-body.with-material .question-panel { width: 55%; }
.material-panel {
  width: 45%;
  background: #f7f8fa;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.dark .material-panel { background: #1d1e1f; }
.material-head {
  padding: 10px 14px;
  font-weight: 600;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.material-content {
  padding: 12px 14px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.8;
}
.material-content :deep(img) { max-width: 100%; }
.material-content :deep(table) { border-collapse: collapse; margin: 8px 0; }
.material-content :deep(td), .material-content :deep(th) { border: 1px solid #aaa; padding: 4px 8px; }
.question-panel {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}
.q-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.q-no { font-size: 16px; font-weight: 700; }
.q-stem { font-size: 15px; line-height: 1.9; margin-bottom: 16px; }
.q-stem :deep(img) { max-width: 100%; }
.q-options { display: flex; flex-direction: column; gap: 10px; }
.q-option {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all .15s;
  line-height: 1.7;
  font-size: 14px;
}
.q-option:hover { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.q-option.selected { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.q-option.correct { border-color: #67c23a; background: #f0f9eb; }
.q-option.wrong { border-color: #f56c6c; background: #fef0f0; }
.opt-label {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}
.q-option.correct .opt-label { background: #67c23a; color: #fff; border-color: #67c23a; }
.q-option.wrong .opt-label { background: #f56c6c; color: #fff; border-color: #f56c6c; }
.opt-html :deep(img) { max-width: 220px; vertical-align: middle; }
.opt-flag { margin-left: auto; flex-shrink: 0; font-size: 18px; }
.opt-flag.ok { color: #67c23a; }
.opt-flag.no { color: #f56c6c; }
.q-result { margin-top: 16px; border-radius: 8px; padding: 12px 16px; }
.q-result.ok { background: #f0f9eb; border: 1px solid #b3e19d; }
.q-result.no { background: #fef0f0; border: 1px solid #fbc4c4; }
.result-line { display: flex; align-items: center; gap: 6px; font-weight: 600; }
.q-analysis { margin-top: 8px; line-height: 1.8; font-size: 14px; }
.q-nav { margin-top: 18px; display: flex; gap: 10px; }
.card-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 8px; }
.card-cell {
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
}
.card-cell.green { background: #f0f9eb; border: 1px solid #b3e19d; }
.card-cell.red { background: #fef0f0; border: 1px solid #fbc4c4; }
.card-cell.gray { background: #f4f4f5; border: 1px solid #e4e7ed; }
.card-legend { margin-top: 12px; display: flex; gap: 16px; align-items: center; font-size: 13px; color: var(--el-text-color-secondary); }
.dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; margin-right: 4px; }
.dot.green { background: #f0f9eb; border: 1px solid #b3e19d; }
.dot.red { background: #fef0f0; border: 1px solid #fbc4c4; }
.dot.gray { background: #f4f4f5; border: 1px solid #e4e7ed; }
.finish-stats { text-align: center; padding: 8px 0; }
.finish-num { font-size: 40px; font-weight: 700; color: #67c23a; }
.finish-label { color: var(--el-text-color-secondary); margin-bottom: 12px; }
@media (max-width: 900px) {
  .session-body { flex-direction: column; }
  .session-body.with-material .question-panel { width: 100%; }
  .material-panel { width: 100%; max-height: 40vh; }
}
</style>
