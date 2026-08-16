<template>
  <div class="prep-page">
    <!-- 左侧导航 -->
    <aside class="prep-nav">
      <div class="prep-nav-head">
        <el-icon color="#409eff" :size="20"><DataAnalysis /></el-icon>
        <span>备考中心</span>
      </div>
      <div
        v-for="t in tabs"
        :key="t.id"
        class="prep-nav-item"
        :class="{ active: active === t.id }"
        @click="active = t.id"
      >
        <el-icon><component :is="t.icon" /></el-icon>
        <span>{{ t.name }}</span>
      </div>
      <div class="prep-nav-foot">
        <el-icon><Calendar /></el-icon>
        <span>已打卡 {{ checkins }} 天</span>
      </div>
    </aside>

    <!-- 右侧内容 -->
    <main class="prep-main">
      <Daily v-if="active === 'daily'" />
      <Plan v-else-if="active === 'plan'" />
      <Chengyu v-else-if="active === 'chengyu'" />
      <Guifan v-else-if="active === 'guifan'" />
      <Shizheng v-else-if="active === 'shizheng'" />
      <Cards v-else-if="active === 'cards'" />
      <Sucai v-else-if="active === 'sucai'" />
      <Report v-else />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import useUserStore from '@/store/modules/user'
import { DataAnalysis, Calendar, EditPen, Notebook, Reading, Clock, Tickets, Collection, TrendCharts } from '@element-plus/icons-vue'
import { checkinCount } from './store'
import Daily from './daily.vue'
import Plan from './plan.vue'
import Chengyu from './chengyu.vue'
import Guifan from './guifan.vue'
import Shizheng from './shizheng.vue'
import Cards from './cards.vue'
import Sucai from './sucai.vue'
import Report from './report.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')
const active = ref('daily')
const checkins = ref(checkinCount(uid.value))

const tabs = [
  { id: 'daily', name: '每日一练', icon: EditPen },
  { id: 'plan', name: '学习计划', icon: Calendar },
  { id: 'chengyu', name: '成语积累', icon: Reading },
  { id: 'guifan', name: '申论规范词', icon: Notebook },
  { id: 'shizheng', name: '时政速递', icon: Clock },
  { id: 'cards', name: '速记卡片', icon: Tickets },
  { id: 'sucai', name: '申论素材', icon: Collection },
  { id: 'report', name: '学习报告', icon: TrendCharts }
]
</script>

<style scoped>
.prep-page {
  display: flex;
  gap: 18px;
  height: calc(100vh - 84px);
  min-height: 0;
}
.prep-nav {
  width: 190px;
  flex-shrink: 0;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.prep-nav-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  padding: 4px 10px 14px;
}
.prep-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--el-text-color-regular);
  transition: all .15s;
}
.prep-nav-item:hover { background: var(--el-fill-color-light); }
.prep-nav-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: 600;
}
.prep-nav-foot {
  margin-top: auto;
  padding: 12px 12px 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
  border-top: 1px dashed var(--el-border-color-light);
}
.prep-main {
  flex: 1;
  min-width: 0;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  overflow-y: auto;
  padding: 22px 26px 36px;
}
@media (max-width: 900px) {
  .prep-page { flex-direction: column; height: auto; }
  .prep-nav { width: 100%; flex-direction: row; flex-wrap: wrap; gap: 4px; }
  .prep-nav-head, .prep-nav-foot { display: none; }
}
</style>
