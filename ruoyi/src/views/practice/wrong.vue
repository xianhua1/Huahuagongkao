<template>
  <div class="app-container">
    <el-card shadow="never">
      <div class="page-head">
        <div>
          <h2 class="page-title">错题本</h2>
          <p class="page-desc">答错的题目汇总，可重新练习、移出或清空</p>
        </div>
        <div class="page-actions">
          <el-select v-model="filterPaper" placeholder="按试卷筛选" clearable style="width: 220px">
            <el-option v-for="t in paperTitles" :key="t" :label="t" :value="t" />
          </el-select>
          <el-button type="danger" plain :disabled="!filtered.length" @click="clearWrong">清空错题本</el-button>
        </div>
      </div>

      <el-table v-loading="loading" :data="filtered" row-key="questionId">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="wrong-detail">
              <div v-if="row.materialContent" class="wrong-material">
                <div class="wrong-material-title">{{ row.materialTitle || '阅读材料' }}</div>
                <div v-html="row.materialContent"></div>
              </div>
              <div class="wrong-stem" v-html="row.stem"></div>
              <div v-if="row.optionsList && row.optionsList.length" class="wrong-options">
                <div
                  v-for="opt in row.optionsList"
                  :key="opt.label"
                  class="wrong-option"
                  :class="{ 'is-right': opt.label === row.answer, 'is-wrong': opt.label === row.userAnswer }"
                >
                  <span class="opt-label">{{ opt.label }}</span>
                  <span v-html="opt.html"></span>
                </div>
              </div>
              <div class="wrong-result">
                <el-tag size="small" type="danger">我的答案：{{ row.userAnswer || '未答' }}</el-tag>
                <el-tag size="small" type="success">正确答案：{{ row.answer || '暂无' }}</el-tag>
              </div>
              <div v-if="row.analysis" class="wrong-analysis">
                <div class="wrong-analysis-title">解析</div>
                <div v-html="analysisHtml(row.analysis)"></div>
              </div>
              <div class="wrong-actions">
                <el-button size="small" type="primary" @click="removeWrong(row)">移出错题本</el-button>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="试卷" prop="paperTitle" min-width="200" show-overflow-tooltip />
        <el-table-column label="题号" prop="qorder" width="70" align="center" />
        <el-table-column label="题型" prop="section" width="140" align="center" />
        <el-table-column label="题干" min-width="260" show-overflow-tooltip>
          <template #default="{ row }">{{ plainText(row.stem) }}</template>
        </el-table-column>
        <el-table-column label="我的答案" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="danger">{{ row.userAnswer || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="正确答案" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{ row.answer || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="作答时间" width="160" align="center">
          <template #default="{ row }">{{ fmtTime(row.answeredTime) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !filtered.length" description="太棒了，暂无错题" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { wrongList, removeRecord, clearWrongRecords } from '@/api/exam'

const loading = ref(false)
const list = ref([])
const filterPaper = ref('')

const paperTitles = computed(() => [...new Set(list.value.map(r => r.paperTitle))])
const filtered = computed(() => {
  if (!filterPaper.value) return list.value
  return list.value.filter(r => r.paperTitle === filterPaper.value)
})

function plainText(html) {
  const div = document.createElement('div')
  div.innerHTML = html || ''
  return div.textContent.trim().slice(0, 80)
}

function fmtTime(t) {
  if (!t) return '-'
  return String(t).replace('T', ' ').slice(0, 19)
}

function analysisHtml(a) {
  return String(a || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br/>')
}

async function load() {
  loading.value = true
  try {
    const rows = await wrongList()
    list.value = (rows || []).map(r => {
      try {
        r.optionsList = JSON.parse(r.options || '[]')
      } catch (e) {
        r.optionsList = []
      }
      return r
    })
  } finally {
    loading.value = false
  }
}

async function removeWrong(row) {
  await ElMessageBox.confirm('确定将该题移出错题本吗？', '提示', { type: 'warning' })
  await removeRecord(row.questionId)
  ElMessage.success('已移出')
  load()
}

async function clearWrong() {
  await ElMessageBox.confirm('确定清空全部错题吗？', '提示', { type: 'warning' })
  await clearWrongRecords()
  ElMessage.success('已清空')
  load()
}

onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.page-title { margin: 0 0 6px; font-size: 20px; }
.page-desc { margin: 0; color: var(--el-text-color-secondary); font-size: 13px; }
.page-actions { display: flex; gap: 8px; }
.wrong-detail { padding: 8px 16px 16px 60px; }
.wrong-material { background: #f7f8fa; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; }
.dark .wrong-material { background: #1d1e1f; }
.wrong-material-title { font-weight: 600; margin-bottom: 6px; }
.wrong-material :deep(img), .wrong-stem :deep(img) { max-width: 100%; }
.wrong-material :deep(table) { border-collapse: collapse; }
.wrong-material :deep(td) { border: 1px solid #aaa; padding: 3px 8px; }
.wrong-stem { font-size: 15px; line-height: 1.9; margin-bottom: 12px; }
.wrong-options { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.wrong-option { display: flex; gap: 8px; align-items: flex-start; padding: 6px 10px; border-radius: 6px; font-size: 14px; }
.wrong-option.is-right { background: #f0f9eb; }
.wrong-option.is-wrong { background: #fef0f0; }
.opt-label { font-weight: 700; }
.wrong-option :deep(img) { max-width: 180px; }
.wrong-result { display: flex; gap: 10px; margin-bottom: 10px; }
.wrong-analysis { border-top: 1px dashed var(--el-border-color); padding-top: 10px; }
.wrong-analysis-title { font-weight: 600; margin-bottom: 6px; }
.wrong-analysis div:last-child { line-height: 1.8; font-size: 14px; }
.wrong-actions { margin-top: 12px; }
</style>
