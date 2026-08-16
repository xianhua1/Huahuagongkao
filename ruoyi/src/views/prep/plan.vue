<template>
  <div class="tab">
    <PageHead icon="calendar" title="90 天学习计划" desc="按《备考总纲》排好的完整计划，每天打卡，跟着走就不会迷茫。" />
<!-- 进度总览 -->
    <div class="plan-overview">
      <div class="plan-stat">
        <div class="plan-stat-num">{{ doneCount }}</div>
        <div class="plan-stat-label">已完成任务</div>
      </div>
      <div class="plan-stat">
        <div class="plan-stat-num">{{ checkins }}</div>
        <div class="plan-stat-label">累计打卡天数</div>
      </div>
      <div class="plan-stat">
        <div class="plan-stat-num">{{ pct }}%</div>
        <div class="plan-stat-label">计划完成度</div>
      </div>
      <div class="plan-bar">
        <el-progress :percentage="pct" :stroke-width="14" color="#409eff" />
      </div>
    </div>

    <!-- 今日任务 -->
    <div v-if="nextTask" class="next-task">
      <el-icon color="#e6a23c" :size="20"><Pointer /></el-icon>
      <div>
        <div class="next-task-label">下一个任务</div>
        <div class="next-task-text">{{ nextTask }}</div>
      </div>
      <el-button type="primary" size="small" @click="doNext">完成了</el-button>
    </div>
    <div v-else class="next-task done">
      <el-icon color="#67c23a" :size="20"><CircleCheckFilled /></el-icon>
      <div>
        <div class="next-task-label">恭喜</div>
        <div class="next-task-text">90 天计划全部完成！保持每日一练直到考试～</div>
      </div>
    </div>

    <!-- 周计划 -->
    <div class="week-list">
      <div v-for="(wk, wi) in plan" :key="wi" class="week">
        <div class="week-head" @click="toggleWeek(wi)">
          <el-icon :class="{ open: openWeeks.includes(wi) }"><ArrowRight /></el-icon>
          <span class="week-title">{{ wk.week }}</span>
          <span class="week-pct">{{ weekDone(wi) }}/7</span>
        </div>
        <div v-show="openWeeks.includes(wi)" class="week-tasks">
          <div
            v-for="(task, ti) in wk.tasks"
            :key="ti"
            class="task-row"
            :class="{ done: isDone(wi, ti), today: isTodayTask(wi, ti) }"
            @click="toggleTask(wi, ti)"
          >
            <el-icon class="task-check">
              <CircleCheckFilled v-if="isDone(wi, ti)" />
              <CircleCheck v-else />
            </el-icon>
            <span class="task-text">{{ task }}</span>
            <span v-if="isTodayTask(wi, ti)" class="task-today">今日</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import useUserStore from '@/store/modules/user'
import { ArrowRight, CircleCheck, CircleCheckFilled, Pointer } from '@element-plus/icons-vue'
import { plan } from './data/plan'
import { load, save, today, addCheckin } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const doneSet = ref(new Set())
const openWeeks = ref([0])
const checkins = ref(0)

const TOTAL = plan.reduce((n, w) => n + w.tasks.length, 0)

function dayIndexOf(wi, ti) {
  let idx = 0
  for (let i = 0; i < wi; i++) idx += plan[i].tasks.length
  return idx + ti
}

const doneCount = computed(() => doneSet.value.size)
const pct = computed(() => Math.round(doneSet.value.size / TOTAL * 100))
const flatTasks = computed(() => {
  const arr = []
  plan.forEach((w, wi) => w.tasks.forEach((t, ti) => arr.push({ text: t, idx: dayIndexOf(wi, ti) })))
  return arr
})
const nextTask = computed(() => {
  const t = flatTasks.value.find(x => !doneSet.value.has(x.idx))
  return t ? t.text : ''
})

function isDone(wi, ti) {
  return doneSet.value.has(dayIndexOf(wi, ti))
}
function weekDone(wi) {
  return plan[wi].tasks.filter((_, ti) => isDone(wi, ti)).length
}
function toggleWeek(wi) {
  openWeeks.value = openWeeks.value.includes(wi)
    ? openWeeks.value.filter(x => x !== wi)
    : [...openWeeks.value, wi]
}
function toggleTask(wi, ti) {
  const idx = dayIndexOf(wi, ti)
  if (doneSet.value.has(idx)) {
    doneSet.value.delete(idx)
  } else {
    doneSet.value.add(idx)
    addCheckin(uid.value)
  }
  save(uid.value, 'planDone', [...doneSet.value])
  checkins.value = load(uid.value, 'checkins', []).length
}
function doNext() {
  const t = flatTasks.value.find(x => !doneSet.value.has(x.idx))
  if (t) {
    doneSet.value.add(t.idx)
    save(uid.value, 'planDone', [...doneSet.value])
    addCheckin(uid.value)
    checkins.value = load(uid.value, 'checkins', []).length
  }
}
function isTodayTask(wi, ti) {
  return nextTask.value && nextTask.value === plan[wi].tasks[ti] && !isDone(wi, ti)
}

onMounted(() => {
  doneSet.value = new Set(load(uid.value, 'planDone', []))
  checkins.value = load(uid.value, 'checkins', []).length
  // 默认展开含“今日任务”的那一周
  const t = flatTasks.value.find(x => !doneSet.value.has(x.idx))
  if (t) {
    let acc = 0
    for (let i = 0; i < plan.length; i++) {
      if (t.idx < acc + plan[i].tasks.length) {
        openWeeks.value = [i]
        break
      }
      acc += plan[i].tasks.length
    }
  }
})
</script>

<style scoped>
.plan-overview {
  display: flex; align-items: center; gap: 28px; flex-wrap: wrap;
  background: var(--el-color-primary-light-9);
  border: 1px solid var(--el-color-primary-light-5);
  border-radius: 12px;
  padding: 16px 22px;
  margin-bottom: 16px;
}
.plan-stat { text-align: center; }
.plan-stat-num { font-size: 24px; font-weight: 700; color: var(--el-color-primary); }
.plan-stat-label { font-size: 12px; color: var(--el-text-color-secondary); }
.plan-bar { flex: 1; min-width: 200px; }
.next-task {
  display: flex; align-items: center; gap: 12px;
  border: 1px dashed var(--el-color-warning);
  background: var(--el-color-warning-light-9);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 16px;
}
.next-task.done { border-color: #67c23a; background: #f0f9eb; }
.next-task-label { font-size: 12px; color: var(--el-text-color-secondary); }
.next-task-text { font-size: 14px; color: var(--el-text-color-primary); line-height: 1.6; }
.next-task .el-button { margin-left: auto; }
.week-list { display: flex; flex-direction: column; gap: 10px; }
.week { border: 1px solid var(--el-border-color-light); border-radius: 10px; overflow: hidden; }
.week-head {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; cursor: pointer;
  background: var(--el-fill-color-light);
  font-weight: 600; font-size: 14px;
}
.week-head .el-icon { transition: transform .2s; color: var(--el-text-color-secondary); }
.week-head .el-icon.open { transform: rotate(90deg); }
.week-title { flex: 1; }
.week-pct { font-size: 12px; color: var(--el-text-color-secondary); font-weight: 400; }
.week-tasks { padding: 6px 0; }
.task-row {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 18px; cursor: pointer;
  font-size: 14px; color: var(--el-text-color-regular);
  border-bottom: 1px dashed var(--el-border-color-lighter);
}
.task-row:last-child { border-bottom: none; }
.task-row:hover { background: var(--el-fill-color-light); }
.task-check { color: var(--el-text-color-placeholder); flex-shrink: 0; }
.task-row.done .task-check { color: #67c23a; }
.task-row.done .task-text { text-decoration: line-through; color: var(--el-text-color-placeholder); }
.task-row.today { background: var(--el-color-primary-light-9); }
.task-today {
  margin-left: auto; flex-shrink: 0;
  font-size: 12px; color: #fff; background: var(--el-color-primary);
  border-radius: 8px; padding: 1px 8px;
}
.task-text { line-height: 1.6; }
</style>
