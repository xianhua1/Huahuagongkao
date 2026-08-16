<template>
  <div class="tab">
    <PageHead icon="trend" title="学习报告" desc="刷题数据来自答题记录，学习进度来自备考中心各模块。知己知彼，才能有的放矢。" />
<div v-if="loading" class="empty">正在统计……</div>

    <template v-else>
      <!-- 刷题统计 -->
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-num">{{ stats.answered || 0 }}</div>
          <div class="stat-label">累计做题</div>
        </div>
        <div class="stat-card ok">
          <div class="stat-num">{{ stats.correct || 0 }}</div>
          <div class="stat-label">答对</div>
        </div>
        <div class="stat-card bad">
          <div class="stat-num">{{ stats.wrong || 0 }}</div>
          <div class="stat-label">答错</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">{{ rate }}%</div>
          <div class="stat-label">总正确率</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">{{ checkins }}</div>
          <div class="stat-label">打卡天数</div>
        </div>
      </div>

      <!-- 分模块正确率 -->
      <div class="block">
        <div class="block-title">各模块正确率（薄弱模块一眼可见）</div>
        <div v-if="!sections.length" class="empty small">
          还没有答题记录，先去「刷题中心」做几套题，或先在「每日一练」练起来吧～
        </div>
        <div v-else>
          <div v-for="s in sections" :key="s.section" class="sec-row">
            <span class="sec-name">{{ s.section }}</span>
            <div class="sec-bar">
              <div class="sec-fill" :style="{ width: secRate(s) + '%', background: secColor(s) }"></div>
            </div>
            <span class="sec-num">{{ secRate(s) }}%（{{ s.correct }}/{{ s.total }}）</span>
          </div>
          <div class="weak-tip" v-if="weakest">
            <el-icon color="#e6a23c"><Warning /></el-icon>
            <span>最薄弱：<b>{{ weakest.section }}</b>（{{ secRate(weakest) }}%），建议回看
              <a :href="'#' + sectionDoc(weakest.section)">{{ sectionDocName(weakest.section) }}</a> 再专项刷题。
            </span>
          </div>
        </div>
      </div>

      <!-- 学习进度 -->
      <div class="block">
        <div class="block-title">备考中心学习进度</div>
        <div class="prog-grid">
          <div v-for="p in progress" :key="p.name" class="prog-item">
            <div class="prog-name">{{ p.name }}</div>
            <el-progress :percentage="p.pct" :stroke-width="10" :color="p.color" />
          </div>
        </div>
      </div>

      <!-- 学习建议 -->
      <div class="block advice">
        <div class="block-title">💡 学习建议</div>
        <ul class="advice-list">
          <li>正确率低于 60% 的模块：先回看对应教程（资料/判断/言语/数量），再刷 30 道专项题</li>
          <li>每日一练别断：10 分钟 / 天，保持题感比周末猛刷 3 小时更有效</li>
          <li>错题本每周清理一遍：做对的移出，做错的标星重做</li>
          <li>考前 2 周开始整卷模考，训练时间分配</li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import useUserStore from '@/store/modules/user'
import request from '@/utils/request'
import { Warning } from '@element-plus/icons-vue'
import { checkinCount, load } from './store'
import { chengyu } from './data/chengyu'
import { guifan } from './data/guifan'
import { cards } from './data/cards'
import { plan } from './data/plan'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const loading = ref(true)
const stats = ref({})
const sections = ref([])
const checkins = ref(0)

const rate = computed(() => {
  const t = (stats.value.answered || 0)
  return t ? Math.round((stats.value.correct || 0) / t * 100) : 0
})

function secRate(s) {
  return s.total ? Math.round(s.correct / s.total * 100) : 0
}
function secColor(s) {
  const r = secRate(s)
  return r >= 80 ? '#67c23a' : r >= 60 ? '#409eff' : '#f56c6c'
}
const weakest = computed(() => {
  if (!sections.value.length) return null
  return [...sections.value].sort((a, b) => secRate(a) - secRate(b))[0]
})
function sectionDoc(section) {
  return {
    '常识判断': 'cs',
    '言语理解与表达': 'yy',
    '数量关系': 'sl',
    '判断推理': 'pd',
    '资料分析': 'zl'
  }[section] || 'gk-zonggang'
}
function sectionDocName(section) {
  return {
    '常识判断': '常识判断全攻略',
    '言语理解与表达': '言语理解全攻略',
    '数量关系': '数量关系全攻略',
    '判断推理': '判断推理全攻略',
    '资料分析': '资料分析全攻略'
  }[section] || '备考总纲'
}

const progress = ref([])

onMounted(async () => {
  checkins.value = checkinCount(uid.value)
  try {
    const res = await request.get('/exam/dashboard')
    stats.value = res.data || {}
  } catch (e) {
    /* ignore */
  }
  try {
    const res2 = await request.get('/exam/record/section-stats')
    sections.value = (res2.data || []).map(s => ({
      section: s.section,
      total: Number(s.total || 0),
      correct: Number(s.correct || 0)
    }))
  } catch (e) {
    /* ignore */
  }

  const cyDone = new Set(load(uid.value, 'chengyuDone', []))
  const gfDone = new Set(load(uid.value, 'guifanDone', []))
  const cdDone = new Set(load(uid.value, 'cardKnown', []))
  const plDone = new Set(load(uid.value, 'planDone', []))
  const totalPlan = plan.reduce((n, w) => n + w.tasks.length, 0)

  progress.value = [
    { name: '高频成语', pct: Math.round(cyDone.size / chengyu.length * 100), color: '#409eff' },
    { name: '申论规范词', pct: Math.round(gfDone.size / (guifan.reduce((n, t) => n + t.items.length, 0)) * 100), color: '#67c23a' },
    { name: '速记卡片', pct: Math.round(cdDone.size / cards.length * 100), color: '#e6a23c' },
    { name: '学习计划', pct: Math.round(plDone.size / totalPlan * 100), color: '#f56c6c' }
  ]
  loading.value = false
})
</script>

<style scoped>
.empty { text-align: center; padding: 60px 0; color: var(--el-text-color-secondary); font-size: 14px; }
.empty.small { padding: 20px 0; }
.stat-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: 22px; }
.stat-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  background: var(--el-color-primary-light-9);
}
.stat-card.ok { background: #f0f9eb; }
.stat-card.bad { background: #fef0f0; }
.stat-num { font-size: 26px; font-weight: 700; color: var(--el-color-primary); }
.stat-card.ok .stat-num { color: #67c23a; }
.stat-card.bad .stat-num { color: #f56c6c; }
.stat-label { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }
.block { margin-bottom: 22px; max-width: 860px; }
.block-title { font-size: 15px; font-weight: 700; color: var(--el-color-primary); margin-bottom: 12px; }
.sec-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.sec-name { width: 130px; flex-shrink: 0; font-size: 13px; color: var(--el-text-color-regular); }
.sec-bar { flex: 1; height: 16px; background: var(--el-fill-color-light); border-radius: 8px; overflow: hidden; }
.sec-fill { height: 100%; border-radius: 8px; transition: width .5s; }
.sec-num { width: 110px; flex-shrink: 0; text-align: right; font-size: 12px; color: var(--el-text-color-secondary); }
.weak-tip {
  display: flex; align-items: center; gap: 8px;
  background: var(--el-color-warning-light-9);
  border: 1px dashed var(--el-color-warning);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  margin-top: 12px;
}
.weak-tip a { color: var(--el-color-primary); text-decoration: none; border-bottom: 1px dashed var(--el-color-primary); }
.prog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.prog-item { border: 1px solid var(--el-border-color-light); border-radius: 10px; padding: 12px 14px; }
.prog-name { font-size: 13px; margin-bottom: 8px; color: var(--el-text-color-regular); }
.advice { background: var(--el-color-primary-light-9); border-radius: 12px; padding: 16px 20px; }
.advice-list { margin: 0; padding-left: 20px; font-size: 13px; color: var(--el-text-color-regular); line-height: 2; }
</style>
