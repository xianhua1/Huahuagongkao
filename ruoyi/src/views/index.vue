<template>
  <div class="portal">
    <!-- ============ 顶部工具条 ============ -->
    <div class="topbar">
      <div class="topbar-logo">
        <img src="@/assets/logo/logo.png" class="logo-img" alt="花花公考刷题" />
        <span class="logo-name">花花公考刷题</span>
        <span class="logo-badge">国考 · 行测 · 申论</span>
      </div>
      <div class="topbar-search">
        <el-input
          v-model="kw"
          placeholder="搜索知识点、教程、真题年份…"
          size="large"
          clearable
          @keyup.enter="doSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
          <template #suffix>
            <el-button v-if="kw" type="primary" size="small" class="search-btn" @click="doSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
      <div class="topbar-links">
        <a @click="go('/docs')">📚 资料教程</a>
        <a @click="go('/practice/papers')">📝 题库</a>
        <a @click="go('/practice/shenlun')">✍️ 申论</a>
        <a @click="go('/report')">📊 学习报告</a>
      </div>
    </div>

    <!-- ============ 大 Banner ============ -->
    <section class="banner">
      <div class="banner-deco d1"></div>
      <div class="banner-deco d2"></div>
      <div class="banner-deco d3"></div>
      <div class="banner-main">
        <div class="banner-badge"><span class="dot"></span> 国考行测真题 2000-2022 全收录</div>
        <h1 class="banner-title">刷题，就是<span class="grad">现在</span></h1>
        <p class="banner-sub">
          {{ nickName }}，你好！今天已答 <b>{{ statsData.answered || 0 }}</b> 题，正确率 <b>{{ accuracy }}%</b>。
          <br />每一道题，都离上岸更近一步。
        </p>
        <div class="banner-actions">
          <el-button class="b-btn-main" size="large" @click="go('/practice/papers')">🚀 开始刷题</el-button>
          <el-button class="b-btn-ghost" size="large" @click="go('/practice/shenlun')">✍️ 申论作答</el-button>
          <el-button class="b-btn-ghost" size="large" @click="go('/prep/chengyu')">🎯 备考中心</el-button>
        </div>
      </div>
      <div class="banner-side">
        <div class="b-num">{{ statsData.papers || 0 }}</div>
        <div class="b-label">套历年真题</div>
        <div class="b-sub">{{ statsData.questions || 0 }} 道题 · {{ statsData.materials || 0 }} 段材料</div>
      </div>
    </section>

    <!-- ============ 功能模块 ============ -->
    <section class="modules">
      <div v-for="m in modules" :key="m.title" class="mod-card" @click="go(m.path)">
        <div class="mod-icon" :style="{ background: m.bg }">
          <el-icon :size="26" color="#fff"><component :is="m.icon" /></el-icon>
        </div>
        <div class="mod-info">
          <div class="mod-title">{{ m.title }}</div>
          <div class="mod-desc">{{ m.desc }}</div>
          <div class="mod-tags">
            <span v-for="t in m.tags" :key="t">{{ t }}</span>
          </div>
        </div>
        <span class="mod-arrow">→</span>
      </div>
    </section>

    <!-- ============ 数据看板 ============ -->
    <section class="stats">
      <div v-for="(s, i) in statList" :key="s.label" class="stat-card" :style="{ '--accent': s.color, '--delay': i * 60 + 'ms' }">
        <div class="stat-icon" :style="{ background: s.color + '1f', color: s.color }">
          <el-icon :size="20"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-num" :style="{ color: s.color }">{{ animateNum(s.value) }}{{ s.suffix || '' }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </section>

    <!-- ============ 底部标语 ============ -->
    <section class="motto">
      <span class="motto-line"></span>
      <p>道阻且长，行则将至 —— 每一道题，都离上岸更近一步</p>
      <span class="motto-line"></span>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Document, RefreshRight, CircleClose, Reading, Collection, DataLine, Aim, TrendCharts, EditPen, Calendar, Notebook, Search } from '@element-plus/icons-vue'
import logo from '@/assets/logo/logo.png'
import { dashboardStats } from '@/api/exam'
import { getInfo } from '@/api/login'

const router = useRouter()
const nickName = ref('同学')
const statsData = ref({})
const kw = ref('')
let rafId = null
const shown = ref({})

const statList = computed(() => {
  const d = statsData.value || {}
  const answered = Number(d.answered || 0)
  const correct = Number(d.correct || 0)
  return [
    { label: '试卷总数', value: Number(d.papers || 0), color: '#409eff', icon: Collection },
    { label: '题目总数', value: Number(d.questions || 0), color: '#36cfc9', icon: DataLine },
    { label: '已答题数', value: answered, color: '#9254de', icon: Aim },
    { label: '正确率', value: answered ? Math.round(correct * 100 / answered) : 0, suffix: '%', color: '#fa8c16', icon: TrendCharts },
    { label: '错题数', value: Number(d.wrong || 0), color: '#f5222d', icon: CircleClose }
  ]
})

const accuracy = computed(() => {
  const d = statsData.value || {}
  const answered = Number(d.answered || 0)
  return answered ? Math.round(Number(d.correct || 0) * 100 / answered) : 0
})

const modules = [
  { title: '行测刷题', desc: '2000-2022 真题逐套练习，资料联动，逐题解析', path: '/practice/papers', icon: Reading, bg: 'linear-gradient(135deg,#409eff,#7ecbff)', tags: ['36 套真题', '断点续练'] },
  { title: '申论作答', desc: '材料阅读 + 格子答题卡，交卷后 AI 评分分析', path: '/practice/shenlun', icon: EditPen, bg: 'linear-gradient(135deg,#722ed1,#b37feb)', tags: ['格子答题卡', 'AI 评分'] },
  { title: '每日一练', desc: '每天 10 题混模块练习，10 分钟保持手感', path: '/practice/daily', icon: Calendar, bg: 'linear-gradient(135deg,#36cfc9,#86e8e2)', tags: ['自动组卷', '错题收录'] },
  { title: '备考中心', desc: '成语 / 规范词 / 时政 / 速记卡 / 万能模板', path: '/prep/chengyu', icon: Notebook, bg: 'linear-gradient(135deg,#fa8c16,#ffc069)', tags: ['打卡学习', '实时时政'] },
  { title: '资料教程', desc: '零基础到进阶，11 篇全模块教程 + 视频目录', path: '/docs', icon: Document, bg: 'linear-gradient(135deg,#13c2c2,#5cdbd3)', tags: ['小白友好', '真题精讲'] },
  { title: '学习报告', desc: '模块正确率分析，薄弱点一眼可见', path: '/report', icon: TrendCharts, bg: 'linear-gradient(135deg,#f5222d,#ff7875)', tags: ['薄弱定位', '进度追踪'] }
]

function animateNum(target) {
  return Math.round(shown.value[target] ?? 0)
}

function startCountUp() {
  const targets = {}
  statList.value.forEach(s => { targets[s.value] = s.value })
  const keys = Object.keys(targets).map(Number)
  const start = {}
  keys.forEach(k => { start[k] = 0 })
  const dur = 900
  const t0 = performance.now()
  const step = (now) => {
    const p = Math.min(1, (now - t0) / dur)
    const ease = 1 - Math.pow(1 - p, 3)
    keys.forEach(k => { shown.value[k] = Math.round(start[k] + (targets[k] - start[k]) * ease) })
    if (p < 1) rafId = requestAnimationFrame(step)
  }
  rafId = requestAnimationFrame(step)
}

function go(path) {
  router.push(path)
}

function doSearch() {
  const k = kw.value.trim()
  if (k) {
    router.push({ path: '/docs', query: { kw: k } })
  }
}

onMounted(async () => {
  try {
    const info = await getInfo()
    if (info.user && info.user.nickName) nickName.value = info.user.nickName
  } catch (e) { /* ignore */ }
  try {
    statsData.value = await dashboardStats()
  } catch (e) { /* ignore */ }
  startCountUp()
})

onBeforeUnmount(() => {
  if (rafId) cancelAnimationFrame(rafId)
})
</script>

<style scoped>
.portal {
  min-height: calc(100vh - 84px);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ---------- 顶部工具条 ---------- */
.topbar {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  padding: 14px 22px;
  box-shadow: 0 4px 16px rgba(31, 45, 61, .05);
}
.topbar-logo { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.logo-img { width: 42px; height: 42px; border-radius: 10px; object-fit: contain; }
.logo-name { font-size: 19px; font-weight: 800; letter-spacing: 1px; }
.logo-badge {
  font-size: 11px; color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  border-radius: 999px; padding: 2px 10px;
}
.topbar-search { flex: 1; max-width: 520px; }
.search-btn { border-radius: 8px; }
.topbar-links { display: flex; gap: 6px; flex-shrink: 0; }
.topbar-links a {
  font-size: 13px; color: var(--el-text-color-regular);
  padding: 7px 12px; border-radius: 8px; cursor: pointer;
  transition: all .15s; text-decoration: none;
}
.topbar-links a:hover { background: var(--el-color-primary-light-9); color: var(--el-color-primary); }

/* ---------- Banner ---------- */
.banner {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  background: linear-gradient(120deg, #e8f4ff 0%, #f0faff 45%, #f5f0ff 100%);
  border: 1px solid #e0edff;
  padding: 44px 46px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.banner-deco { position: absolute; border-radius: 50%; pointer-events: none; }
.d1 { width: 300px; height: 300px; background: rgba(64, 158, 255, .12); top: -120px; right: 6%; }
.d2 { width: 200px; height: 200px; background: rgba(54, 207, 201, .12); bottom: -90px; left: 8%; }
.d3 { width: 90px; height: 90px; background: rgba(114, 46, 209, .10); top: 20%; right: 32%; }
.banner-main { position: relative; z-index: 1; }
.banner-badge {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--el-color-primary);
  background: rgba(64, 158, 255, .10);
  border-radius: 999px; padding: 6px 14px; margin-bottom: 16px;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--el-color-primary); animation: pulse 1.6s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .3; } }
.banner-title { margin: 0 0 12px; font-size: 44px; font-weight: 800; color: #1f2d3d; letter-spacing: 2px; }
.grad {
  background: linear-gradient(90deg, #409eff, #36cfc9, #722ed1);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.banner-sub { margin: 0 0 24px; font-size: 15px; line-height: 1.9; color: var(--el-text-color-secondary); }
.banner-sub b { color: var(--el-color-primary); }
.banner-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.b-btn-main {
  background: linear-gradient(135deg, #409eff, #36cfc9) !important;
  border: none !important; color: #fff !important; font-weight: 700;
  border-radius: 12px; box-shadow: 0 10px 24px rgba(64, 158, 255, .35);
  transition: transform .2s, box-shadow .2s;
}
.b-btn-main:hover { transform: translateY(-2px); box-shadow: 0 14px 30px rgba(64, 158, 255, .5) !important; }
.b-btn-ghost {
  background: #fff !important;
  border: 1px solid #d9e6ff !important;
  color: var(--el-color-primary) !important;
  border-radius: 12px;
  transition: all .2s;
}
.b-btn-ghost:hover { border-color: var(--el-color-primary) !important; transform: translateY(-2px); }
.banner-side { position: relative; z-index: 1; text-align: right; flex-shrink: 0; padding-left: 30px; }
.b-num {
  font-size: 72px; font-weight: 900; line-height: 1;
  background: linear-gradient(180deg, #409eff, #722ed1);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.b-label { font-size: 17px; margin-top: 6px; color: var(--el-color-primary); font-weight: 700; }
.b-sub { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 6px; }

/* ---------- 功能模块 ---------- */
.modules { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.mod-card {
  display: flex; align-items: center; gap: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: transform .25s, box-shadow .25s, border-color .25s;
}
.mod-card:hover { transform: translateY(-5px); box-shadow: 0 16px 34px rgba(0, 0, 0, .10); border-color: var(--el-color-primary); }
.mod-icon {
  width: 52px; height: 52px; border-radius: 14px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 18px rgba(0, 0, 0, .12);
}
.mod-info { flex: 1; min-width: 0; }
.mod-title { font-size: 17px; font-weight: 700; margin-bottom: 4px; }
.mod-desc { font-size: 12px; color: var(--el-text-color-secondary); line-height: 1.6; margin-bottom: 8px; }
.mod-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.mod-tags span {
  font-size: 11px; color: var(--el-text-color-regular);
  background: var(--el-fill-color-light); border-radius: 999px; padding: 2px 8px;
}
.mod-arrow { font-size: 20px; color: var(--el-text-color-placeholder); transition: transform .25s, color .25s; }
.mod-card:hover .mod-arrow { transform: translateX(5px); color: var(--el-color-primary); }

/* ---------- 数据看板 ---------- */
.stats { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }
.stat-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  padding: 18px 16px;
  display: flex; align-items: center; gap: 12px;
  transition: transform .2s, box-shadow .2s;
  animation: rise .5s ease both;
  animation-delay: var(--delay);
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(0, 0, 0, .10); }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.stat-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-num { font-size: 24px; font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 2px; }

/* ---------- 底部标语 ---------- */
.motto { display: flex; align-items: center; gap: 16px; justify-content: center; padding: 8px 0 4px; color: var(--el-text-color-secondary); font-size: 14px; }
.motto-line { height: 1px; width: 90px; background: linear-gradient(90deg, transparent, var(--el-border-color)); }

@media (max-width: 1100px) {
  .modules { grid-template-columns: repeat(2, 1fr); }
  .stats { grid-template-columns: repeat(3, 1fr); }
  .banner-side { display: none; }
  .topbar { flex-wrap: wrap; }
  .topbar-links { width: 100%; justify-content: flex-end; }
}
@media (max-width: 700px) {
  .modules { grid-template-columns: 1fr; }
  .stats { grid-template-columns: repeat(2, 1fr); }
  .banner { padding: 30px 22px; }
  .banner-title { font-size: 32px; }
  .banner-actions { flex-direction: column; align-items: stretch; }
}
</style>
