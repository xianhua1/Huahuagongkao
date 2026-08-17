<template>
  <div class="tab">
    <PageHead icon="notebook" title="申论规范词库" :desc="`申论小题拿分关键：把材料里的“大白话”翻译成“机关语言”。共 ${totalPairs} 组。`" />
<!-- 模式切换 -->
    <div class="mode-bar">
      <el-radio-group v-model="mode" size="small">
        <el-radio-button value="study">📖 学习模式</el-radio-button>
        <el-radio-button value="quiz">✏️ 翻译练习</el-radio-button>
      </el-radio-group>
      <el-button size="small" type="primary" plain @click="resetDone">重置进度</el-button>
    </div>

    <!-- 学习模式 -->
    <template v-if="mode === 'study'">
      <div class="theme-tabs">
        <div
          v-for="(th, ti) in guifan"
          :key="ti"
          class="theme-tab"
          :class="{ active: theme === ti }"
          @click="theme = ti"
        >
          {{ th.t }} <span class="theme-cnt">{{ themeDone(ti) }}/{{ th.items.length }}</span>
        </div>
      </div>
      <div class="gf-list">
        <div v-for="(item, i) in currentItems" :key="i" class="gf-card" :class="{ known: known.has(itemKey(ti, i)) }">
          <div class="gf-row">
            <span class="gf-label">材料大白话</span>
            <span class="gf-b">{{ item[0] }}</span>
          </div>
          <div class="gf-arrow">↓ 概括为</div>
          <div class="gf-row">
            <span class="gf-label">规范表达</span>
            <span class="gf-g">{{ item[1] }}</span>
          </div>
          <div class="gf-tip">💡 {{ item[2] }}</div>
          <el-button
            v-if="!known.has(itemKey(ti, i))"
            size="small" type="success" plain class="gf-btn"
            @click="markKnown(ti, i)"
          >✓ 已掌握</el-button>
          <span v-else class="gf-known">已掌握</span>
        </div>
      </div>
    </template>

    <!-- 翻译练习 -->
    <template v-else>
      <div v-if="!quizDone && quizQ" class="quiz-box">
        <div class="quiz-progress">第 {{ qi + 1 }} / {{ quizTotal }} 题 · 答对 {{ quizCorrect }} 题</div>
        <div class="quiz-q">
          <div class="quiz-question">材料中出现："{{ quizQ.q }}"</div>
          <div class="quiz-sub">最规范的概括表达是？</div>
          <div
            v-for="(opt, oi) in quizQ.opts"
            :key="oi"
            class="quiz-opt"
            :class="quizOptClass(oi)"
            @click="!quizRevealed && quizChoose(oi)"
          >
            {{ String.fromCharCode(65 + oi) }}. {{ opt }}
          </div>
        </div>
        <div v-if="quizRevealed" class="quiz-result" :class="quizRight ? 'right' : 'wrong'">
          <span>{{ quizRight ? '翻译到位！' : '还不够规范' }} 正确答案：{{ quizQ.ans }}</span>
          <el-button size="small" type="primary" @click="quizNext">下一题</el-button>
        </div>
      </div>
      <div v-else class="done-box">
        <h3>练习完成！答对 {{ quizCorrect }} / {{ quizTotal }}</h3>
        <p class="done-tip">写申论小题时，先写规范词、再抄材料依据，分数就是这么来的。</p>
        <el-button type="primary" size="small" @click="startQuiz">再来一组</el-button>
      </div>
      <div class="quiz-actions">
        <el-button type="primary" size="small" @click="startQuiz">开始翻译练习（10 题）</el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import useUserStore from '@/store/modules/user'
import { guifan } from './data/guifan'
import { load, save } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const mode = ref('study')
const theme = ref(0)
const known = ref(new Set())

const currentItems = computed(() => guifan[theme.value].items)
const totalPairs = computed(() => guifan.reduce((n, t) => n + t.items.length, 0))
const knownPct = computed(() => Math.round(known.value.size / totalPairs.value * 100))
const ti = computed(() => theme.value)

function itemKey(t, i) {
  return t + ':' + i
}
function themeDone(t) {
  return guifan[t].items.filter((_, i) => known.value.has(itemKey(t, i))).length
}
function markKnown(t, i) {
  known.value.add(itemKey(t, i))
  save(uid.value, 'guifanDone', [...known.value])
}
function resetDone() {
  known.value = new Set()
  save(uid.value, 'guifanDone', [])
}

// ---------- 翻译练习 ----------
const quizTotal = ref(0)
const quizItems = ref([])
const qi = ref(0)
const quizCorrect = ref(0)
const quizRevealed = ref(false)
const quizRight = ref(false)
const quizPicked = ref(-1)
const quizDone = ref(false)
const quizQ = ref(null)

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function allPairs() {
  const arr = []
  guifan.forEach((t, ti2) => t.items.forEach((it, i) => arr.push({ t: ti2, i, b: it[0], g: it[1] })))
  return arr
}

function startQuiz() {
  const pool = allPairs()
  const picked = shuffle(pool).slice(0, 10)
  quizItems.value = picked
  quizTotal.value = picked.length
  qi.value = 0
  quizCorrect.value = 0
  quizDone.value = false
  quizRevealed.value = false
  buildQ()
}

function buildQ() {
  const item = quizItems.value[qi.value]
  const others = shuffle(allPairs().filter(x => x.g !== item.g)).slice(0, 3)
  const opts = shuffle([item, ...others])
  quizQ.value = {
    q: item.b,
    opts: opts.map(x => x.g),
    ans: item.g,
    item: item
  }
  quizPicked.value = -1
  quizRevealed.value = false
  quizRight.value = false
}

function quizOptClass(oi) {
  if (!quizRevealed.value) return ''
  if (quizQ.value.opts[oi] === quizQ.value.ans) return 'ok'
  if (oi === quizPicked.value) return 'bad'
  return ''
}

function quizChoose(oi) {
  if (quizRevealed.value) return
  quizPicked.value = oi
  quizRevealed.value = true
  const right = quizQ.value.opts[oi] === quizQ.value.ans
  quizRight.value = right
  if (right) {
    quizCorrect.value++
    known.value.add(itemKey(quizQ.value.item.t, quizQ.value.item.i))
    save(uid.value, 'guifanDone', [...known.value])
  }
}

function quizNext() {
  qi.value++
  if (qi.value >= quizTotal.value) {
    quizDone.value = true
  } else {
    buildQ()
  }
}

onMounted(() => {
  known.value = new Set(load(uid.value, 'guifanDone', []))
})

// 切到翻译练习模式时自动开始
watch(mode, v => {
  if (v === 'quiz' && !quizItems.value.length) startQuiz()
})
</script>

<style scoped>
.mode-bar { display: flex; gap: 12px; align-items: center; margin: 14px 0; }
.theme-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.theme-tab {
  padding: 7px 14px; border-radius: 16px; cursor: pointer;
  font-size: 13px; color: var(--el-text-color-regular);
  background: var(--el-fill-color-light);
  transition: all .15s;
}
.theme-tab.active { background: var(--el-color-primary); color: #fff; font-weight: 600; }
.theme-cnt { font-size: 11px; opacity: .8; margin-left: 2px; }
.gf-list { display: flex; flex-direction: column; gap: 10px; max-width: 760px; }
.gf-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 12px 16px;
  position: relative;
}
.gf-card.known { opacity: .55; background: var(--el-fill-color-lighter); }
.gf-row { display: flex; align-items: flex-start; gap: 10px; line-height: 1.7; }
.gf-label {
  flex-shrink: 0; font-size: 11px; color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light); border-radius: 6px; padding: 2px 8px; margin-top: 3px;
}
.gf-b { font-size: 14px; color: var(--el-text-color-regular); }
.gf-arrow { font-size: 12px; color: var(--el-color-primary); margin: 4px 0 4px 66px; }
.gf-g { font-size: 15px; font-weight: 700; color: var(--el-color-primary); }
.gf-tip { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 6px; line-height: 1.6; }
.gf-btn { position: absolute; right: 12px; top: 12px; }
.gf-known { position: absolute; right: 16px; top: 14px; font-size: 13px; color: #67c23a; font-weight: 600; }
.quiz-box { max-width: 720px; }
.quiz-progress { font-size: 13px; color: var(--el-text-color-secondary); margin-bottom: 10px; }
.quiz-q { border: 1px solid var(--el-border-color-light); border-radius: 12px; padding: 18px; }
.quiz-question { font-size: 15px; font-weight: 600; line-height: 1.7; }
.quiz-sub { font-size: 13px; color: var(--el-text-color-secondary); margin: 6px 0 14px; }
.quiz-opt {
  border: 1px solid var(--el-border-color); border-radius: 8px;
  padding: 10px 14px; margin-bottom: 8px; cursor: pointer;
  font-size: 14px; transition: all .15s;
}
.quiz-opt:hover { border-color: var(--el-color-primary); }
.quiz-opt.ok { border-color: #67c23a; background: #f0f9eb; }
.quiz-opt.bad { border-color: #f56c6c; background: #fef0f0; }
.quiz-result { margin-top: 12px; padding: 10px 14px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 600; }
.quiz-result.right { background: #f0f9eb; color: #67c23a; }
.quiz-result.wrong { background: #fef0f0; color: #f56c6c; }
.quiz-actions { margin-top: 14px; }
.done-box { text-align: center; padding: 40px 0; }
.done-box h3 { font-size: 20px; margin: 0 0 8px; }
.done-tip { font-size: 13px; color: var(--el-text-color-secondary); margin: 0 0 16px; }
</style>
