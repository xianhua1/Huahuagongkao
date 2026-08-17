<template>
  <div class="app-container">
    <el-card shadow="never">
      <div class="page-head">
        <div>
          <h2 class="page-title">历年真题练习</h2>
          <p class="page-desc">国考 / 省考 / 事业单位历年《行测》真题，含资料分析材料联动与逐题解析</p>
        </div>
      </div>

      <!-- 便捷搜索：分类标签 + 年份 + 查询 -->
      <div class="quick-search">
        <div class="qs-tags">
          <span
            class="qs-tag"
            :class="{ active: category === '' }"
            @click="category = ''; loadPapers()"
          >全部</span>
          <span
            v-for="c in categories"
            :key="c"
            class="qs-tag"
            :class="{ active: category === c }"
            @click="category = c; loadPapers()"
          >{{ c }}</span>
        </div>
        <div class="qs-actions">
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
const category = ref('')
const years = Array.from({ length: 26 }, (_, i) => 2000 + i)

// 分类固定顺序（国考 → 各省 → 事业编）
const CAT_ORDER = ['国考', '安徽', '福建', '甘肃', '广东', '广西', '贵州', '海南', '河北', '河南', '黑龙江', '湖北', '湖南', '吉林', '江苏', '江西', '辽宁', '内蒙古', '宁夏', '青海', '山东', '山西', '陕西', '四川', '新疆', '云南', '浙江', '北京市', '上海市', '天津市', '重庆市', '深圳市', '事业编']
const categories = ref([])

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
    if (category.value) params.version = category.value
    const list = await listPapers(params)
    papers.value = list || []
    // 分类列表（首次全量拉取时收集）
    if (!category.value) {
      const exist = new Set((list || []).map(p => p.version).filter(Boolean))
      categories.value = CAT_ORDER.filter(c => exist.has(c))
    }
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
.page-head { margin-bottom: 16px; }
.page-title { margin: 0 0 6px; font-size: 20px; }
.page-desc { margin: 0; color: var(--el-text-color-secondary); font-size: 13px; }

/* 便捷搜索 */
.quick-search {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 12px 14px;
  margin-bottom: 16px;
  background: var(--el-fill-color-light);
  border-radius: 10px;
  flex-wrap: wrap;
}
.qs-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
  min-width: 200px;
}
.qs-tag {
  font-size: 12px;
  color: var(--el-text-color-regular);
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 999px;
  padding: 3px 12px;
  cursor: pointer;
  transition: all .15s;
  user-select: none;
}
.qs-tag:hover { border-color: var(--el-color-primary); color: var(--el-color-primary); }
.qs-tag.active {
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
  color: #fff;
  font-weight: 600;
}
.qs-actions { display: flex; gap: 8px; flex-shrink: 0; }

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
