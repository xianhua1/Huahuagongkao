<template>
  <div class="app-container">
    <el-card shadow="never">
      <el-form :model="query" inline>
        <el-form-item label="试卷">
          <el-select v-model="query.paperId" placeholder="全部试卷" clearable filterable style="width: 260px" @change="getList">
            <el-option v-for="p in papers" :key="p.id" :label="p.title" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="query.section" placeholder="全部题型" clearable style="width: 160px" @change="getList">
            <el-option v-for="s in sections" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="缺答案">
          <el-switch v-model="query.answerEmpty" active-value="1" inactive-value="" @change="getList" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getList">查询</el-button>
          <el-button type="success" @click="openAdd">
            <el-icon><Plus /></el-icon>新增题目
          </el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="list">
        <el-table-column label="ID" prop="id" width="70" align="center" />
        <el-table-column label="试卷ID" prop="paperId" width="80" align="center" />
        <el-table-column label="题号" prop="qorder" width="70" align="center" />
        <el-table-column label="题型" prop="section" width="140" align="center" />
        <el-table-column label="题干" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">{{ plainText(row.stem) }}</template>
        </el-table-column>
        <el-table-column label="答案" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.answer" type="success">{{ row.answer }}</el-tag>
            <el-tag v-else type="danger">缺</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="图片" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.hasImage" type="warning">有</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total > 0"
        :total="total"
        v-model:page="query.pageNum"
        v-model:limit="query.pageSize"
        @pagination="onPagination"
      />
    </el-card>

    <el-dialog v-model="editVisible" :title="editForm.id ? '编辑题目' : '新增题目'" width="800px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item v-if="!editForm.id" label="所属试卷" required>
          <el-select
            v-model="editForm.paperId"
            filterable
            allow-create
            default-first-option
            placeholder="选择已有试卷，或直接输入新试卷名称"
            style="width: 100%"
          >
            <el-option v-for="p in papers" :key="p.id" :label="p.title" :value="p.id" />
          </el-select>
          <div v-if="isNewPaper" class="new-paper-box">
            <span class="tip-text">检测到新试卷名「{{ editForm.paperId }}」，将自动创建</span>
            <div class="new-paper-row">
              <el-input-number v-model="editForm.newPaperYear" :min="1990" :max="2035" placeholder="年份" style="width: 110px" />
              <el-select v-model="editForm.newPaperSubject" style="width: 120px">
                <el-option label="国考行测" value="行测" />
                <el-option label="事业单位职测" value="职测" />
              </el-select>
              <el-select v-model="editForm.newPaperVersion" style="width: 120px">
                <el-option label="副省级" value="副省级" />
                <el-option label="地市级" value="地市级" />
                <el-option label="A类" value="A类" />
                <el-option label="B类" value="B类" />
                <el-option label="C类" value="C类" />
                <el-option label="D类" value="D类" />
                <el-option label="E类" value="E类" />
                <el-option label="自定义" value="自定义" />
              </el-select>
            </div>
          </div>
        </el-form-item>
        <el-form-item v-else label="所属试卷">
          <span class="tip-text">{{ paperTitleOf(editForm.paperId) }}（题号 {{ editForm.qno }}）</span>
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="editForm.section" clearable style="width: 100%">
            <el-option v-for="s in sections" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="材料">
          <div class="field-col">
            <el-input v-model="editForm.materialText" type="textarea" :rows="3" placeholder="该题对应的阅读材料（可选）" />
            <image-upload v-model="editForm.materialImages" :limit="5" />
          </div>
        </el-form-item>
        <el-form-item label="题干" required>
          <div class="field-col">
            <el-input v-model="editForm.stem" type="textarea" :rows="4" placeholder="题干文本" />
            <image-upload v-model="editForm.stemImages" :limit="5" />
          </div>
        </el-form-item>
        <el-form-item label="选项">
          <div class="opt-list">
            <div v-for="(opt, i) in editForm.optionRows" :key="opt.key" class="opt-row">
              <span class="opt-letter">{{ opt.label }}</span>
              <el-input v-model="opt.text" placeholder="选项内容（可选，也可只上传图片）" />
              <image-upload v-model="opt.images" :limit="1" style="width: 110px" />
              <el-button v-if="editForm.optionRows.length > 2" link type="danger" @click="removeOption(i)">删除</el-button>
            </div>
            <el-button link type="primary" @click="addOption">
              <el-icon><Plus /></el-icon>添加选项
            </el-button>
          </div>
        </el-form-item>
        <el-form-item v-if="!editForm.id" label="题号">
          <el-input-number v-model="editForm.qno" :min="1" :max="9999" placeholder="留空自动接在卷末" style="width: 160px" />
          <span class="tip-text">留空则自动排在试卷最后</span>
        </el-form-item>
        <el-form-item label="正确答案">
          <el-radio-group v-model="editForm.answer">
            <el-radio-button v-for="l in answerLabels" :key="l" :value="l">{{ l }}</el-radio-button>
            <el-radio-button value="">无</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="解析">
          <div class="field-col">
            <el-input v-model="editForm.analysis" type="textarea" :rows="4" placeholder="填写该题解析（多行文本，可选）" />
            <image-upload v-model="editForm.analysisImages" :limit="5" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { listPapers, questionPage, updateQuestion, addQuestion, addPaper, getMaterial } from '@/api/exam'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const papers = ref([])
const query = ref({ paperId: undefined, section: undefined, answerEmpty: '', pageNum: 1, pageSize: 10 })
const sections = ['常识判断', '言语理解与表达', '数量关系', '判断推理', '资料分析']
const editVisible = ref(false)
const editForm = ref({
  id: undefined, paperId: undefined, section: undefined, qno: undefined,
  stem: '', materialText: '', materialImages: '', stemImages: '',
  optionRows: [], answer: '', analysis: '', analysisImages: '',
  newPaperYear: new Date().getFullYear(), newPaperSubject: '行测', newPaperVersion: '自定义'
})
const answerLabels = ['A', 'B', 'C', 'D', 'E', 'F']
let optKey = 0

const isNewPaper = computed(() => typeof editForm.value.paperId === 'string' && editForm.value.paperId.trim() !== '')

function newOptionRow(label) {
  return { key: 'opt-' + (optKey++), label, text: '', images: '' }
}

function imgsHtml(str) {
  return String(str || '').split(',').filter(Boolean).map(u => '<img src="' + u + '" alt="图片"/>').join('')
}

function escHtml(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function splitHtml(html) {
  const imgs = []
  let text = String(html || '')
  text = text.replace(/<img[^>]*src="([^"]+)"[^>]*>/gi, (m, src) => { imgs.push(src); return '' })
  text = text.replace(/<br\s*\/?>/gi, '\n')
  text = text.replace(/<[^>]+>/g, '')
  text = text.replace(/&nbsp;/gi, ' ').replace(/&amp;/gi, '&').replace(/&lt;/gi, '<').replace(/&gt;/gi, '>')
  return { text: text.trim(), images: imgs.join(',') }
}

function paperTitleOf(pid) {
  const p = papers.value.find(x => x.id === pid)
  return p ? p.title : ''
}

function plainText(html) {
  const div = document.createElement('div')
  div.innerHTML = html || ''
  return div.textContent.trim().slice(0, 60)
}

async function getList() {
  loading.value = true
  try {
    const res = await questionPage(query.value)
    list.value = res.rows || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function onPagination(p) {
  query.value.pageNum = p.page
  query.value.pageSize = p.limit
  getList()
}

async function openEdit(row) {
  let materialText = ''
  let materialImages = ''
  if (row.materialId) {
    try {
      const mat = await getMaterial(row.materialId)
      const sp = splitHtml(mat.content)
      materialText = sp.text
      materialImages = sp.images
    } catch (e) { /* ignore */ }
  }
  const stem = splitHtml(row.stem)
  const ana = splitHtml(row.analysis)
  let optionRows = []
  try {
    const list = JSON.parse(row.options || '[]')
    optionRows = list.map(o => {
      const sp = splitHtml(o.html)
      return { key: 'opt-' + (optKey++), label: o.label, text: sp.text, images: sp.images }
    })
  } catch (e) {
    optionRows = []
  }
  editForm.value = {
    id: row.id, paperId: row.paperId, materialId: row.materialId || undefined,
    section: row.section || '', qno: row.qno,
    stem: stem.text, materialText: materialText, materialImages: materialImages,
    stemImages: stem.images, optionRows: optionRows,
    answer: row.answer || '', analysis: ana.text, analysisImages: ana.images,
    newPaperYear: new Date().getFullYear(), newPaperSubject: '行测', newPaperVersion: '自定义'
  }
  editVisible.value = true
}

function openAdd() {
  editForm.value = {
    id: undefined, paperId: undefined, section: undefined, qno: undefined,
    stem: '', materialText: '', materialImages: '', stemImages: '',
    optionRows: ['A', 'B', 'C', 'D'].map(newOptionRow),
    answer: '', analysis: '', analysisImages: '',
    newPaperYear: new Date().getFullYear(), newPaperSubject: '行测', newPaperVersion: '自定义'
  }
  editVisible.value = true
}

function addOption() {
  const labels = 'ABCDEFGH'
  const used = editForm.value.optionRows.map(r => r.label)
  const next = labels.split('').find(l => !used.includes(l))
  if (next) editForm.value.optionRows.push(newOptionRow(next))
}

function removeOption(i) {
  editForm.value.optionRows.splice(i, 1)
}

async function submitEdit() {
  const stemHtml = '<p>' + escHtml(editForm.value.stem).replace(/\n/g, '<br/>') + '</p>' + imgsHtml(editForm.value.stemImages)
  const options = editForm.value.optionRows
    .filter(o => o.text.trim() || o.images)
    .map(o => ({ label: o.label, html: escHtml(o.text).replace(/\n/g, '<br/>') + imgsHtml(o.images) }))
  const materialText = editForm.value.materialText.trim()
  const materialContent = (materialText || editForm.value.materialImages)
    ? '<p>' + escHtml(materialText).replace(/\n/g, '<br/>') + '</p>' + imgsHtml(editForm.value.materialImages)
    : ''
  const analysis = escHtml(editForm.value.analysis).replace(/\n/g, '<br/>') + imgsHtml(editForm.value.analysisImages)

  if (editForm.value.id) {
    await updateQuestion({
      id: editForm.value.id,
      section: editForm.value.section || '',
      stem: stemHtml,
      options: JSON.stringify(options),
      answer: editForm.value.answer || '',
      analysis: analysis,
      materialId: editForm.value.materialId,
      materialContent: materialContent,
      materialTitle: ''
    })
    ElMessage.success('已保存')
  } else {
    let paperId = editForm.value.paperId
    if (typeof paperId === 'string' && paperId.trim()) {
      // 自定义新试卷：先创建
      const newId = await addPaper({
        title: paperId.trim(),
        year: editForm.value.newPaperYear,
        subject: editForm.value.newPaperSubject,
        version: editForm.value.newPaperVersion
      })
      paperId = newId
      papers.value = await listPapers({})
    }
    if (!paperId) {
      ElMessage.warning('请选择或输入所属试卷')
      return
    }
    if (!editForm.value.stem.trim()) {
      ElMessage.warning('请填写题干')
      return
    }
    await addQuestion({
      paperId: paperId,
      section: editForm.value.section || '',
      qno: editForm.value.qno || undefined,
      stem: stemHtml,
      options: JSON.stringify(options),
      answer: editForm.value.answer || '',
      analysis: analysis,
      materialContent: materialContent,
      materialTitle: ''
    })
    ElMessage.success('已新增')
  }
  editVisible.value = false
  getList()
}

onMounted(async () => {
  papers.value = await listPapers({})
  getList()
})
</script>

<style scoped>
.edit-stem {
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 10px;
  line-height: 1.8;
  font-size: 14px;
}
.edit-stem :deep(img) { max-width: 100%; }
.tip-text { margin-left: 8px; color: var(--el-text-color-secondary); font-size: 12px; }
.field-col { width: 100%; display: flex; flex-direction: column; gap: 6px; }
.opt-list { width: 100%; display: flex; flex-direction: column; gap: 8px; }
.opt-row { display: flex; align-items: center; gap: 8px; }
.opt-letter { flex-shrink: 0; width: 24px; height: 24px; border-radius: 50%; background: var(--el-color-primary-light-8); display: flex; align-items: center; justify-content: center; font-weight: 700; }
.new-paper-box { width: 100%; margin-top: 6px; display: flex; flex-direction: column; gap: 6px; }
.new-paper-row { display: flex; gap: 8px; }
</style>
