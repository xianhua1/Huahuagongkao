<template>
  <div class="tab">
    <PageHead icon="clock" title="计时工具" desc="模拟考试计时与专项限时训练。倒计时结束自动提醒，历史记录保存在本地。" />

    <div class="timer-layout">
      <!-- 计时区 -->
      <div class="timer-panel">
        <div class="tabs">
          <el-radio-group v-model="mode" size="small">
            <el-radio-button value="countdown">⏳ 倒计时</el-radio-button>
            <el-radio-button value="stopwatch">⏱️ 正计时</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 倒计时 -->
        <template v-if="mode === 'countdown'">
          <div class="preset-bar">
            <el-select v-model="preset" size="small" style="width: 180px" @change="applyPreset">
              <el-option label="自定义" value="custom" />
              <el-option-group label="行测">
                <el-option label="常识判断 15 分钟" value="15" />
                <el-option label="言语理解 40 分钟" value="40" />
                <el-option label="数量关系 10 分钟" value="10" />
                <el-option label="判断推理 35 分钟" value="35" />
                <el-option label="资料分析 20 分钟" value="20" />
              </el-option-group>
              <el-option-group label="申论">
                <el-option label="申论整卷 150 分钟" value="150" />
                <el-option label="单题 25 分钟" value="25" />
              </el-option-group>
            </el-select>
            <div class="set-time">
              <el-input-number v-model="minutes" :min="1" :max="600" size="small" controls-position="right" />
              <span>分钟</span>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="set-time">
            <el-tag size="small" type="info">正计时：开始后累计用时，随时暂停</el-tag>
          </div>
        </template>

        <div class="clock" :class="{ warn: mode === 'countdown' && running && remain <= 60 }">
          {{ display }}
        </div>

        <div class="ctrl">
          <el-button type="primary" size="large" @click="start">{{ running ? '暂停' : paused ? '继续' : '开始' }}</el-button>
          <el-button size="large" @click="reset">重置</el-button>
          <el-button size="large" plain @click="finish">结束并记录</el-button>
        </div>

        <div v-if="finished" class="finish-msg">
          {{ mode === 'countdown' ? '⏰ 时间到！' : '⏹️ 已结束' }}
          {{ lastNote }}
        </div>
      </div>

      <!-- 历史记录 -->
      <div class="history-panel">
        <div class="hp-head">
          <span>📋 练习记录（{{ records.length }}）</span>
          <el-button size="small" text type="danger" @click="clearHistory">清空</el-button>
        </div>
        <div v-if="!records.length" class="hp-empty">暂无记录，开始一次计时试试。</div>
        <div v-for="(r, i) in records" :key="i" class="hp-item">
          <div class="hp-top">
            <span class="hp-name">{{ r.name }}</span>
            <span class="hp-time">{{ r.duration }}</span>
          </div>
          <div class="hp-sub">{{ r.date }} · {{ r.kind }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import useUserStore from '@/store/modules/user'
import { load, save, today } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const mode = ref('countdown')
const preset = ref('custom')
const minutes = ref(120)
const remain = ref(0) // 倒计时剩余秒数
const elapsed = ref(0) // 正计时秒数
const running = ref(false)
const paused = ref(false)
const finished = ref(false)
const lastNote = ref('')
const records = ref([])

let timer = null
const startAt = ref('')

const display = computed(() => {
  const s = mode.value === 'countdown' ? remain.value : elapsed.value
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return (h ? String(h).padStart(2, '0') + ':' : '') + String(m).padStart(2, '0') + ':' + String(sec).padStart(2, '0')
})

function applyPreset(v) {
  if (v !== 'custom') minutes.value = Number(v)
}
function start() {
  if (mode.value === 'countdown' && remain.value <= 0) remain.value = minutes.value * 60
  if (mode.value === 'stopwatch' && !running.value && !paused.value) elapsed.value = 0
  if (!running.value) {
    running.value = true
    paused.value = false
    finished.value = false
    startAt.value = new Date().toLocaleTimeString()
    timer = setInterval(tick, 1000)
  }
}
function tick() {
  if (mode.value === 'countdown') {
    remain.value--
    if (remain.value <= 0) {
      remain.value = 0
      stopTick()
      finished.value = true
      lastNote.value = '倒计时结束'
      record()
    }
  } else {
    elapsed.value++
  }
}
function stopTick() {
  clearInterval(timer)
  timer = null
}
function pause() {
  if (running.value) {
    stopTick()
    running.value = false
    paused.value = true
  }
}
function reset() {
  stopTick()
  running.value = false
  paused.value = false
  finished.value = false
  remain.value = mode.value === 'countdown' ? minutes.value * 60 : 0
  elapsed.value = 0
  lastNote.value = ''
}
function finish() {
  if (running.value) stopTick()
  running.value = false
  paused.value = false
  finished.value = true
  lastNote.value = '手动结束'
  record()
}
function record() {
  const dur = mode.value === 'countdown'
    ? fmt(minutes.value * 60 - remain.value)
    : fmt(elapsed.value)
  const name = presetName()
  records.value.unshift({
    name: mode.value === 'countdown' ? `倒计时·${name}` : `正计时·${name}`,
    duration: dur,
    date: today() + ' ' + startAt.value,
    kind: mode.value === 'countdown' ? '限时训练' : '计时训练'
  })
  records.value = records.value.slice(0, 50)
  save(uid.value, 'timerRecords', records.value)
}
function presetName() {
  if (mode.value === 'stopwatch') return '自由计时'
  if (preset.value === 'custom') return '自定义 ' + minutes.value + ' 分钟'
  const map = {
    15: '常识判断', 40: '言语理解', 10: '数量关系', 35: '判断推理', 20: '资料分析', 150: '申论整卷', 25: '申论单题'
  }
  return map[preset.value] + ' ' + preset.value + ' 分钟'
}
function fmt(s) {
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return (h ? h + '时' : '') + (m || h ? m + '分' : '') + sec + '秒'
}
function clearHistory() {
  records.value = []
  save(uid.value, 'timerRecords', [])
}

onMounted(() => {
  records.value = load(uid.value, 'timerRecords', [])
  remain.value = minutes.value * 60
})
onBeforeUnmount(() => stopTick())
</script>

<style scoped>
.timer-layout { display: flex; gap: 24px; flex-wrap: wrap; }
.timer-panel {
  flex: 1 1 380px;
  max-width: 560px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 14px;
  padding: 24px;
}
.tabs { margin-bottom: 16px; }
.preset-bar { display: flex; gap: 12px; align-items: center; margin-bottom: 18px; flex-wrap: wrap; }
.set-time { display: flex; gap: 8px; align-items: center; font-size: 13px; color: var(--el-text-color-secondary); }
.clock {
  font-size: 64px;
  font-weight: 800;
  letter-spacing: 3px;
  text-align: center;
  padding: 30px 0;
  font-variant-numeric: tabular-nums;
  color: var(--el-color-primary);
  font-family: 'Consolas', 'Menlo', monospace;
}
.clock.warn { color: #f56c6c; animation: blink 1s step-start infinite; }
@keyframes blink { 50% { opacity: .35; } }
.ctrl { display: flex; gap: 12px; justify-content: center; }
.finish-msg { margin-top: 16px; text-align: center; font-size: 15px; font-weight: 700; color: #e6a23c; }
.history-panel { flex: 1 1 300px; min-width: 260px; }
.hp-head { display: flex; justify-content: space-between; align-items: center; font-size: 15px; font-weight: 700; margin-bottom: 12px; }
.hp-empty { color: var(--el-text-color-secondary); font-size: 13px; padding: 30px 0; text-align: center; }
.hp-item { border: 1px solid var(--el-border-color-light); border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; }
.hp-top { display: flex; justify-content: space-between; align-items: center; }
.hp-name { font-size: 14px; font-weight: 600; }
.hp-time { font-size: 15px; font-weight: 700; color: var(--el-color-primary); }
.hp-sub { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }
</style>
