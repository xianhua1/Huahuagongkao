<template>
  <div class="tab">
    <PageHead icon="clock" title="时政速递" desc="实时新闻简讯（央视《新闻联播》+ 新华社评论员）+ 常考时政测验。热点看实时，考点看测验。" />
<!-- 实时新闻 -->
    <div class="news-wrap">
      <div class="news-head">
        <span class="news-title">📺 实时资讯</span>
        <span class="news-time">更新于 {{ newsTime || '--' }} · 点击卡片查看原文</span>
        <el-button size="small" :loading="newsLoading" @click="loadNews">刷新</el-button>
      </div>
      <div v-if="newsLoading" class="news-loading">正在获取最新资讯……</div>
      <div v-else-if="newsError" class="news-error">
        {{ newsError }}
        <a href="https://news.cctv.com/" target="_blank" rel="noopener">去央视网看新闻 →</a>
      </div>
      <div v-else class="news-cols">
        <!-- 央视快讯：文字简讯 -->
        <div class="news-col">
          <div class="news-col-title">央视快讯 · 文字简讯</div>
          <a
            v-for="(it, i) in kuaixun"
            :key="'k' + i"
            class="news-card"
            :href="it.url"
            target="_blank"
            rel="noopener"
          >
            <div class="nc-title">{{ it.title }}</div>
            <div class="nc-brief">{{ it.brief }}</div>
            <div class="nc-meta">{{ it.date }}</div>
          </a>
          <div v-if="!kuaixun.length" class="news-empty">暂无数据</div>
        </div>
        <!-- 新闻联播：视频条目 -->
        <div class="news-col">
          <div class="news-col-title">《新闻联播》要点</div>
          <a
            v-for="(it, i) in lianbo"
            :key="'l' + i"
            class="news-card video"
            :href="it.url"
            target="_blank"
            rel="noopener"
          >
            <div class="nc-title">{{ it.title }}</div>
            <div class="nc-meta">{{ it.date }} {{ it.time }} · 点击观看视频</div>
          </a>
          <div v-if="!lianbo.length" class="news-empty">暂无数据</div>
        </div>
        <!-- 新华社评论员：标题 + 摘要 -->
        <div class="news-col">
          <div class="news-col-title">新华社评论员文章</div>
          <a
            v-for="(it, i) in xinhua"
            :key="'x' + i"
            class="news-card"
            :href="it.url"
            target="_blank"
            rel="noopener"
          >
            <div class="nc-title">{{ it.title }}</div>
            <div class="nc-brief">{{ it.brief || '点击阅读全文' }}</div>
          </a>
          <div v-if="!xinhua.length" class="news-empty">暂无数据</div>
        </div>
      </div>
    </div>

    <!-- 时政测验 -->
    <div class="quiz-head">
      <span class="news-title">📝 常考时政测验（{{ shizheng.length }} 题）</span>
      <el-button size="small" type="primary" plain @click="startQuiz">随机测验 10 题</el-button>
      <el-button size="small" @click="resetDone">重置进度</el-button>
    </div>

    <div v-if="quizMode" class="quiz-box">
      <div class="quiz-progress">第 {{ qi + 1 }} / {{ quizTotal }} 题 · 答对 {{ quizCorrect }} 题</div>
      <div class="quiz-q">
        <div class="quiz-question">{{ quizQ.q }}</div>
        <div class="quiz-cat">{{ quizQ.c }}</div>
        <div
          v-for="(opt, oi) in quizQ.o"
          :key="oi"
          class="quiz-opt"
          :class="quizOptClass(oi)"
          @click="!quizRevealed && quizChoose(oi)"
        >
          {{ String.fromCharCode(65 + oi) }}. {{ opt }}
        </div>
      </div>
      <div v-if="quizRevealed" class="quiz-result" :class="quizRight ? 'right' : 'wrong'">
        <div>
          <span class="quiz-r-title">{{ quizRight ? '答对啦！' : '答错了，正确答案是 ' + String.fromCharCode(65 + quizQ.a) }}</span>
          <div class="quiz-e">{{ quizQ.e }}</div>
        </div>
        <el-button size="small" type="primary" @click="quizNext">下一题</el-button>
      </div>
    </div>

    <!-- 全部题目浏览 -->
    <div v-else class="sz-list">
      <div v-for="(item, i) in shizheng" :key="i" class="sz-card">
        <div class="sz-q">
          <el-tag size="small" type="info" class="sz-cat">{{ item.c }}</el-tag>
          {{ item.q }}
        </div>
        <div class="sz-opts">
          <div
            v-for="(opt, oi) in item.o"
            :key="oi"
            class="sz-opt"
            :class="szOptClass(item, oi, i)"
            @click="revealItem(i)"
          >
            {{ String.fromCharCode(65 + oi) }}. {{ opt }}
          </div>
        </div>
        <div v-if="revealedSet.has(i)" class="sz-e">
          <span :class="doneSet.has(i) ? 'ok' : 'bad'">
            {{ doneSet.has(i) ? '✓ 已答对' : '✗ 未答对' }}
          </span>
          {{ item.e }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import useUserStore from '@/store/modules/user'
import { shizheng } from './data/shizheng'
import { load, save } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

// ---------- 实时新闻 ----------
const lianbo = ref([])
const kuaixun = ref([])
const xinhua = ref([])
const newsLoading = ref(false)
const newsError = ref('')
const newsTime = ref('')

async function loadNews() {
  newsLoading.value = true
  newsError.value = ''
  try {
    const [r1, r2] = await Promise.all([
      fetch('/news/cctv').then(r => r.json()),
      fetch('/news/xinhua').then(r => r.json())
    ])
    if (r1.ok) {
      lianbo.value = (r1.items && r1.items.lianbo) || []
      kuaixun.value = (r1.items && r1.items.kuaixun) || []
    } else {
      throw new Error(r1.msg || '央视资讯获取失败')
    }
    if (r2.ok) {
      xinhua.value = r2.items || []
    } else {
      throw new Error(r2.msg || '新华社资讯获取失败')
    }
    const t = new Date()
    newsTime.value = t.getHours().toString().padStart(2, '0') + ':' + t.getMinutes().toString().padStart(2, '0')
  } catch (e) {
    newsError.value = e.message || '资讯获取失败'
  } finally {
    newsLoading.value = false
  }
}

// ---------- 测验 ----------
const doneSet = ref(new Set())
const revealedSet = ref(new Set())
const quizMode = ref(false)
const quizItems = ref([])
const quizTotal = ref(0)
const qi = ref(0)
const quizCorrect = ref(0)
const quizRevealed = ref(false)
const quizRight = ref(false)
const quizPicked = ref(-1)
const quizQ = ref(null)

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function startQuiz() {
  quizItems.value = shuffle([...shizheng.keys()]).slice(0, 10)
  quizTotal.value = quizItems.value.length
  qi.value = 0
  quizCorrect.value = 0
  quizDone.value = false
  quizRevealed.value = false
  quizMode.value = true
  buildQ()
}
const quizDone = ref(false)

function buildQ() {
  const item = shizheng[quizItems.value[qi.value]]
  quizQ.value = { c: item.c, q: item.q, o: item.o, a: item.a, e: item.e }
  quizPicked.value = -1
  quizRevealed.value = false
  quizRight.value = false
}

function quizOptClass(oi) {
  if (!quizRevealed.value) return ''
  if (oi === quizQ.value.a) return 'ok'
  if (oi === quizPicked.value) return 'bad'
  return ''
}

function quizChoose(oi) {
  if (quizRevealed.value) return
  quizPicked.value = oi
  quizRevealed.value = true
  const right = oi === quizQ.value.a
  quizRight.value = right
  const realIdx = quizItems.value[qi.value]
  if (right) {
    quizCorrect.value++
    doneSet.value.add(realIdx)
    save(uid.value, 'shizhengDone', [...doneSet.value])
  }
}

function quizNext() {
  qi.value++
  if (qi.value >= quizTotal.value) {
    quizMode.value = false
  } else {
    buildQ()
  }
}

// ---------- 浏览模式 ----------
function revealItem(i) {
  revealedSet.value.add(i)
}
function szOptClass(item, oi, i) {
  if (!revealedSet.value.has(i)) return ''
  if (oi === item.a) return 'ok'
  return ''
}
function resetDone() {
  doneSet.value = new Set()
  save(uid.value, 'shizhengDone', [])
}

onMounted(() => {
  doneSet.value = new Set(load(uid.value, 'shizhengDone', []))
  loadNews()
})
</script>

<style scoped>
.news-wrap {
  border: 1px solid var(--el-border-color-light);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 20px;
  background: var(--el-bg-color);
  box-shadow: 0 2px 12px rgba(31, 45, 61, .05);
}
.news-head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.news-title { font-size: 15px; font-weight: 700; }
.news-time { font-size: 12px; color: var(--el-text-color-secondary); flex: 1; }
.news-loading, .news-error, .news-empty { font-size: 13px; color: var(--el-text-color-secondary); padding: 14px 0; }
.news-error a { color: var(--el-color-primary); margin-left: 8px; }
.news-cols { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
@media (max-width: 1200px) { .news-cols { grid-template-columns: 1fr; } }
.news-col { min-width: 0; }
.news-col-title {
  font-size: 13px; font-weight: 700; color: var(--el-color-primary);
  margin-bottom: 8px; padding-left: 8px;
  border-left: 3px solid var(--el-color-primary);
}
.news-card {
  display: block;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 8px;
  text-decoration: none;
  transition: all .18s;
  background: var(--el-bg-color);
}
.news-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 14px rgba(64, 158, 255, .18);
  transform: translateY(-2px);
}
.news-card.video { background: var(--el-color-primary-light-9); }
.nc-title {
  font-size: 13px; font-weight: 600; color: var(--el-text-color-primary);
  line-height: 1.5; margin-bottom: 4px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.news-card:hover .nc-title { color: var(--el-color-primary); }
.nc-brief {
  font-size: 12px; color: var(--el-text-color-secondary);
  line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.nc-meta { font-size: 11px; color: var(--el-text-color-placeholder); margin-top: 5px; }
.quiz-head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.quiz-box { max-width: 780px; }
.quiz-progress { font-size: 13px; color: var(--el-text-color-secondary); margin-bottom: 10px; }
.quiz-q { border: 1px solid var(--el-border-color-light); border-radius: 12px; padding: 18px; }
.quiz-question { font-size: 15px; font-weight: 600; line-height: 1.8; }
.quiz-cat { display: inline-block; font-size: 11px; color: var(--el-color-primary); background: var(--el-color-primary-light-9); border-radius: 8px; padding: 1px 8px; margin: 8px 0 12px; }
.quiz-opt {
  border: 1px solid var(--el-border-color); border-radius: 8px;
  padding: 10px 14px; margin-bottom: 8px; cursor: pointer;
  font-size: 14px; transition: all .15s; line-height: 1.6;
}
.quiz-opt:hover { border-color: var(--el-color-primary); }
.quiz-opt.ok { border-color: #67c23a; background: #f0f9eb; }
.quiz-opt.bad { border-color: #f56c6c; background: #fef0f0; }
.quiz-result { margin-top: 12px; padding: 12px 14px; border-radius: 8px; display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; font-size: 14px; }
.quiz-result.right { background: #f0f9eb; }
.quiz-result.wrong { background: #fef0f0; }
.quiz-r-title { font-weight: 700; }
.quiz-result.right .quiz-r-title { color: #67c23a; }
.quiz-result.wrong .quiz-r-title { color: #f56c6c; }
.quiz-e { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.7; margin-top: 4px; }
.sz-list { display: flex; flex-direction: column; gap: 12px; }
.sz-card { border: 1px solid var(--el-border-color-light); border-radius: 10px; padding: 14px 16px; }
.sz-q { font-size: 14px; font-weight: 600; line-height: 1.7; display: flex; align-items: flex-start; gap: 8px; }
.sz-cat { flex-shrink: 0; margin-top: 2px; }
.sz-opts { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
.sz-opt {
  border: 1px solid var(--el-border-color); border-radius: 8px;
  padding: 8px 12px; cursor: pointer; font-size: 13px; transition: all .15s; line-height: 1.6;
}
.sz-opt:hover { border-color: var(--el-color-primary); }
.sz-opt.ok { border-color: #67c23a; background: #f0f9eb; }
.sz-e { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.7; background: var(--el-fill-color-light); border-radius: 8px; padding: 10px 12px; margin-top: 10px; }
.sz-e .ok { color: #67c23a; font-weight: 700; margin-right: 6px; }
.sz-e .bad { color: #f56c6c; font-weight: 700; margin-right: 6px; }
</style>
