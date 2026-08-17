<template>
  <div class="tab">
    <PageHead icon="trend" title="行测助手 · 口算练习" desc="照搬备考神器同款题型：基础练习 12 种口算、资料专项 7 种速算、舒尔特方格与数字谜题。电脑上输入答案后按 Tab / 回车对焦下一题，做完点「提交」看成绩。" />

    <!-- 配置 -->
    <div v-if="!started" class="config">
      <div class="cat-tabs">
        <div
          v-for="c in cats" :key="c.key"
          class="cat-tab" :class="{ active: cat === c.key }"
          @click="cat = c.key"
        >{{ c.label }}</div>
      </div>
      <div class="cfg-row">
        <span class="cfg-label">题型</span>
        <div class="type-grid">
          <div
            v-for="t in types" :key="t.key"
            class="type-item" :class="{ active: sub === t.key }"
            @click="sub = t.key"
          >{{ t.label }}</div>
        </div>
      </div>
      <div v-if="cat !== 'other'" class="cfg-row">
        <span class="cfg-label">题量</span>
        <el-radio-group v-model="count">
          <el-radio-button :value="5">5 题</el-radio-button>
          <el-radio-button :value="10">10 题</el-radio-button>
          <el-radio-button :value="20">20 题</el-radio-button>
        </el-radio-group>
        <span class="cfg-hint">每题限时 {{ limit }} 秒</span>
      </div>
      <div class="cfg-row">
        <el-button type="primary" size="large" @click="begin">{{ cat === 'other' ? '开始练习' : '开始练习' }}</el-button>
      </div>
      <p class="cfg-tip">💡 {{ cat === 'other' ? (sub === 'schulte' ? '舒尔特方格：按顺序从 1 点击到 25，越快说明专注力越强。' : '数字谜题：猜一个 4 位不重复数字，A=数字和位置都对，B=数字对但位置不对。') : '输入答案后按 回车 或 Tab 键对焦下一题；全部填完点「提交」评分。' }}</p>
    </div>

    <!-- 练习中：答题卡 -->
    <div v-else-if="!done && cat !== 'other'" class="practice">
      <div class="p-head">
        <span class="p-progress">第 {{ qi + 1 }} / {{ count }} 题 · {{ subName }}</span>
        <span class="p-score">已填 {{ filledCount }} 题</span>
        <span class="p-timer" :class="{ low: qRemain <= 5 }">{{ qRemain }}s</span>
      </div>

      <!-- 普通输入题 -->
      <template v-if="qtype === 'input'">
        <div class="p-question" v-html="question.html"></div>
        <div class="p-input-row">
          <input
            ref="ansInput"
            v-model="answer"
            class="p-input"
            type="text"
            inputmode="decimal"
            :placeholder="qtype === 'input' ? '输入答案后回车 / Tab 下一题' : ''"
            @keydown.enter="submit"
            @keydown.tab.prevent="submit"
          />
        </div>
        <div class="p-feedback" :class="fbClass">{{ feedback }}</div>
      </template>

      <!-- 比较题 > = < -->
      <template v-else-if="qtype === 'compare'">
        <div class="compare-box">
          <div class="cmp-row">
            <span class="cmp-num">{{ question.a }}</span>
            <span class="cmp-op">?</span>
            <span class="cmp-num">{{ question.b }}</span>
          </div>
          <div class="cmp-btns">
            <button v-for="op in ['>', '=', '<']" :key="op" class="cmp-btn" :class="{ picked: answer === op }" @click="pickOp(op)">{{ op }}</button>
          </div>
        </div>
        <div class="p-feedback" :class="fbClass">{{ feedback }}</div>
      </template>

      <!-- 图表题 -->
      <template v-else-if="qtype === 'chart'">
        <div class="chart-box">
          <div class="chart-title">{{ question.chartTitle }}</div>
          <div class="chart-canvas">
            <svg :viewBox="'0 0 ' + chartW + ' ' + chartH" class="chart-svg">
              <line v-for="i in chartLines" :key="'h' + i" :x1="padL" :y1="padT + i * rowH" :x2="chartW - padR" :y2="padT + i * rowH" class="grid-line" />
              <text v-for="(lb, i) in chartLabels" :key="'y' + i" :x="padL - 8" :y="padT + i * rowH + 4" class="axis-label" text-anchor="end">{{ lb }}</text>
              <g v-for="(g, gi) in chartGroups" :key="gi">
                <g v-for="(v, vi) in g.vals" :key="vi">
                  <rect
                    :x="barX(vi, gi)" :y="yOf(v)" :width="barW" :height="chartH - padB - yOf(v)"
                    :fill="g.colors[vi % g.colors.length]" rx="3"
                  />
                  <text v-if="g.showVal" :x="barX(vi, gi) + barW / 2" :y="yOf(v) - 5" class="val-label" text-anchor="middle">{{ v }}</text>
                </g>
              </g>
              <text v-for="(x, xi) in question.xLabels" :key="'x' + xi" :x="xLabelX(xi)" :y="chartH - padB + 20" class="axis-label" text-anchor="middle">{{ x }}</text>
              <g v-for="(lg, li) in question.legend" :key="'lg' + li" :transform="`translate(${chartW - padR - 150 + li * 95}, ${padT - 24})`">
                <rect x="0" y="-9" width="14" height="14" :fill="lg.color" rx="2" />
                <text x="18" y="2" class="legend-label">{{ lg.name }}</text>
              </g>
            </svg>
          </div>
          <div class="chart-sub">{{ question.chartNote }}</div>
          <div class="chart-question">{{ question.text }}</div>
          <div class="p-input-row chart-input">
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
          </div>
          <div class="p-feedback" :class="fbClass">{{ feedback }}</div>
        </div>
      </template>

      <!-- 答题卡进度 -->
      <div v-if="count > 5" class="answer-grid">
        <div
          v-for="(_, i) in count" :key="i"
          class="ans-cell"
          :class="{ cur: i === qi, filled: answers[i] !== '' }"
          @click="qi = i; focusInput()"
        >{{ i + 1 }}</div>
      </div>
      <div class="p-actions">
        <el-button type="primary" @click="submitAll">提交评分</el-button>
        <el-button @click="resetAll">退出</el-button>
      </div>
    </div>

    <!-- 舒尔特方格 -->
    <div v-else-if="started && !done && cat === 'other' && sub === 'schulte'" class="schulte-box">
      <div class="s-head">
        <span class="s-title">舒尔特方格</span>
        <span class="s-timer">{{ sTime.toFixed(1) }}s</span>
        <el-button size="small" @click="resetAll">退出</el-button>
      </div>
      <div class="s-grid">
        <button
          v-for="(n, i) in schulteGrid" :key="i"
          class="s-cell" :class="{ found: n < schulteNext }"
          @click="schulteClick(n)"
        >{{ n }}</button>
      </div>
      <div class="s-tip">按顺序从 1 点击到 25：下一个要找 {{ schulteNext }}</div>
    </div>

    <!-- 数字谜题 -->
    <div v-else-if="started && !done && cat === 'other' && sub === 'mystery'" class="mystery-box">
      <div class="m-head">
        <span class="s-title">数字谜题</span>
        <span class="m-guess">{{ guesses }} 次</span>
        <el-button size="small" @click="resetAll">退出</el-button>
      </div>
      <div class="m-rule">猜一个 4 位不重复数字（0-9）。每次输入后返回：A=数字和位置都对，B=数字对但位置不对。例：答案是 1234，输入 2134 返回 2A2B。</div>
      <div class="m-input-row">
        <input
          ref="ansInput"
          v-model="answer"
          class="p-input m-input"
          type="text"
          maxlength="4"
          placeholder="输入 4 位数字"
          @keydown.enter="submitMystery"
        />
        <el-button type="primary" @click="submitMystery">猜</el-button>
      </div>
      <div class="m-history">
        <div v-for="(h, i) in mHistory" :key="i" class="m-row" :class="{ win: h.win }">
          <span class="m-num">{{ h.guess }}</span>
          <span class="m-result">{{ h.result }}</span>
        </div>
      </div>
    </div>

    <!-- 结果 -->
    <div v-else class="result">
      <h2>{{ cat === 'other' ? (sub === 'schulte' ? '练习完成！' : '恭喜猜中！') : '练习完成！' }}</h2>
      <div class="r-stats">
        <div class="r-item"><span class="r-num">{{ correct }}</span><span class="r-label">正确</span></div>
        <div class="r-item"><span class="r-num">{{ wrong }}</span><span class="r-label">错误</span></div>
        <div class="r-item"><span class="r-num">{{ unanswered }}</span><span class="r-label">未答</span></div>
        <div class="r-item"><span class="r-num">{{ totalSec }}s</span><span class="r-label">耗时</span></div>
        <div class="r-item"><span class="r-num">{{ acc }}%</span><span class="r-label">准确率</span></div>
      </div>
      <div v-if="cat === 'other'" class="r-grade" :class="otherGrade.cls">成绩：{{ otherGrade.grade }} —— {{ otherGrade.tip }}</div>
      <div v-else class="r-grade" :class="grade.cls">成绩：{{ grade.grade }} —— {{ grade.tip }}</div>
      <div class="r-actions">
        <el-button type="primary" size="large" @click="begin">再来一组</el-button>
        <el-button size="large" @click="resetAll">更换题型</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onBeforeUnmount, watch } from 'vue'
import PageHead from './PageHead.vue'

const limit = 45 // 每题限时秒数

const cats = [
  { key: 'base', label: '基础练习' },
  { key: 'data', label: '资料专项' },
  { key: 'other', label: '其他训练' }
]

// ------- 题型定义（与 saduck 一致）-------
const TYPES = {
  base: [
    { key: 'add2', label: '两位数加法' },
    { key: 'sub2', label: '两位数减法' },
    { key: 'add3', label: '三位数加法' },
    { key: 'sub3', label: '三位数减法' },
    { key: 'mul2x1', label: '两位乘一位' },
    { key: 'mul2x2', label: '两位乘两位' },
    { key: 'mul3x1', label: '三位乘一位' },
    { key: 'div3x1', label: '三位除一位' },
    { key: 'div3x2', label: '三位除两位' },
    { key: 'div5x3', label: '五位除三位' },
    { key: 'sumN', label: '多个数相加' },
    { key: 'square', label: '常见平方数' }
  ],
  data: [
    { key: 'baseEst', label: '估算基期' },
    { key: 'growthEst', label: '估算增长量' },
    { key: 'pctFrac', label: '百化分计算' },
    { key: 'fracCmp', label: '分数比较' },
    { key: 'baseCmp', label: '基期比较' },
    { key: 'avgYear', label: '年平均量' },
    { key: 'growthRate', label: '年均增长率' }
  ],
  other: [
    { key: 'schulte', label: '舒尔特方格' },
    { key: 'mystery', label: '数字谜题' }
  ]
}

const cat = ref('base')
const sub = ref('add2')
const count = ref(10)

const types = computed(() => TYPES[cat.value] || [])
const subName = computed(() => {
  const t = types.value.find(x => x.key === sub.value)
  return t ? t.label : ''
})

watch(cat, c => {
  sub.value = TYPES[c][0].key
})

// ------- 状态 -------
const started = ref(false)
const done = ref(false)
const qi = ref(0)
const correct = ref(0)
const wrong = ref(0)
const unanswered = ref(0)
const answers = ref([])
const questions = ref([])
const answer = ref('')
const feedback = ref('')
const fbClass = ref('')
const qRemain = ref(limit)
const totalSec = ref(0)
const ansInput = ref(null)

let qTimer = null
let startTs = 0

const qtype = computed(() => {
  if (!questions.value[qi.value]) return 'input'
  return questions.value[qi.value].type || 'input'
})
const question = computed(() => questions.value[qi.value] || {})
const filledCount = computed(() => answers.value.filter(a => a !== '').length)

// ------- 出题 -------
function ri(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}
function escHtml(s) {
  return String(s)
}

function genBase(s) {
  if (s === 'add2') {
    const a = ri(11, 99), b = ri(11, 99)
    return { type: 'input', html: `${a}＋${b} =`, ans: a + b }
  }
  if (s === 'sub2') {
    const a = ri(21, 99), b = ri(11, a - 1)
    return { type: 'input', html: `${a} - ${b} =`, ans: a - b }
  }
  if (s === 'add3') {
    const a = ri(101, 999), b = ri(101, 999)
    return { type: 'input', html: `${a}＋${b} =`, ans: a + b }
  }
  if (s === 'sub3') {
    const a = ri(301, 999), b = ri(101, a - 1)
    return { type: 'input', html: `${a} - ${b} =`, ans: a - b }
  }
  if (s === 'mul2x1') {
    const a = ri(11, 99), b = ri(2, 9)
    return { type: 'input', html: `${a} × ${b} =`, ans: a * b }
  }
  if (s === 'mul2x2') {
    const a = ri(11, 99), b = ri(11, 99)
    return { type: 'input', html: `${a} × ${b} =`, ans: a * b }
  }
  if (s === 'mul3x1') {
    const a = ri(101, 999), b = ri(2, 9)
    return { type: 'input', html: `${a} × ${b} =`, ans: a * b }
  }
  if (s === 'div3x1') {
    const b = ri(2, 9), c = ri(12, 99)
    return { type: 'input', html: `${b * c} ÷ ${b} =`, ans: c }
  }
  if (s === 'div3x2') {
    // 三位除两位：构造整除
    const b = ri(12, 98), c = ri(3, 19)
    return { type: 'input', html: `${b * c} ÷ ${b} =`, ans: c }
  }
  if (s === 'div5x3') {
    // 五位除三位：构造整除，商三位
    const b = ri(102, 987), c = ri(102, 987)
    return { type: 'input', html: `${b * c} ÷ ${b} =`, ans: c }
  }
  if (s === 'sumN') {
    const n = ri(3, 5)
    const nums = []
    for (let i = 0; i < n; i++) nums.push(ri(10, 99))
    return { type: 'input', html: nums.join('＋') + ' =', ans: nums.reduce((x, y) => x + y, 0) }
  }
  if (s === 'square') {
    const n = ri(11, 29)
    return { type: 'input', html: `${n} × ${n} =`, ans: n * n }
  }
}

function genData(s) {
  if (s === 'baseEst') {
    // 基期 = 现期 / (1 + 增长率)，保留整数
    const now = ri(2000, 9999)
    const rate = ri(-45, 60) / 1
    const ans = Math.round(now / (1 + rate / 100))
    return { type: 'input', html: `现期${now}，增长率 ${rate > 0 ? '+' : ''}${rate.toFixed(2)}%，基期 =`, ans }
  }
  if (s === 'growthEst') {
    // 增长量 = 现期 × 增长率 / (1 + 增长率)，保留整数（负增长为负值）
    const now = ri(2000, 9999)
    const rate = ri(-60, 70) / 1
    const g = now * rate / 100 / (1 + rate / 100)
    const ans = Math.round(g)
    return { type: 'input', html: `现期${now}，增长率${rate >= 0 ? '+' : ''}${rate.toFixed(2)}%，增长量 =`, ans }
  }
  if (s === 'pctFrac') {
    const d = ri(2, 20)
    const ans = Math.round(10000 / d) / 100
    return { type: 'input', html: `1 / ${d} =`, ans }
  }
  if (s === 'fracCmp') {
    const a = { n: ri(100, 999), d: ri(100, 999) }
    const b = { n: ri(100, 999), d: ri(100, 999) }
    const v = a.n / a.d - b.n / b.d
    return { type: 'compare', a: `${a.n}/${a.d}`, b: `${b.n}/${b.d}`, ans: v > 0 ? '>' : v < 0 ? '<' : '=' }
  }
  if (s === 'baseCmp') {
    // 基期比较：现期/（1+增长率）
    const a = { now: ri(300, 999), r: (ri(-60, 80) / 100).toFixed(3) }
    const b = { now: ri(300, 999), r: (ri(-60, 80) / 100).toFixed(3) }
    const va = a.now / (1 + parseFloat(a.r))
    const vb = b.now / (1 + parseFloat(b.r))
    return {
      type: 'compare',
      a: `${a.now}/${a.r}`,
      b: `${b.now}/${b.r}`,
      ans: va > vb ? '>' : va < vb ? '<' : '='
    }
  }
  if (s === 'avgYear') {
    // 年平均量：5 年柱状图（虚拟数据），求平均
    const years = ['2021', '2022', '2023', '2024', '2025']
    const ex = years.map(() => ri(1200, 2000))
    const im = years.map(() => ri(500, 1000))
    const which = Math.random() < 0.5 ? 'ex' : 'im'
    const avg = Math.round((which === 'ex' ? ex : im).reduce((x, y) => x + y, 0) / 5)
    return {
      type: 'chart',
      chartTitle: '2021~2025年小鸭出口额及进口额',
      chartNote: '注：虚拟数据，请勿当真',
      xLabels: years,
      groups: [
        { vals: ex, w: 34, gap: 12, colors: ['#409eff'], showVal: true },
        { vals: im, w: 34, gap: 12, colors: ['#e6a23c'], showVal: true }
      ],
      legend: [{ name: '出口额', color: '#409eff' }, { name: '进口额', color: '#e6a23c' }],
      text: `问题：求2021~2025小鸭的年平均${which === 'ex' ? '出口' : '进口'}额 万元。`,
      ans: avg
    }
  }
  if (s === 'growthRate') {
    // 年均增长率：6 年柱状图，(末/首)^(1/5)-1 取百分数一位小数
    const years = ['2021', '2022', '2023', '2024', '2025', '2026']
    const first = ri(500, 800)
    const vals = [first]
    for (let i = 1; i < 6; i++) vals.push(Math.round(vals[i - 1] * ri(108, 122) / 100))
    const r = Math.pow(vals[5] / vals[0], 1 / 5) - 1
    const ans = Math.round(r * 1000) / 10
    return {
      type: 'chart',
      chartTitle: '2021~2026年我国电影票房',
      chartNote: '注：虚拟数据，请勿当真',
      xLabels: years,
      groups: [{ vals, w: 36, gap: 16, colors: ['#409eff'], showVal: true }],
      legend: [{ name: '票房（亿元）', color: '#409eff' }],
      text: `求：2021~2026我国电影票房的年均增长率为 %（不往前推）。`,
      ans
    }
  }
}

function genQ() {
  if (cat.value === 'base') return genBase(sub.value)
  if (cat.value === 'data') return genData(sub.value)
}

// ------- 图表渲染参数 -------
const padL = 46, padR = 20, padT = 30, padB = 40
const chartW = 560, chartH = 300
const chartLabels = ['2000', '1500', '1000', '500', '0']
const rowH = (chartH - padT - padB) / 4
const chartLines = [0, 1, 2, 3, 4]
const chartGroups = computed(() => question.value.groups || [])
const xStep = computed(() => (chartW - padL - padR) / Math.max(question.value.xLabels ? question.value.xLabels.length : 6, 1))
const barW = computed(() => {
  const n = Math.max(question.value.xLabels ? question.value.xLabels.length : 6, 1)
  const groups = chartGroups.value.length || 1
  return Math.min(26, (xStep.value * 0.62) / groups)
})
function barX(vi, gi) {
  const groups = chartGroups.value.length || 1
  const total = barW.value * groups
  const start = padL + vi * xStep.value + (xStep.value - total) / 2
  return start + gi * barW.value
}
function xLabelX(xi) {
  return padL + xi * xStep.value + xStep.value / 2
}

function maxVal(groups) {
  let m = 0
  groups.forEach(g => g.vals.forEach(v => { if (v > m) m = v }))
  return m
}
function yOf(v) {
  const m = maxVal(question.value.groups || [])
  const h = m > 0 ? (v / m) * (chartH - padT - padB) : 0
  return chartH - padB - h
}

// ------- 流程 -------
function begin() {
  if (cat.value === 'other') {
    started.value = true
    done.value = false
    if (sub.value === 'schulte') {
      const nums = shuffle([...Array(25).keys()].map(i => i + 1))
      schulteGrid.value = nums
      schulteNext.value = 1
      sTime.value = 0
      clearInterval(qTimer)
      qTimer = setInterval(() => { sTime.value += 0.1 }, 100)
    } else {
      startMystery()
    }
    return
  }
  started.value = true
  done.value = false
  qi.value = 0
  correct.value = 0
  wrong.value = 0
  unanswered.value = 0
  answers.value = Array(count.value).fill('')
  questions.value = []
  for (let i = 0; i < count.value; i++) questions.value.push(genQ())
  totalSec.value = 0
  startTs = Date.now()
  nextQ()
}

function nextQ() {
  if (qi.value >= count.value) {
    finish()
    return
  }
  answer.value = ''
  feedback.value = ''
  fbClass.value = ''
  qRemain.value = limit
  clearInterval(qTimer)
  if (question.value.type !== 'compare') {
    qTimer = setInterval(() => {
      qRemain.value--
      if (qRemain.value <= 0) {
        clearInterval(qTimer)
        if (answers.value[qi.value] === '') {
          answers.value[qi.value] = '__'
        }
        feedback.value = `⏰ 超时！正确答案：${question.value.ans}`
        fbClass.value = 'bad'
        qi.value++
        nextQ()
      }
    }, 1000)
  }
  nextTick(() => ansInput.value && ansInput.value.focus())
}

function submit() {
  if (question.value.type === 'compare') return
  clearInterval(qTimer)
  const v = parseFloat(answer.value)
  const ok = !isNaN(v) && Math.abs(v - question.value.ans) < 0.06
  if (answers.value[qi.value] === '') {
    if (ok) correct.value++
    else wrong.value++
    answers.value[qi.value] = ok ? 'ok' : 'bad'
  }
  feedback.value = ok ? '✅ 正确！' : `❌ 正确答案：${question.value.ans}`
  fbClass.value = ok ? 'good' : 'bad'
  qi.value++
  nextQ()
}

function pickOp(op) {
  if (answers.value[qi.value] !== '') return
  answer.value = op
  const ok = op === question.value.ans
  if (ok) correct.value++
  else wrong.value++
  answers.value[qi.value] = ok ? 'ok' : 'bad'
  feedback.value = ok ? '✅ 正确！' : `❌ 正确答案：${question.value.ans}`
  fbClass.value = ok ? 'good' : 'bad'
  setTimeout(() => {
    qi.value++
    nextQ()
  }, 400)
}

function submitAll() {
  finish()
}

function finish() {
  clearInterval(qTimer)
  done.value = true
  totalSec.value = Math.round((Date.now() - startTs) / 1000)
  // 未答统计：未提交（''）或超时（'__'）的题
  let u = 0
  answers.value.forEach(a => { if (a === '' || a === '__') u++ })
  unanswered.value = u
}

// ------- 舒尔特方格 -------
const schulteGrid = ref([])
const schulteNext = ref(1)
const sTime = ref(0)

function schulteClick(n) {
  if (n !== schulteNext.value) return
  schulteNext.value++
  if (schulteNext.value > 25) {
    clearInterval(qTimer)
    done.value = true
    totalSec.value = Math.round(sTime.value)
    correct.value = 25
  }
}

// ------- 数字谜题 -------
const mSecret = ref('')
const mHistory = ref([])
const guesses = computed(() => mHistory.value.length)

function startMystery() {
  const digits = shuffle([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).slice(0, 4)
  mSecret.value = digits.join('')
  mHistory.value = []
  answer.value = ''
  started.value = true
  done.value = false
  nextTick(() => ansInput.value && ansInput.value.focus())
}
function submitMystery() {
  const g = answer.value.trim()
  if (!/^\d{4}$/.test(g)) {
    ElMessage.warning('请输入 4 位数字')
    return
  }
  if (new Set(g).size !== 4) {
    ElMessage.warning('4 位数字不能重复')
    return
  }
  let a = 0, b = 0
  for (let i = 0; i < 4; i++) {
    if (g[i] === mSecret.value[i]) a++
    else if (mSecret.value.includes(g[i])) b++
  }
  const win = a === 4
  mHistory.value.unshift({ guess: g, result: `${a}A${b}B`, win })
  answer.value = ''
  if (win) {
    done.value = true
    correct.value = 25 - Math.min(mHistory.value.length, 24) // 猜得越少分越高
    totalSec.value = mHistory.value.length
  }
}
const otherGrade = computed(() => {
  if (sub.value === 'schulte') {
    if (totalSec.value <= 20) return { grade: 'S', cls: 's', tip: '顶尖专注力！' }
    if (totalSec.value <= 30) return { grade: 'A', cls: 'a', tip: '专注力优秀。' }
    if (totalSec.value <= 45) return { grade: 'B', cls: 'b', tip: '专注力良好。' }
    return { grade: 'C', cls: 'c', tip: '多练习，专注力可以练出来。' }
  }
  if (guesses.value <= 6) return { grade: 'S', cls: 's', tip: `${guesses.value} 次猜中，推理大师！` }
  if (guesses.value <= 9) return { grade: 'A', cls: 'a', tip: `${guesses.value} 次猜中，很不错。` }
  if (guesses.value <= 13) return { grade: 'B', cls: 'b', tip: `${guesses.value} 次猜中，还可以。` }
  return { grade: 'C', cls: 'c', tip: `${guesses.value} 次猜中，试试先固定数字再排位置。` }
})

// ------- 评分 -------
const acc = computed(() => {
  if (cat.value === 'other') return 100
  const total = count.value
  return total ? Math.round(correct.value / total * 100) : 0
})
const grade = computed(() => {
  const p = acc.value
  if (p >= 95) return { grade: 'S', cls: 's', tip: '心算大神，资料分析稳了！' }
  if (p >= 80) return { grade: 'A', cls: 'a', tip: '非常棒，保持每天一组。' }
  if (p >= 60) return { grade: '及格', cls: 'b', tip: '基础不错，错题多练几次。' }
  return { grade: '不及格', cls: 'c', tip: '别急，从简单题型开始慢慢来。' }
})

function focusInput() {
  nextTick(() => ansInput.value && ansInput.value.focus())
}

function resetAll() {
  started.value = false
  done.value = false
  clearInterval(qTimer)
}
function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

onBeforeUnmount(() => clearInterval(qTimer))
</script>

<style scoped>
.config { max-width: 760px; }
.cat-tabs { display: flex; gap: 10px; margin-bottom: 16px; }
.cat-tab {
  padding: 8px 22px;
  border-radius: 999px;
  border: 1px solid var(--el-border-color);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-regular);
  transition: all .15s;
}
.cat-tab:hover { border-color: var(--el-color-primary); color: var(--el-color-primary); }
.cat-tab.active { background: var(--el-color-primary); border-color: var(--el-color-primary); color: #fff; }
.cfg-row { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; flex-wrap: wrap; }
.cfg-label { width: 48px; font-size: 14px; font-weight: 600; color: var(--el-text-color-secondary); padding-top: 7px; }
.type-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.type-item {
  padding: 6px 16px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all .15s;
}
.type-item:hover { border-color: var(--el-color-primary); color: var(--el-color-primary); }
.type-item.active { background: var(--el-color-primary-light-9); border-color: var(--el-color-primary); color: var(--el-color-primary); font-weight: 600; }
.cfg-hint { font-size: 12px; color: var(--el-text-color-secondary); align-self: center; }
.cfg-tip { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 8px; line-height: 1.7; }

.practice { max-width: 680px; }
.p-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; gap: 10px; flex-wrap: wrap; }
.p-progress { font-size: 15px; font-weight: 700; }
.p-score { font-size: 13px; color: var(--el-text-color-secondary); }
.p-timer { font-size: 18px; font-weight: 800; color: var(--el-color-primary); font-variant-numeric: tabular-nums; }
.p-timer.low { color: #f56c6c; animation: blink 1s step-start infinite; }
@keyframes blink { 50% { opacity: .35; } }
.p-question {
  font-size: 25px;
  font-weight: 800;
  text-align: center;
  padding: 36px 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 14px;
  line-height: 1.6;
  font-variant-numeric: tabular-nums;
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
.p-actions { margin-top: 18px; display: flex; gap: 10px; }
.answer-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }
.ans-cell {
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  color: var(--el-text-color-secondary);
}
.ans-cell.cur { border-color: var(--el-color-primary); color: var(--el-color-primary); font-weight: 700; background: var(--el-color-primary-light-9); }
.ans-cell.filled { background: #f0f9eb; border-color: #67c23a; color: #67c23a; }

/* 比较题 */
.compare-box { text-align: center; padding: 20px 0; }
.cmp-row { display: flex; justify-content: center; align-items: center; gap: 22px; }
.cmp-num { font-size: 27px; font-weight: 800; font-variant-numeric: tabular-nums; }
.cmp-op { font-size: 24px; font-weight: 800; color: var(--el-color-primary); }
.cmp-btns { display: flex; gap: 18px; justify-content: center; margin-top: 22px; }
.cmp-btn {
  width: 64px; height: 64px;
  font-size: 26px; font-weight: 800;
  border: 2px solid var(--el-border-color);
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  color: var(--el-text-color-primary);
  transition: all .15s;
}
.dark .cmp-btn { background: transparent; }
.cmp-btn:hover { border-color: var(--el-color-primary); color: var(--el-color-primary); }
.cmp-btn.picked { border-color: var(--el-color-primary); background: var(--el-color-primary); color: #fff; }

/* 图表题 */
.chart-box { border: 1px solid var(--el-border-color-light); border-radius: 14px; padding: 18px; }
.chart-title { font-size: 16px; font-weight: 700; text-align: center; margin-bottom: 10px; }
.chart-canvas { overflow-x: auto; }
.chart-svg { width: 100%; max-width: 560px; height: auto; display: block; margin: 0 auto; }
.grid-line { stroke: var(--el-border-color-lighter); stroke-width: 1; }
.axis-label { font-size: 11px; fill: var(--el-text-color-secondary); }
.val-label { font-size: 10px; fill: var(--el-text-color-regular); font-weight: 600; }
.legend-label { font-size: 11px; fill: var(--el-text-color-regular); }
.chart-sub { font-size: 11px; color: var(--el-text-color-secondary); text-align: center; margin: 6px 0 10px; }
.chart-question { font-size: 15px; font-weight: 600; line-height: 1.7; text-align: center; }
.chart-input { margin-top: 14px; }

/* 舒尔特方格 */
.schulte-box { max-width: 480px; }
.s-head, .m-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.s-title { font-size: 18px; font-weight: 800; }
.s-timer { font-size: 20px; font-weight: 800; color: var(--el-color-primary); font-variant-numeric: tabular-nums; }
.s-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.s-cell {
  aspect-ratio: 1;
  font-size: 22px;
  font-weight: 700;
  border: 2px solid var(--el-border-color);
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  color: var(--el-text-color-primary);
  transition: all .15s;
}
.dark .s-cell { background: transparent; }
.s-cell:hover { border-color: var(--el-color-primary); color: var(--el-color-primary); }
.s-cell.found { background: var(--el-color-primary-light-9); border-color: var(--el-color-primary); color: var(--el-color-primary); }
.s-tip { margin-top: 14px; font-size: 13px; color: var(--el-text-color-secondary); text-align: center; }

/* 数字谜题 */
.mystery-box { max-width: 520px; }
.m-guess { font-size: 15px; font-weight: 700; color: var(--el-color-primary); }
.m-rule {
  font-size: 13px; color: var(--el-text-color-secondary);
  border: 1px dashed var(--el-border-color);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 16px;
  line-height: 1.8;
}
.m-input-row { display: flex; gap: 12px; }
.m-input { letter-spacing: 8px; font-weight: 800; }
.m-history { margin-top: 16px; }
.m-row {
  display: flex; justify-content: space-between;
  padding: 8px 14px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  margin-bottom: 6px;
  font-size: 15px;
  font-variant-numeric: tabular-nums;
}
.m-row.win { background: #f0f9eb; border-color: #67c23a; }
.m-num { font-weight: 700; letter-spacing: 3px; }
.m-result { font-weight: 800; color: var(--el-color-primary); }
.m-row.win .m-result { color: #67c23a; }

/* 结果 */
.result { text-align: center; max-width: 640px; padding: 20px 0; }
.result h2 { font-size: 24px; margin: 0 0 24px; }
.r-stats { display: flex; justify-content: center; gap: 26px; margin-bottom: 24px; flex-wrap: wrap; }
.r-item { display: flex; flex-direction: column; gap: 6px; }
.r-num { font-size: 28px; font-weight: 800; color: var(--el-color-primary); }
.r-label { font-size: 13px; color: var(--el-text-color-secondary); }
.r-grade { display: inline-block; padding: 10px 24px; border-radius: 999px; font-size: 16px; font-weight: 700; margin-bottom: 24px; }
.r-grade.s { background: #f0f9eb; color: #67c23a; }
.r-grade.a { background: #ecf5ff; color: #409eff; }
.r-grade.b { background: #fdf6ec; color: #e6a23c; }
.r-grade.c { background: #fef0f0; color: #f56c6c; }
.r-actions { display: flex; gap: 12px; justify-content: center; }
</style>
