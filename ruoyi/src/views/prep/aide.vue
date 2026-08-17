<template>
  <div class="tab">
    <PageHead icon="trend" title="行测助手 · 口算练习" desc="每日一组口算，练出资料分析的心算速度。输入答案后回车或 Tab 进入下一题，结束自动评分。" />

    <!-- 配置 -->
    <div v-if="!started" class="config">
      <div class="cfg-row">
        <span class="cfg-label">练习类型</span>
        <el-radio-group v-model="cat">
          <el-radio-button value="base">基础计算</el-radio-button>
          <el-radio-button value="data">资料专项</el-radio-button>
          <el-radio-button value="other">其他训练</el-radio-button>
        </el-radio-group>
      </div>
      <div class="cfg-row">
        <span class="cfg-label">题型</span>
        <el-radio-group v-model="sub">
          <template v-if="cat === 'base'">
            <el-radio-button value="add">加法</el-radio-button>
            <el-radio-button value="sub">减法</el-radio-button>
            <el-radio-button value="mul">乘法</el-radio-button>
            <el-radio-button value="div">除法</el-radio-button>
            <el-radio-button value="mix">混合</el-radio-button>
          </template>
          <template v-else-if="cat === 'data'">
            <el-radio-button value="pct">百分比计算</el-radio-button>
            <el-radio-button value="growth">增长量/增长率</el-radio-button>
            <el-radio-button value="ratio">比重</el-radio-button>
          </template>
          <template v-else>
            <el-radio-button value="square">平方速算</el-radio-button>
            <el-radio-button value="frac">分数化百分数</el-radio-button>
            <el-radio-button value="unit">单位换算</el-radio-button>
          </template>
        </el-radio-group>
      </div>
      <div class="cfg-row">
        <span class="cfg-label">题量</span>
        <el-radio-group v-model="count">
          <el-radio-button :value="5">5 题</el-radio-button>
          <el-radio-button :value="10">10 题</el-radio-button>
          <el-radio-button :value="20">20 题</el-radio-button>
        </el-radio-group>
        <span class="cfg-hint">每题限时 {{ limit }} 秒</span>
      </div>
      <div class="cfg-row">
        <el-button type="primary" size="large" @click="begin">开始练习</el-button>
      </div>
    </div>

    <!-- 练习中 -->
    <div v-else-if="!done" class="practice">
      <div class="p-head">
        <span class="p-progress">第 {{ qi + 1 }} / {{ count }} 题</span>
        <span class="p-score">已对 {{ correct }} · 已错 {{ wrong }} </span>
        <span class="p-timer" :class="{ low: qRemain <= 5 }">{{ qRemain }}s</span>
      </div>
      <div class="p-question">{{ question.text }}</div>
      <div class="p-input-row">
        <input
          ref="ansInput"
          v-model="answer"
          class="p-input"
          type="text"
          inputmode="decimal"
          placeholder="输入答案后回车 / Tab 下一题"
          @keydown.enter="submit"
          @keydown.tab.prevent="submit"
        />
        <el-button type="primary" @click="submit">提交</el-button>
      </div>
      <div class="p-feedback" :class="fbClass">{{ feedback }}</div>
      <div class="p-tip">💡 输入答案后按 回车 或 Tab 键立即进入下一题；超时自动判错。</div>
    </div>

    <!-- 结果 -->
    <div v-else class="result">
      <h2>练习完成！</h2>
      <div class="r-stats">
        <div class="r-item"><span class="r-num">{{ correct }}</span><span class="r-label">答对</span></div>
        <div class="r-item"><span class="r-num">{{ wrong }}</span><span class="r-label">答错</span></div>
        <div class="r-item"><span class="r-num">{{ totalSec }}s</span><span class="r-label">总用时</span></div>
        <div class="r-item"><span class="r-num">{{ acc }}%</span><span class="r-label">正确率</span></div>
      </div>
      <div class="r-grade" :class="grade.cls">评分：{{ grade.grade }} —— {{ grade.tip }}</div>
      <div class="r-actions">
        <el-button type="primary" size="large" @click="begin">再来一组</el-button>
        <el-button size="large" @click="resetAll">更换题型</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onBeforeUnmount } from 'vue'
import PageHead from './PageHead.vue'

const cat = ref('base')
const sub = ref('add')
const count = ref(10)
const limit = 30 // 每题限时秒数

const started = ref(false)
const done = ref(false)
const qi = ref(0)
const correct = ref(0)
const wrong = ref(0)
const answer = ref('')
const question = ref({ text: '', ans: null })
const feedback = ref('')
const fbClass = ref('')
const qRemain = ref(limit)
const totalSec = ref(0)
const ansInput = ref(null)

let qTimer = null
let startTs = 0

// ---------- 出题 ----------
function genQ() {
  const s = sub.value
  if (cat.value === 'base') return genBase(s)
  if (cat.value === 'data') return genData(s)
  return genOther(s)
}
function ri(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}
function genBase(s) {
  const mode = s === 'mix' ? ['add', 'sub', 'mul', 'div'][ri(0, 3)] : s
  if (mode === 'add') {
    const a = ri(11, 99), b = ri(11, 99)
    return { text: `${a} + ${b} = ？`, ans: a + b }
  }
  if (mode === 'sub') {
    const a = ri(30, 99), b = ri(1, a - 1)
    return { text: `${a} - ${b} = ？`, ans: a - b }
  }
  if (mode === 'mul') {
    const a = ri(11, 99), b = ri(2, 9)
    return { text: `${a} × ${b} = ？`, ans: a * b }
  }
  const b = ri(2, 9), c = ri(2, 9)
  const a = b * c
  return { text: `${a} ÷ ${b} = ？`, ans: c }
}
function genData(s) {
  if (s === 'pct') {
    // 百分比计算：a 的 b% 是多少
    const a = ri(10, 99) * 10
    const b = [5, 10, 15, 20, 25, 30, 40, 50, 60, 75][ri(0, 9)]
    return { text: `${a} 的 ${b}% 是多少？`, ans: a * b / 100 }
  }
  if (s === 'growth') {
    // 增长量：现期 = 基期 + 基期×增速%（只算增长量）
    const base = ri(10, 99) * 100
    const rate = [5, 10, 12, 15, 20, 25][ri(0, 5)]
    return { text: `基期 ${base}，同比增长 ${rate}%，增长量为多少？`, ans: base * rate / 100 }
  }
  // 比重：占 a 的 b% 是多少（部分量）
  const a = ri(10, 99) * 10
  const b = [10, 20, 25, 30, 40, 50][ri(0, 5)]
  return { text: `总量 ${a}，其中某部分占 ${b}%，该部分是多少？`, ans: a * b / 100 }
}
function genOther(s) {
  if (s === 'square') {
    const n = ri(11, 30)
    return { text: `${n}² = ？`, ans: n * n }
  }
  if (s === 'frac') {
    // 分数化百分数：1/2..1/8
    const d = ri(2, 8)
    const pct = Math.round(1000 / d) / 10
    return { text: `1/${d} 化成百分数是？（保留 1 位小数，如 33.3）`, ans: pct }
  }
  const k = ri(1, 24)
  return { text: `${k} 小时 = ？分钟`, ans: k * 60 }
}

// ---------- 流程 ----------
function begin() {
  started.value = true
  done.value = false
  qi.value = 0
  correct.value = 0
  wrong.value = 0
  totalSec.value = 0
  startTs = Date.now()
  nextQ()
}
function nextQ() {
  if (qi.value >= count.value) {
    finish()
    return
  }
  question.value = genQ()
  answer.value = ''
  feedback.value = ''
  fbClass.value = ''
  qRemain.value = limit
  clearInterval(qTimer)
  qTimer = setInterval(() => {
    qRemain.value--
    if (qRemain.value <= 0) {
      clearInterval(qTimer)
      wrong.value++
      feedback.value = `⏰ 超时！正确答案：${question.value.ans}`
      fbClass.value = 'bad'
      qi.value++
      setTimeout(nextQ, 900)
    }
  }, 1000)
  nextTick(() => ansInput.value && ansInput.value.focus())
}
function submit() {
  clearInterval(qTimer)
  const v = parseFloat(answer.value)
  const ok = !isNaN(v) && Math.abs(v - question.value.ans) < 0.01
  if (ok) {
    correct.value++
    feedback.value = '✅ 正确！'
    fbClass.value = 'good'
  } else {
    wrong.value++
    feedback.value = `❌ 正确答案：${question.value.ans}`
    fbClass.value = 'bad'
  }
  qi.value++
  setTimeout(nextQ, 500)
}
function finish() {
  clearInterval(qTimer)
  done.value = true
  totalSec.value = Math.round((Date.now() - startTs) / 1000)
}
function resetAll() {
  started.value = false
  done.value = false
}
function fmt(s) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return (m ? m + '分' : '') + sec + '秒'
}
const acc = computed(() => (count.value ? Math.round(correct.value / count.value * 100) : 0))
const grade = computed(() => {
  const p = acc.value
  if (p >= 95) return { grade: 'S', cls: 's', tip: '心算大神，资料分析稳了！' }
  if (p >= 80) return { grade: 'A', cls: 'a', tip: '非常棒，保持每天一组。' }
  if (p >= 60) return { grade: 'B', cls: 'b', tip: '基础不错，错题多练几次。' }
  return { grade: 'C', cls: 'c', tip: '别急，从加法开始慢慢来。' }
})

onBeforeUnmount(() => clearInterval(qTimer))
</script>

<style scoped>
.config { max-width: 720px; border: 1px solid var(--el-border-color-light); border-radius: 14px; padding: 24px; }
.cfg-row { display: flex; align-items: center; gap: 16px; margin-bottom: 18px; flex-wrap: wrap; }
.cfg-label { width: 80px; font-size: 14px; font-weight: 600; color: var(--el-text-color-secondary); }
.cfg-hint { font-size: 12px; color: var(--el-text-color-secondary); }
.practice { max-width: 640px; }
.p-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.p-progress { font-size: 15px; font-weight: 700; }
.p-score { font-size: 13px; color: var(--el-text-color-secondary); }
.p-timer { font-size: 18px; font-weight: 800; color: var(--el-color-primary); font-variant-numeric: tabular-nums; }
.p-timer.low { color: #f56c6c; animation: blink 1s step-start infinite; }
@keyframes blink { 50% { opacity: .35; } }
.p-question {
  font-size: 26px;
  font-weight: 800;
  text-align: center;
  padding: 40px 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 14px;
  line-height: 1.6;
}
.p-input-row { display: flex; gap: 12px; margin-top: 20px; }
.p-input {
  flex: 1;
  height: 48px;
  font-size: 22px;
  text-align: center;
  border: 2px solid var(--el-border-color);
  border-radius: 10px;
  outline: none;
  transition: border-color .15s;
}
.p-input:focus { border-color: var(--el-color-primary); }
.p-feedback { margin-top: 14px; font-size: 16px; font-weight: 700; min-height: 24px; }
.p-feedback.good { color: #67c23a; }
.p-feedback.bad { color: #f56c6c; }
.p-tip { margin-top: 10px; font-size: 12px; color: var(--el-text-color-secondary); }
.result { text-align: center; max-width: 640px; padding: 20px 0; }
.result h2 { font-size: 24px; margin: 0 0 24px; }
.r-stats { display: flex; justify-content: center; gap: 30px; margin-bottom: 24px; }
.r-item { display: flex; flex-direction: column; gap: 6px; }
.r-num { font-size: 30px; font-weight: 800; color: var(--el-color-primary); }
.r-label { font-size: 13px; color: var(--el-text-color-secondary); }
.r-grade { display: inline-block; padding: 10px 24px; border-radius: 999px; font-size: 16px; font-weight: 700; margin-bottom: 24px; }
.r-grade.s { background: #f0f9eb; color: #67c23a; }
.r-grade.a { background: #ecf5ff; color: #409eff; }
.r-grade.b { background: #fdf6ec; color: #e6a23c; }
.r-grade.c { background: #fef0f0; color: #f56c6c; }
.r-actions { display: flex; gap: 12px; justify-content: center; }
</style>
