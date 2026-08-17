<template>
  <div class="app-container">
    <el-card shadow="never" class="sp-card">
      <h2 class="sp-title">专项练习</h2>
      <p class="sp-desc">按题型专项刷历年真题，直击薄弱模块，做完即出答案与解析</p>

      <div class="sp-section-title">① 选择专项题型</div>
      <div class="sp-grid">
        <div
          v-for="s in sectionList"
          :key="s.name"
          class="sp-item"
          :class="{ active: section === s.name }"
          @click="section = s.name"
        >
          <div class="sp-icon" :style="{ background: s.bg }">
            <el-icon :size="24" color="#fff"><component :is="s.icon" /></el-icon>
          </div>
          <div class="sp-info">
            <div class="sp-name">{{ s.name }}</div>
            <div class="sp-tip">{{ s.tip }}</div>
          </div>
          <el-icon v-if="section === s.name" class="sp-check"><CircleCheckFilled /></el-icon>
        </div>
      </div>

      <div class="sp-section-title">② 选择题量</div>
      <div class="sp-counts">
        <el-radio-group v-model="count">
          <el-radio-button :value="10">10 题</el-radio-button>
          <el-radio-button :value="20">20 题</el-radio-button>
          <el-radio-button :value="30">30 题</el-radio-button>
          <el-radio-button :value="50">50 题</el-radio-button>
        </el-radio-group>
      </div>

      <el-button type="primary" size="large" class="sp-start" @click="start">
        🚀 开始{{ section ? '「' + section + '」' : '' }}专项练习
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Reading, EditPen, DataLine, MagicStick, TrendCharts, List, CircleCheckFilled } from '@element-plus/icons-vue'

const router = useRouter()
const section = ref('')
const count = ref(10)

const sectionList = [
  { name: '常识判断', tip: '时政 · 法律 · 科技 · 历史', bg: 'linear-gradient(135deg,#409eff,#7ecbff)', icon: Reading },
  { name: '言语理解与表达', tip: '逻辑填空 · 片段阅读 · 语句表达', bg: 'linear-gradient(135deg,#36cfc9,#86e8e2)', icon: EditPen },
  { name: '数量关系', tip: '工程 · 行程 · 利润 · 排列组合', bg: 'linear-gradient(135deg,#fa8c16,#ffc069)', icon: DataLine },
  { name: '判断推理', tip: '图形 · 定义 · 类比 · 逻辑', bg: 'linear-gradient(135deg,#722ed1,#b37feb)', icon: MagicStick },
  { name: '资料分析', tip: '增长率 · 比重 · 平均数 · 速算', bg: 'linear-gradient(135deg,#13c2c2,#5cdbd3)', icon: TrendCharts },
  { name: '全部混刷', tip: '五大题型随机抽取', bg: 'linear-gradient(135deg,#f5222d,#ff7875)', icon: List }
]

function start() {
  router.push({
    path: '/practice/session',
    query: { mode: 'random', section: section.value, count: count.value }
  })
}
</script>

<style scoped>
.sp-card { max-width: 760px; margin: 30px auto; padding: 10px 26px 30px; }
.sp-title { text-align: center; margin: 14px 0 6px; font-size: 22px; }
.sp-desc { text-align: center; color: var(--el-text-color-secondary); font-size: 13px; margin-bottom: 24px; }
.sp-section-title { font-size: 14px; font-weight: 700; color: var(--el-text-color-primary); margin: 18px 0 12px; }
.sp-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.sp-item {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 2px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all .18s;
  position: relative;
}
.sp-item:hover { border-color: var(--el-color-primary); transform: translateY(-2px); }
.sp-item.active { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.sp-icon {
  width: 46px; height: 46px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.sp-info { flex: 1; min-width: 0; }
.sp-name { font-size: 15px; font-weight: 700; }
.sp-tip { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 3px; }
.sp-check { color: var(--el-color-primary); font-size: 20px; }
.sp-counts { margin-bottom: 6px; }
.sp-start { width: 100%; margin-top: 26px; height: 46px; font-size: 16px; border-radius: 10px; }
@media (max-width: 640px) { .sp-grid { grid-template-columns: 1fr; } }
</style>
