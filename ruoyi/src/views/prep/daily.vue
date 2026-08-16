<template>
  <div class="tab">
    <PageHead icon="edit" title="每日一练" desc="每天 10 题（常识 2 + 言语 3 + 判断 2 + 数量 1 + 资料 2），10 分钟保持手感。错题自动进入错题本。" />
<!-- 加载中 -->
    <div v-if="phase === 'loading'" class="empty">
      <el-icon :size="40" class="is-loading" color="#409eff"><Loading /></el-icon>
      <p>正在为你挑选今天的题目……</p>
    </div>

    <!-- 答题 -->
    <div v-else-if="phase === 'quiz' && q">
      <div class="q-progress">
        <el-progress :percentage="Math.round(done / total * 100)" :stroke-width="10" :show-text="false" />
        <span class="q-count">{{ done + 1 }} / {{ total }}</span>
      </div>

      <!-- 材料 -->
      <div v-if="q.material" class="material-box">
        <div class="material-title">【材料】</div>
        <div class="material-content" v-html="q.material"></div>
      </div>

      <div class="q-card">
        <div class="q-section">{{ q.section }} · 第 {{ q.qno }} 题</div>
        <div class="q-stem" v-html="q.stem"></div>
        <div class="q-opts">
          <div
            v-for="opt in q.optList"
            :key="opt.label"
            class="q-opt"
            :class="optClass(opt.label)"
            @click="!revealed && choose(opt.label)"
          >
            <span class="q-opt-label">{{ opt.label }}</span>
            <span class="q-opt-html" v-html="opt.html"></span>
            <el-icon v-if="revealed && opt.label === q.answer" class="q-mark ok"><CircleCheckFilled /></el-icon>
            <el-icon v-else-if="revealed && opt.label === myAnswer" class="q-mark bad"><CircleCloseFilled /></el-icon>
          </div>
        </div>
        <div v-if="revealed" class="q-result" :class="isRight ? 'right' : 'wrong'">
          <div class="q-result-title">
            {{ isRight ? '回答正确！' : '回答错误' }}
            <span v-if="!isRight">正确答案：{{ q.answer }}</span>
          </div>
          <div class="q-analysis" v-html="q.analysis || '本题暂无解析'"></div>
          <el-button v-if="!isRight" size="small" type="danger" plain @click="markWrongToBook">加入错题本</el-button>
          <el-button type="primary" size="small" class="next-btn" @click="next">{{ done + 1 >= total ? '查看结果' : '下一题' }}</el-button>
        </div>
      </div>
    </div>

    <!-- 完成 -->
    <div v-else-if="phase === 'done'" class="done-box">
      <div class="done-icon"><el-icon :size="52" color="#67c23a"><CircleCheckFilled /></el-icon></div>
      <h3>今日练习完成！</h3>
      <p class="done-score">答对 <b>{{ correctCount }}</b> / {{ total }} 题，正确率 {{ Math.round(correctCount / total * 100) }}%</p>
      <p class="done-tip">错题已自动加入错题本，明天记得继续打卡哦～</p>
      <el-button type="primary" @click="regenerate">再练一组</el-button>
      <el-button @click="goWrong">去错题本复习</el-button>
    </div>

    <!-- 错误 -->
    <div v-else-if="phase === 'error'" class="empty">
      <el-icon :size="40" color="#f56c6c"><WarningFilled /></el-icon>
      <p>{{ errMsg }}</p>
      <el-button type="primary" size="small" @click="init">重试</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import useUserStore from '@/store/modules/user'
import request from '@/utils/request'
import { Loading, WarningFilled, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { load, save, today, addCheckin } from './store'
import PageHead from './PageHead.vue'

const router = useRouter()
const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const phase = ref('loading')
const questions = ref([])
const done = ref(0)
const myAnswer = ref('')
const revealed = ref(false)
const correctCount = ref(0)
const errMsg = ref('')

const total = computed(() => questions.value.length)
const q = computed(() => questions.value[done.value] || null)
const isRight = computed(() => revealed.value && myAnswer.value === q.value.answer)

const SECTIONS = [['常识判断', 2], ['言语理解与表达', 3], ['判断推理', 2], ['数量关系', 1], ['资料分析', 2]]

function parseOpts(str) {
  try {
    const arr = JSON.parse(str || '[]')
    return arr.map(o => ({ label: o.label, html: o.html || '' }))
  } catch (e) {
    return []
  }
}

function optClass(label) {
  if (!revealed.value) return ''
  if (label === q.value.answer) return 'ok'
  if (label === myAnswer.value) return 'bad'
  return ''
}

async function fetchSet() {
  const results = []
  for (const [section, count] of SECTIONS) {
    const res = await request.get('/exam/random', { params: { section, count } })
    const data = res.data || {}
    const qs = data.questions || []
    const mats = {}
    ;(data.materials || []).forEach(m => { mats[m.id] = m.content })
    qs.forEach(x => {
      results.push({
        id: x.id,
        section: x.section,
        qno: x.qno,
        stem: x.stem || '',
        answer: (x.answer || '').trim().toUpperCase(),
        analysis: x.analysis || '',
        material: x.materialId ? (mats[x.materialId] || '') : '',
        optList: parseOpts(x.options)
      })
    })
  }
  return results
}

async function init() {
  phase.value = 'loading'
  try {
    const t = today()
    const saved = load(uid.value, 'daily', null)
    if (saved && saved.date === t && saved.questions && saved.questions.length) {
      questions.value = saved.questions
      done.value = saved.done || 0
      myAnswer.value = ''
      revealed.value = false
      if (done.value >= questions.value.length) {
        phase.value = 'done'
      } else {
        phase.value = 'quiz'
      }
      return
    }
    questions.value = await fetchSet()
    done.value = 0
    save(uid.value, 'daily', { date: t, questions: questions.value, done: 0 })
    phase.value = 'quiz'
  } catch (e) {
    phase.value = 'error'
    errMsg.value = '题目获取失败：' + (e.message || '网络异常，请稍后重试')
  }
}

function choose(label) {
  if (revealed.value) return
  myAnswer.value = label
  revealed.value = true
  if (label === q.value.answer) correctCount.value++
  // 保存答题记录（同步后端，进入错题本与学习报告）
  saveRecord(q.value.id, label)
}

async function saveRecord(questionId, userAnswer) {
  try {
    await request.post('/exam/record/save', { questionId, userAnswer })
  } catch (e) {
    /* ignore */
  }
}

function markWrongToBook() {
  saveRecord(q.value.id, myAnswer.value)
  // 已是错题状态，提示即可
  revealed.value = true
}

function next() {
  const nextIdx = done.value + 1
  done.value = nextIdx
  myAnswer.value = ''
  revealed.value = false
  const cur = load(uid.value, 'daily', null)
  if (cur) {
    cur.done = nextIdx
    save(uid.value, 'daily', cur)
  }
  if (nextIdx >= questions.value.length) {
    const cur2 = load(uid.value, 'daily', null)
    if (cur2) {
      cur2.done = questions.value.length
      save(uid.value, 'daily', cur2)
    }
    addCheckin(uid.value)
    phase.value = 'done'
  }
}

function regenerate() {
  localStorage.removeItem('dsh.prep.' + uid.value + '.daily')
  init()
}

function goWrong() {
  router.push('/practice/wrong')
}

onMounted(init)
</script>

<style scoped>
.empty { text-align: center; padding: 70px 0; color: var(--el-text-color-secondary); }
.empty p { margin: 12px 0 16px; }
.q-progress { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
.q-progress .el-progress { flex: 1; }
.q-count { font-size: 14px; color: var(--el-text-color-secondary); flex-shrink: 0; }
.material-box {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 14px;
  max-height: 220px;
  overflow-y: auto;
}
.material-title { font-weight: 700; color: var(--el-color-primary); font-size: 13px; margin-bottom: 6px; }
.material-content { font-size: 14px; line-height: 1.8; color: var(--el-text-color-regular); }
.material-content :deep(img) { max-width: 100%; }
.q-card { border: 1px solid var(--el-border-color-light); border-radius: 12px; padding: 18px 20px; }
.q-section { font-size: 12px; color: var(--el-color-primary); background: var(--el-color-primary-light-9); display: inline-block; padding: 2px 10px; border-radius: 10px; margin-bottom: 10px; }
.q-stem { font-size: 15px; line-height: 1.9; color: var(--el-text-color-primary); margin-bottom: 14px; }
.q-stem :deep(img) { max-width: 100%; }
.q-opts { display: flex; flex-direction: column; gap: 10px; }
.q-opt {
  display: flex; align-items: flex-start; gap: 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all .15s;
  position: relative;
}
.q-opt:hover { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.q-opt.ok { border-color: #67c23a; background: #f0f9eb; }
.q-opt.bad { border-color: #f56c6c; background: #fef0f0; }
.q-opt-label { font-weight: 700; color: var(--el-color-primary); flex-shrink: 0; }
.q-opt-html { font-size: 14px; line-height: 1.7; color: var(--el-text-color-regular); }
.q-opt-html :deep(img) { max-width: 100%; vertical-align: middle; }
.q-mark { position: absolute; right: 12px; top: 12px; }
.q-mark.ok { color: #67c23a; }
.q-mark.bad { color: #f56c6c; }
.q-result { margin-top: 16px; border-radius: 10px; padding: 14px 16px; }
.q-result.right { background: #f0f9eb; border: 1px solid #b3e19d; }
.q-result.wrong { background: #fef0f0; border: 1px solid #fbc4c4; }
.q-result-title { font-weight: 700; font-size: 15px; margin-bottom: 8px; }
.q-result.right .q-result-title { color: #67c23a; }
.q-result.wrong .q-result-title { color: #f56c6c; }
.q-analysis { font-size: 14px; line-height: 1.9; color: var(--el-text-color-regular); }
.q-analysis :deep(img) { max-width: 100%; }
.next-btn { float: right; }
.done-box { text-align: center; padding: 60px 0; }
.done-icon { margin-bottom: 10px; }
.done-box h3 { margin: 0 0 8px; font-size: 22px; }
.done-score { font-size: 17px; }
.done-score b { color: #67c23a; font-size: 22px; }
.done-tip { font-size: 13px; color: var(--el-text-color-secondary); margin: 6px 0 20px; }
</style>
