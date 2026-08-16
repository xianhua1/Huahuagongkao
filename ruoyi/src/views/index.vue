<template>
  <div class="dash-page">
    <!-- ============ 主视觉区 ============ -->
    <section class="hero">
      <div class="hero-bg">
        <span class="orb orb-1"></span>
        <span class="orb orb-2"></span>
        <span class="orb orb-3"></span>
        <span class="grid-mask"></span>
      </div>
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          国考行测真题 · 2000-2022 全收录
        </div>
        <h1 class="hero-title">
          刷题，就是<span class="grad-text">现在</span>
        </h1>
        <p class="hero-sub">
          {{ nickName }}，距离上岸还差一套真题的距离。
          <br class="hide-mobile" />
          今天已答 <b class="hl">{{ statsData.answered || 0 }}</b> 题，正确率 <b class="hl">{{ accuracy }}%</b>，继续加油！
        </p>
        <div class="hero-actions">
          <el-button class="btn-primary" size="large" @click="go('/practice/papers')">
            <el-icon><Document /></el-icon>&nbsp;开始刷题
          </el-button>
          <el-button class="btn-ghost" size="large" @click="go('/practice/random')">
            <el-icon><RefreshRight /></el-icon>&nbsp;随机练习
          </el-button>
        </div>
      </div>
      <div class="hero-side">
        <div class="big-num">{{ statsData.papers || 0 }}</div>
        <div class="big-label">套历年真题</div>
        <div class="big-sub">36 套行测卷 · 4600+ 道题</div>
      </div>
    </section>

    <!-- ============ 数据看板 ============ -->
    <section class="stat-section">
      <div class="stat-card" v-for="(s, i) in statList" :key="s.label" :style="{ '--accent': s.color, '--delay': i * 60 + 'ms' }">
        <div class="stat-icon" :style="{ background: s.color + '22', color: s.color }">
          <el-icon :size="22"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-num" :style="{ color: s.color }">{{ animateNum(s.value) }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </section>

    <!-- ============ 快捷入口 ============ -->
    <section class="quick-section">
      <div class="quick-card" v-for="q in quicks" :key="q.title" @click="go(q.path)">
        <div class="quick-top">
          <div class="quick-icon" :style="{ background: q.bg, boxShadow: '0 8px 20px ' + q.bg + '66' }">
            <el-icon :size="26" color="#fff"><component :is="q.icon" /></el-icon>
          </div>
          <span class="quick-arrow">→</span>
        </div>
        <div class="quick-title">{{ q.title }}</div>
        <div class="quick-desc">{{ q.desc }}</div>
        <div class="quick-tags">
          <span v-for="t in q.tags" :key="t" class="quick-tag">{{ t }}</span>
        </div>
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
import { Document, RefreshRight, CircleClose, Reading, Collection, DataLine, Star, InfoFilled, Aim, List, TrendCharts } from '@element-plus/icons-vue'
import { dashboardStats } from '@/api/exam'
import { getInfo } from '@/api/login'

const router = useRouter()
const nickName = ref('同学')
const statsData = ref({})
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

const quicks = [
  {
    title: '试卷练习', icon: Reading,
    desc: '按年份逐套刷真题，进度自动保存，随时续练',
    path: '/practice/papers', bg: 'linear-gradient(135deg,#409eff,#7ecbff)',
    tags: ['2000-2022', '资料分析联动', '逐题解析']
  },
  {
    title: '随机练习', icon: RefreshRight,
    desc: '按题型随机抽题，短平快，通勤摸鱼也能刷',
    path: '/practice/random', bg: 'linear-gradient(135deg,#36cfc9,#86e8e2)',
    tags: ['五大题型', '即刷即判']
  },
  {
    title: '错题本', icon: Star,
    desc: '错题自动收录，回顾强化，消灭薄弱点',
    path: '/practice/wrong', bg: 'linear-gradient(135deg,#fa8c16,#ffc069)',
    tags: ['自动收录', '一键清空']
  }
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
.dash-page {
  min-height: calc(100vh - 84px);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ---------- 主视觉 ---------- */
.hero {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  background: linear-gradient(120deg, #1a2a6c 0%, #2e5bff 45%, #6a3df0 100%);
  color: #fff;
  padding: 46px 46px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 18px 46px rgba(46, 91, 255, .35);
}
.hero-bg { position: absolute; inset: 0; pointer-events: none; }
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: .5;
  animation: float 8s ease-in-out infinite;
}
.orb-1 { width: 340px; height: 340px; background: #00c6ff; top: -120px; right: 8%; }
.orb-2 { width: 260px; height: 260px; background: #ff7ad9; bottom: -110px; left: 6%; animation-delay: -3s; }
.orb-3 { width: 200px; height: 200px; background: #7cffb2; top: 30%; left: 42%; opacity: .3; animation-delay: -5s; }
.grid-mask {
  position: absolute; inset: 0;
  background-image: linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: radial-gradient(ellipse at 30% 40%, #000 20%, transparent 75%);
}
@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-26px) scale(1.06); }
}
.hero-content { position: relative; z-index: 1; max-width: 640px; }
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  background: rgba(255, 255, 255, .14);
  border: 1px solid rgba(255, 255, 255, .25);
  border-radius: 999px;
  padding: 6px 14px;
  margin-bottom: 18px;
  backdrop-filter: blur(6px);
}
.badge-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #7cffb2;
  box-shadow: 0 0 10px #7cffb2;
  animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
.hero-title {
  margin: 0 0 14px;
  font-size: 46px;
  font-weight: 800;
  letter-spacing: 2px;
  line-height: 1.25;
}
.grad-text {
  background: linear-gradient(90deg, #ffd86b, #ff9a5c, #ff6aa8);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-sub {
  margin: 0 0 26px;
  font-size: 15px;
  line-height: 1.9;
  color: rgba(255, 255, 255, .85);
}
.hl { color: #ffd86b; font-size: 17px; }
.hero-actions { display: flex; gap: 14px; }
.btn-primary {
  background: linear-gradient(135deg, #ffd86b, #ff9a5c) !important;
  border: none !important;
  color: #4a2c00 !important;
  font-weight: 700;
  border-radius: 12px;
  box-shadow: 0 10px 26px rgba(255, 170, 90, .45);
  transition: transform .2s, box-shadow .2s;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(255, 170, 90, .6) !important; }
.btn-ghost {
  background: rgba(255, 255, 255, .12) !important;
  border: 1px solid rgba(255, 255, 255, .35) !important;
  color: #fff !important;
  border-radius: 12px;
  backdrop-filter: blur(6px);
  transition: background .2s;
}
.btn-ghost:hover { background: rgba(255, 255, 255, .22) !important; }
.hero-side {
  position: relative;
  z-index: 1;
  text-align: right;
  flex-shrink: 0;
  padding-left: 30px;
}
.big-num {
  font-size: 76px;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(180deg, #fff, rgba(255, 255, 255, .55));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.big-label { font-size: 18px; margin-top: 6px; color: #ffd86b; font-weight: 700; }
.big-sub { font-size: 13px; color: rgba(255, 255, 255, .7); margin-top: 6px; }

/* ---------- 数据看板 ---------- */
.stat-section {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}
.stat-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  padding: 20px 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: transform .2s, box-shadow .2s;
  animation: rise .5s ease both;
  animation-delay: var(--delay);
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(0, 0, 0, .1); }
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.stat-icon {
  width: 42px; height: 42px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}
.stat-num { font-size: 30px; font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); }

/* ---------- 快捷入口 ---------- */
.quick-section { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.quick-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  padding: 22px 20px;
  cursor: pointer;
  transition: transform .25s, box-shadow .25s, border-color .25s;
  position: relative;
  overflow: hidden;
}
.quick-card::after {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 140px; height: 140px;
  border-radius: 50%;
  background: var(--q-bg, transparent);
  opacity: .12;
  transition: transform .3s;
}
.quick-card:hover { transform: translateY(-5px); box-shadow: 0 16px 34px rgba(0, 0, 0, .12); border-color: var(--el-color-primary); }
.quick-card:hover::after { transform: scale(1.4); }
.quick-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.quick-icon {
  width: 48px; height: 48px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
}
.quick-arrow { font-size: 20px; color: var(--el-text-color-placeholder); transition: transform .25s, color .25s; }
.quick-card:hover .quick-arrow { transform: translateX(5px); color: var(--el-color-primary); }
.quick-title { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
.quick-desc { font-size: 13px; color: var(--el-text-color-secondary); line-height: 1.7; margin-bottom: 12px; }
.quick-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.quick-tag {
  font-size: 12px;
  color: var(--el-text-color-regular);
  background: var(--el-fill-color-light);
  border-radius: 999px;
  padding: 3px 10px;
}

/* ---------- 底部标语 ---------- */
.motto {
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: center;
  padding: 8px 0 4px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}
.motto-line { height: 1px; width: 90px; background: linear-gradient(90deg, transparent, var(--el-border-color)); }

@media (max-width: 1100px) {
  .stat-section { grid-template-columns: repeat(3, 1fr); }
  .quick-section { grid-template-columns: repeat(2, 1fr); }
  .hero-side { display: none; }
}
@media (max-width: 700px) {
  .stat-section { grid-template-columns: repeat(2, 1fr); }
  .quick-section { grid-template-columns: 1fr; }
  .hero { padding: 30px 22px; }
  .hero-title { font-size: 34px; }
  .hero-actions { flex-direction: column; align-items: stretch; }
  .hide-mobile { display: none; }
}
</style>
