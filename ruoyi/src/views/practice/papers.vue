<template>
  <div class="app-container">
    <el-card shadow="never">
      <div class="page-head">
        <div>
          <h2 class="page-title">历年真题练习</h2>
          <p class="page-desc">2000-2022 年国家公务员考试《行测》真题，含资料分析材料联动与逐题解析</p>
        </div>
        <div class="page-actions">
          <el-radio-group v-model="subject" @change="loadPapers" style="margin-right: 12px">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="行测">国考行测</el-radio-button>
            <el-radio-button value="职测">事业单位职测</el-radio-button>
          </el-radio-group>
          <el-select v-model="year" placeholder="全部年份" clearable style="width: 130px" @change="loadPapers">
            <el-option v-for="y in years" :key="y" :label="y + ' 年'" :value="y" />
          </el-select>
          <el-button type="primary" @click="loadPapers">
            <el-icon><Search /></el-icon>查询
          </el-button>
        </div>
      </div>

      <div v-loading="loading">
        <div v-for="p in papers" :key="p.id" class="paper-card">
          <div class="paper-info">
            <div class="paper-title-row">
              <span class="paper-title">{{ p.title }}</span>
              <el-tag v-if="p.subject === '职测'" size="small" type="warning">职测</el-tag>
              <el-tag size="small" :type="tagType(p.year)">{{ p.year }}</el-tag>
              <el-tag size="small" type="info">{{ p.version }}</el-tag>
            </div>
            <div class="paper-meta">
              共 {{ p.questionCount }} 题
              <template v-if="stats[p.id]">
                · 已答 {{ stats[p.id].answered }} 题 · 正确 {{ stats[p.id].correct }} 题
                · 正确率 {{ stats[p.id].answered ? Math.round(stats[p.id].correct * 100 / stats[p.id].answered) : 0 }}%
              </template>
            </div>
            <el-progress
              v-if="stats[p.id] && p.questionCount"
              :percentage="Math.round(stats[p.id].answered * 100 / p.questionCount)"
              :stroke-width="8"
            />
          </div>
          <div class="paper-actions">
            <el-button type="primary" @click="start(p.id)">
              {{ stats[p.id] && stats[p.id].answered > 0 ? '继续练习' : '开始练习' }}
            </el-button>
          </div>
        </div>
        <el-empty v-if="!loading && !papers.length" description="暂无试卷" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { listPapers, recordStats } from '@/api/exam'

const router = useRouter()
const papers = ref([])
const stats = ref({})
const loading = ref(false)
const year = ref(null)
const subject = ref('')
const years = Array.from({ length: 26 }, (_, i) => 2000 + i)

function tagType(y) {
  if (y >= 2020) return 'danger'
  if (y >= 2015) return 'warning'
  if (y >= 2010) return 'success'
  return 'info'
}

async function loadPapers() {
  loading.value = true
  try {
    const params = {}
    if (year.value) params.year = year.value
    if (subject.value) params.subject = subject.value
    const list = await listPapers(params)
    papers.value = list || []
    const st = {}
    await Promise.all((list || []).map(async p => {
      try {
        const s = await recordStats(p.id)
        st[p.id] = s
      } catch (e) { /* ignore */ }
    }))
    stats.value = st
  } finally {
    loading.value = false
  }
}

function start(paperId) {
  if (!paperId) {
    ElMessage.error('试卷数据异常，请刷新后重试')
    return
  }
  router.push({ path: '/practice/session', query: { mode: 'paper', paperId } })
}

onMounted(loadPapers)
</script>

<style scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
}
.page-title { margin: 0 0 6px; font-size: 20px; }
.page-desc { margin: 0; color: var(--el-text-color-secondary); font-size: 13px; }
.page-actions { display: flex; gap: 8px; }
.paper-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 12px;
  transition: box-shadow .2s;
}
.paper-card:hover { box-shadow: 0 2px 12px rgba(0, 0, 0, .08); }
.paper-info { flex: 1; min-width: 0; padding-right: 16px; }
.paper-title-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.paper-title { font-size: 15px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.paper-meta { font-size: 13px; color: var(--el-text-color-secondary); margin-bottom: 8px; }
.paper-actions { flex-shrink: 0; }
</style>
