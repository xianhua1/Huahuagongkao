<template>
  <div class="app-container">
    <!-- 试卷列表 -->
    <el-card shadow="never">
      <div class="table-head">
        <div>
          <h3>申论题库管理</h3>
          <p>试卷 / 材料 / 题目的增删改查，支持图片上传（材料或题干中插入图片）。</p>
        </div>
        <el-button type="primary" @click="openPaperDialog()">＋ 新增试卷</el-button>
      </div>
      <el-table :data="papers" v-loading="loading" border>
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="title" label="试卷标题" min-width="260" />
        <el-table-column prop="version" label="版本" width="110" />
        <el-table-column prop="questionCount" label="题数" width="70" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="manage(row)">材料与题目</el-button>
            <el-button size="small" @click="openPaperDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="delPaper(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 试卷编辑 -->
    <el-dialog v-model="paperShow" :title="paperForm.id ? '编辑试卷' : '新增试卷'" width="560px">
      <el-form label-width="90px">
        <el-form-item label="试卷标题"><el-input v-model="paperForm.title" /></el-form-item>
        <el-form-item label="年份"><el-input-number v-model="paperForm.year" :min="1999" :max="2030" /></el-form-item>
        <el-form-item label="版本">
          <el-select v-model="paperForm.version">
            <el-option label="副省级" value="副省级" />
            <el-option label="地市级" value="地市级" />
            <el-option label="省部级" value="省部级" />
            <el-option label="行政执法类" value="行政执法类" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="paperShow = false">取消</el-button>
        <el-button type="primary" @click="savePaper">保存</el-button>
      </template>
    </el-dialog>

    <!-- 材料与题目管理 -->
    <el-drawer v-model="drawer" size="86%" :title="'管理：' + (curPaper ? curPaper.title : '')">
      <div class="drawer-body">
        <el-tabs v-model="tab">
          <!-- 材料 -->
          <el-tab-pane label="📄 材料" name="mat">
            <div class="pane-actions">
              <el-button type="primary" size="small" @click="openMatDialog()">＋ 新增材料</el-button>
            </div>
            <el-table :data="materials" border size="small">
              <el-table-column prop="mNo" label="编号" width="70" />
              <el-table-column prop="title" label="标题" width="140" />
              <el-table-column label="内容预览" min-width="320">
                <template #default="{ row }"><span class="preview">{{ stripHtml(row.content).slice(0, 60) }}</span></template>
              </el-table-column>
              <el-table-column label="操作" width="160">
                <template #default="{ row }">
                  <el-button size="small" @click="openMatDialog(row)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="delMat(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 题目（可编辑） -->
          <el-tab-pane label="✍️ 题目" name="q">
            <div class="pane-actions">
              <el-button type="primary" size="small" @click="openQDialog()">＋ 新增题目</el-button>
            </div>
            <el-table :data="questions" border size="small">
              <el-table-column prop="qno" label="题号" width="70" />
              <el-table-column prop="score" label="分值" width="70" />
              <el-table-column prop="wordLimit" label="字数" width="80" />
              <el-table-column label="题目" min-width="300">
                <template #default="{ row }"><span class="preview">{{ stripHtml(row.title).slice(0, 90) }}</span></template>
              </el-table-column>
              <el-table-column label="参考答案" min-width="240">
                <template #default="{ row }"><span class="preview">{{ stripHtml(row.refAnswer || '').slice(0, 60) }}</span></template>
              </el-table-column>
              <el-table-column label="操作" width="160">
                <template #default="{ row }">
                  <el-button size="small" @click="openQDialog(row)">编辑</el-button>
                  <el-button size="small" type="danger" plain @click="delQ(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>

    <!-- 材料编辑 -->
    <el-dialog v-model="matShow" :title="matForm.id ? '编辑材料' : '新增材料'" width="780px" top="4vh">
      <el-form label-width="80px">
        <el-form-item label="编号"><el-input-number v-model="matForm.mNo" :min="1" /></el-form-item>
        <el-form-item label="标题"><el-input v-model="matForm.title" placeholder="材料1" /></el-form-item>
        <el-form-item label="内容">
          <el-input v-model="matForm.content" type="textarea" :rows="12" placeholder="材料正文，支持 <img> 图片标签" />
          <div style="margin-top: 8px">
            <el-upload :action="uploadUrl" :headers="uploadHeaders" :show-file-list="false" accept="image/*" @success="onImgOk('content')">
              <el-button size="small" type="primary" plain>📷 上传图片到光标后</el-button>
            </el-upload>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="matShow = false">取消</el-button>
        <el-button type="primary" @click="saveMat">保存</el-button>
      </template>
    </el-dialog>

    <!-- 题目编辑 -->
    <el-dialog v-model="qShow" :title="qForm.id ? '编辑题目' : '新增题目'" width="820px" top="3vh">
      <el-form label-width="90px">
        <el-form-item label="题号"><el-input-number v-model="qForm.qno" :min="1" /></el-form-item>
        <el-form-item label="分值"><el-input-number v-model="qForm.score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="字数限制"><el-input-number v-model="qForm.wordLimit" :min="0" :max="1500" /></el-form-item>
        <el-form-item label="题目">
          <el-input v-model="qForm.title" type="textarea" :rows="5" placeholder="题目内容（含要求），支持 <img>" />
          <div style="margin-top: 8px">
            <el-upload :action="uploadUrl" :headers="uploadHeaders" :show-file-list="false" accept="image/*" @success="onImgOk('title')">
              <el-button size="small" type="primary" plain>📷 上传图片</el-button>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="参考答案">
          <el-input v-model="qForm.refAnswer" type="textarea" :rows="8" placeholder="参考答案要点，AI 评分时参考" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="qShow = false">取消</el-button>
        <el-button type="primary" @click="saveQ">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import useUserStore from '@/store/modules/user'

const userStore = useUserStore()
const uploadUrl = '/prod-api/common/upload'
const uploadHeaders = { Authorization: 'Bearer ' + (userStore.token || '') }

const loading = ref(false)
const papers = ref([])
const paperShow = ref(false)
const paperForm = ref({})
const drawer = ref(false)
const tab = ref('mat')
const curPaper = ref(null)
const materials = ref([])
const questions = ref([])
const matShow = ref(false)
const matForm = ref({})
const qShow = ref(false)
const qForm = ref({})

function stripHtml(s) {
  return String(s || '').replace(/<[^>]+>/g, ' ')
}

async function loadPapers() {
  loading.value = true
  try {
    const res = await request.get('/shenlun/paper/list')
    papers.value = res.data || []
  } finally {
    loading.value = false
  }
}

function openPaperDialog(row) {
  paperForm.value = row ? { ...row } : { title: '', year: 2022, version: '副省级' }
  paperShow.value = true
}
async function savePaper() {
  if (!paperForm.value.title) {
    ElMessage.warning('请填写标题')
    return
  }
  if (paperForm.value.id) {
    await request.put('/shenlun/paper', paperForm.value)
  } else {
    await request.post('/shenlun/paper', paperForm.value)
  }
  ElMessage.success('已保存')
  paperShow.value = false
  loadPapers()
}
async function delPaper(row) {
  const ok = await ElMessageBox.confirm('删除试卷将同时删除其材料与题目，确认？', '警告', { type: 'warning' }).catch(() => false)
  if (!ok) return
  await request.delete('/shenlun/paper/' + row.id)
  ElMessage.success('已删除')
  loadPapers()
}

async function manage(row) {
  curPaper.value = row
  const res = await request.get('/shenlun/paper/' + row.id)
  materials.value = res.data.materials || []
  questions.value = res.data.questions || []
  drawer.value = true
}

function openMatDialog(row) {
  matForm.value = row ? { ...row } : { paperId: curPaper.value.id, mNo: materials.value.length + 1, title: '', content: '' }
  matShow.value = true
}
async function saveMat() {
  if (matForm.value.id) {
    await request.put('/shenlun/material', matForm.value)
  } else {
    await request.post('/shenlun/material', matForm.value)
  }
  ElMessage.success('已保存')
  matShow.value = false
  manage(curPaper.value)
}

async function delMat(row) {
  const ok = await ElMessageBox.confirm('确认删除该材料？', '提示', { type: 'warning' }).catch(() => false)
  if (!ok) return
  await request.delete('/shenlun/material/' + row.id)
  ElMessage.success('已删除')
  manage(curPaper.value)
}

function openQDialog(row) {
  qForm.value = row
    ? { ...row }
    : { paperId: curPaper.value.id, qno: questions.value.length + 1, score: 15, wordLimit: 300, title: '', refAnswer: '' }
  qShow.value = true
}
async function saveQ() {
  if (qForm.value.id) {
    await request.put('/shenlun/question', qForm.value)
  } else {
    await request.post('/shenlun/question', qForm.value)
  }
  ElMessage.success('已保存')
  qShow.value = false
  manage(curPaper.value)
}
async function delQ(row) {
  const ok = await ElMessageBox.confirm('确认删除该题目？', '提示', { type: 'warning' }).catch(() => false)
  if (!ok) return
  await request.delete('/shenlun/question/' + row.id)
  ElMessage.success('已删除')
  manage(curPaper.value)
}

function onImgOk(field) {
  return (resp) => {
    try {
      const d = typeof resp === 'string' ? JSON.parse(resp) : resp
      if (d && d.fileName) {
        const img = '<img src="' + d.fileName + '" style="max-width:100%" />'
        const form = field === 'content' ? matForm.value : qForm.value
        form[field] = (form[field] || '') + img
        ElMessage.success('图片已插入')
      } else {
        ElMessage.error('上传失败')
      }
    } catch (e) {
      ElMessage.error('上传响应异常')
    }
  }
}

onMounted(loadPapers)
</script>

<style scoped>
.table-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.table-head h3 { margin: 0 0 4px; }
.table-head p { margin: 0; font-size: 12px; color: var(--el-text-color-secondary); }
.pane-actions { margin-bottom: 12px; }
.preview { font-size: 12px; color: var(--el-text-color-secondary); }
.drawer-body { padding: 0 8px; }
</style>
