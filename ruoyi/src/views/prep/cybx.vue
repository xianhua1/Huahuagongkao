<template>
  <div class="tab">
    <PageHead icon="exchange" title="词语辨析练习" :desc="`从 ${words.length} 个高频词语中随机出题：看词选义 / 看义选词，辨析易混词。`" />

    <div class="mode-bar">
      <el-radio-group v-model="mode" size="small">
        <el-radio-button value="quiz">✏️ 随堂练习</el-radio-button>
        <el-radio-button value="list">📋 全部词语</el-radio-button>
      </el-radio-group>
      <el-button size="small" type="primary" plain @click="startQuiz">重新出题（10 题）</el-button>
    </div>

    <!-- 练习 -->
    <template v-if="mode === 'quiz'">
      <div v-if="!quizDone && quizQ" class="quiz-box">
        <div class="quiz-progress">第 {{ qi + 1 }} / {{ quizTotal }} 题 · 答对 {{ quizCorrect }} 题 · 已用时 {{ elapsed }}s</div>
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
          <span>
            {{ quizRight ? '答对啦！' : '答错了' }} 正确答案：{{ quizQ.ans }}
            <span class="quiz-explain">{{ quizQ.explain }}</span>
          </span>
          <el-button size="small" type="primary" @click="quizNext">下一题</el-button>
        </div>
      </div>
      <div v-else-if="quizDone" class="done-box">
        <h3>练习完成！答对 {{ quizCorrect }} / {{ quizTotal }}</h3>
        <p class="done-tip">
          <span v-if="quizCorrect >= 8">🎉 掌握得很扎实，继续保持！</span>
          <span v-else-if="quizCorrect >= 5">👍 基本过关，错题建议回「高频词语」重点复习。</span>
          <span v-else>💪 别灰心，先去「高频词语」学一遍再回来挑战。</span>
        </p>
        <el-button type="primary" size="small" @click="startQuiz">再来一组</el-button>
      </div>
    </template>

    <!-- 列表 -->
    <template v-else>
      <div class="search-bar">
        <el-input v-model="kw" placeholder="搜索词语或释义…" size="small" clearable style="width: 260px" />
        <span class="list-count">共 {{ filteredWords.length }} 条</span>
      </div>
      <div v-for="(w, i) in filteredWords" :key="i" class="cy-card">
        <div class="cy-main">
          <span class="cy-word">{{ w[0] }}</span>
          <span class="cy-py">{{ w[1] }}</span>
          <el-button
            size="small" text type="primary" class="cy-add"
            @click="collect(w)"
          >+ 加入生词锦囊</el-button>
        </div>
        <div class="cy-meaning">{{ w[2] }}</div>
        <div class="cy-example">例句：{{ w[3] }}</div>
      </div>
      <div v-if="!filteredWords.length" class="empty-tip">没有匹配的词语。</div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import useUserStore from '@/store/modules/user'
import { words } from './data/words'
import { load, save } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const mode = ref('quiz')
const kw = ref('')

const filteredWords = computed(() => {
  const k = kw.value.trim()
  if (!k) return words
  return words.filter(w => w[0].includes(k) || w[2].includes(k) || w[1].includes(k))
})

// ---------- 练习 ----------
const quizTotal = ref(0)
const quizItems = ref([])
const quizQ = ref(null)
const qi = ref(0)
const quizCorrect = ref(0)
const quizRevealed = ref(false)
const quizRight = ref(false)
const quizPicked = ref(-1)
const quizDone = ref(false)
const elapsed = ref(0)
let timer = null

function startQuiz() {
  const pool = filteredWords.value.length >= 4 ? filteredWords.value : words
  const idxs = shuffle([...pool.keys()]).slice(0, 10)
  quizItems.value = idxs.map(i => pool[i])
  quizTotal.value = quizItems.value.length
  qi.value = 0
  quizCorrect.value = 0
  quizDone.value = false
  quizRevealed.value = false
  elapsed.value = 0
  clearInterval(timer)
  timer = setInterval(() => elapsed.value++, 1000)
  buildQ()
}

function buildQ() {
  const item = quizItems.value[qi.value]
  const isMeaning = Math.random() < 0.6
  const others = shuffle(words.filter(x => x[0] !== item[0])).slice(0, 3)
  const opts = shuffle([item, ...others])
  quizQ.value = {
    q: isMeaning ? `“${item[0]}”的意思是？` : `下列词语中，释义为“${item[2]}”的是？`,
    opts: opts.map(x => (isMeaning ? x[2] : x[0])),
    ans: String.fromCharCode(65 + opts.indexOf(item)),
    explain: isMeaning ? item[2] : item[0]
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
  quizRight.value = String.fromCharCode(65 + oi) === quizQ.value.ans
  if (quizRight.value) quizCorrect.value++
}
function quizNext() {
  qi.value++
  if (qi.value >= quizTotal.value) {
    quizDone.value = true
    clearInterval(timer)
  } else {
    buildQ()
  }
}

// ---------- 生词锦囊 ----------
function collect(w) {
  const list = load(uid.value, 'mywords', [])
  if (!list.some(x => x[0] === w[0])) {
    list.push(w)
    save(uid.value, 'mywords', list)
    ElMessage.success('已加入生词锦囊')
  } else {
    ElMessage.info('已在生词锦囊中')
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

onMounted(startQuiz)
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.mode-bar { display: flex; gap: 12px; align-items: center; margin: 14px 0; flex-wrap: wrap; }
.search-bar { display: flex; gap: 12px; align-items: center; margin: 6px 0 14px; }
.list-count { font-size: 13px; color: var(--el-text-color-secondary); }
.cy-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 10px;
  position: relative;
}
.cy-main { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cy-word { font-size: 17px; font-weight: 700; color: var(--el-color-primary); }
.cy-py { font-size: 12px; color: var(--el-text-color-secondary); }
.cy-add { margin-left: auto; }
.cy-meaning { font-size: 14px; color: var(--el-text-color-primary); margin-top: 6px; line-height: 1.7; }
.cy-example { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 4px; line-height: 1.7; }
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
.quiz-explain { font-weight: 400; margin-left: 8px; }
.done-box { text-align: center; padding: 40px 0; }
.done-box h3 { font-size: 20px; margin: 0 0 8px; }
.done-tip { font-size: 13px; color: var(--el-text-color-secondary); margin: 0 0 16px; }
</style>
