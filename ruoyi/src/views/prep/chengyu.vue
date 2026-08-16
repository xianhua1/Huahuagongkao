<template>
  <div class="tab">
    <PageHead icon="reading" title="高频成语积累" desc="共 {{ chengyu.length }} 个高频/易错/辨析成语，每天学 10 个，打卡式积累。" />
<!-- 模式切换 -->
    <div class="mode-bar">
      <el-radio-group v-model="mode" size="small">
        <el-radio-button value="study">📖 学习模式</el-radio-button>
        <el-radio-button value="quiz">✏️ 测验模式</el-radio-button>
      </el-radio-group>
      <el-select v-model="filter" size="small" style="width: 130px">
        <el-option label="全部" value="all" />
        <el-option label="高频必考" value="gao" />
        <el-option label="易错（字面≠实际）" value="yicuo" />
        <el-option label="易混辨析" value="bianxi" />
      </el-select>
      <el-button size="small" type="primary" plain @click="resetDone">重置进度</el-button>
    </div>

    <!-- 学习模式 -->
    <template v-if="mode === 'study'">
      <div v-if="batch.length" class="batch-head">
        <span>今日学习（{{ batch.length }} 个）</span>
        <el-button size="small" type="primary" @click="markAll">全部标记掌握</el-button>
      </div>
      <div v-for="(item, i) in batch" :key="i" class="cy-card" :class="{ known: known.has(itemKey(item)) }">
        <div class="cy-main">
          <span class="cy-word">{{ item[0] }}</span>
          <span class="cy-py">{{ item[1] }}</span>
          <el-tag size="small" :type="tagType(item[4])" class="cy-tag">{{ tagText(item[4]) }}</el-tag>
        </div>
        <div class="cy-meaning">{{ item[2] }}</div>
        <div class="cy-example">例句：{{ item[3] }}</div>
        <el-button
          v-if="!known.has(itemKey(item))"
          size="small" type="success" plain class="cy-btn"
          @click="markKnown(item)"
        >✓ 已掌握</el-button>
        <span v-else class="cy-known">已掌握</span>
      </div>
      <div v-if="!batch.length" class="empty-tip">
        <p>🎉 本分类的成语都学完啦！换个分类，或者做一组测验巩固一下。</p>
      </div>
    </template>

    <!-- 测验模式 -->
    <template v-else>
      <div v-if="!quizDone && quizQ" class="quiz-box">
        <div class="quiz-progress">第 {{ qi + 1 }} / {{ quizTotal }} 题 · 答对 {{ quizCorrect }} 题</div>
        <div class="quiz-q">
          <div class="quiz-question">{{ quizQ.q }}</div>
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
          <span>{{ quizRight ? '答对啦！' : '答错了' }} 正确答案：{{ quizQ.ans }}</span>
          <el-button size="small" type="primary" @click="quizNext">下一题</el-button>
        </div>
      </div>
      <div v-else class="done-box">
        <h3>测验完成！答对 {{ quizCorrect }} / {{ quizTotal }}</h3>
        <p class="done-tip">错过的成语建议回到学习模式重点标记。</p>
        <el-button type="primary" size="small" @click="startQuiz">再来一组</el-button>
      </div>
      <div class="quiz-actions">
        <el-button type="primary" size="small" @click="startQuiz">开始/重新测验（10 题）</el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import useUserStore from '@/store/modules/user'
import { chengyu } from './data/chengyu'
import { load, save } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const mode = ref('study')
const filter = ref('all')
const known = ref(new Set())

const filtered = computed(() =>
  filter.value === 'all' ? chengyu : chengyu.filter(x => x[4] === filter.value)
)
const knownPct = computed(() => Math.round(known.value.size / chengyu.length * 100))

function itemKey(item) {
  return item[0]
}
function tagType(t) {
  return t === 'yicuo' ? 'danger' : t === 'bianxi' ? 'warning' : 'success'
}
function tagText(t) {
  return t === 'yicuo' ? '易错' : t === 'bianxi' ? '辨析' : '高频'
}

// 每日一批：优先未掌握的，从今日索引开始轮转
const batch = computed(() => {
  const pool = filtered.value
  const unlearned = pool.filter(x => !known.value.has(itemKey(x)))
  if (!unlearned.length) return []
  const dayNo = Math.floor(Date.now() / 86400000)
  const start = dayNo % unlearned.length
  return [...unlearned.slice(start), ...unlearned.slice(0, start)].slice(0, 10)
})

function markKnown(item) {
  known.value.add(itemKey(item))
  save(uid.value, 'chengyuDone', [...known.value])
}
function markAll() {
  batch.value.forEach(x => known.value.add(itemKey(x)))
  save(uid.value, 'chengyuDone', [...known.value])
}
function resetDone() {
  known.value = new Set()
  save(uid.value, 'chengyuDone', [])
}

// ---------- 测验 ----------
const quizTotal = ref(0)
const quizQ = ref(null)
const qi = ref(0)
const quizCorrect = ref(0)
const quizRevealed = ref(false)
const quizRight = ref(false)
const quizPicked = ref(-1)
const quizDone = ref(false)

function startQuiz() {
  const pool = filtered.value
  if (pool.length < 4) return
  const idxs = shuffle([...pool.keys()]).slice(0, 10)
  quizItems.value = idxs.map(i => pool[i])
  quizTotal.value = quizItems.value.length
  qi.value = 0
  quizCorrect.value = 0
  quizDone.value = false
  quizRevealed.value = false
  buildQ()
}
const quizItems = ref([])

function buildQ() {
  const item = quizItems.value[qi.value]
  const isMeaning = Math.random() < 0.6
  const others = shuffle(filtered.value.filter(x => x[0] !== item[0])).slice(0, 3)
  const opts = shuffle([item, ...others])
  quizQ.value = {
    q: isMeaning ? `“${item[0]}”的意思是？` : `下列成语中，释义为“${item[2]}”的是？`,
    opts: opts.map(x => (isMeaning ? x[2] : x[0])),
    ans: String.fromCharCode(65 + opts.indexOf(item)),
    reveal: isMeaning ? item[2] : item[0]
  }
  quizPicked.value = -1
  quizRevealed.value = false
  quizRight.value = false
}
function quizOptClass(oi) {
  if (!quizRevealed.value) return ''
  if (String.fromCharCode(65 + oi) === quizQ.value.ans) return 'ok'
  if (oi === quizPicked.value) return 'bad'
  return ''
}
function quizChoose(oi) {
  if (quizRevealed.value) return
  quizPicked.value = oi
  quizRevealed.value = true
  const picked = String.fromCharCode(65 + oi) === quizQ.value.ans
  quizRight.value = picked
  if (picked) quizCorrect.value++
  else {
    // 答错自动标记为“未掌握”提醒
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
function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

onMounted(() => {
  known.value = new Set(load(uid.value, 'chengyuDone', []))
})

// 切到测验模式时自动开始
watch(mode, v => {
  if (v === 'quiz' && !quizItems.value.length) startQuiz()
})
</script>

<style scoped>
.mode-bar { display: flex; gap: 12px; align-items: center; margin: 14px 0; flex-wrap: wrap; }
.batch-head { display: flex; justify-content: space-between; align-items: center; margin: 6px 0 12px; font-size: 14px; font-weight: 600; color: var(--el-color-primary); }
.cy-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 10px;
  position: relative;
  transition: all .15s;
}
.cy-card.known { opacity: .55; background: var(--el-fill-color-lighter); }
.cy-main { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cy-word { font-size: 17px; font-weight: 700; color: var(--el-color-primary); }
.cy-py { font-size: 12px; color: var(--el-text-color-secondary); }
.cy-meaning { font-size: 14px; color: var(--el-text-color-primary); margin-top: 6px; line-height: 1.7; }
.cy-example { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 4px; line-height: 1.7; }
.cy-btn { position: absolute; right: 14px; top: 14px; }
.cy-known { position: absolute; right: 16px; top: 16px; font-size: 13px; color: #67c23a; font-weight: 600; }
.empty-tip { text-align: center; padding: 50px 0; color: var(--el-text-color-secondary); }
.quiz-box { max-width: 720px; }
.quiz-progress { font-size: 13px; color: var(--el-text-color-secondary); margin-bottom: 10px; }
.quiz-q { border: 1px solid var(--el-border-color-light); border-radius: 12px; padding: 18px; }
.quiz-question { font-size: 16px; font-weight: 600; margin-bottom: 14px; line-height: 1.7; }
.quiz-opt {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all .15s;
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
