<template>
  <div class="tab">
    <PageHead icon="bookmark" title="生词锦囊" desc="收藏易混易错的生词，随时翻看复习。学完一个就标记「已掌握」。自己也可以添加生词。" />

    <div class="search-bar">
      <el-input v-model="kw" placeholder="搜索生词…" size="small" clearable style="width: 220px" />
      <el-button size="small" type="primary" @click="dialogVisible = true">+ 添加生词</el-button>
      <el-button size="small" type="danger" plain @click="clearAll">清空锦囊</el-button>
    </div>

    <div v-if="!list.length" class="empty-tip">
      <p>📌 锦囊还是空的。<br />在「高频词语」「词语辨析」里点「+ 加入生词锦囊」，或手动添加生词。</p>
    </div>

    <div v-for="(item, i) in filtered" :key="i" class="cy-card" :class="{ known: item.known }">
      <div class="cy-main">
        <span class="cy-word">{{ item[0] }}</span>
        <span class="cy-py">{{ item[1] || '' }}</span>
        <div class="cy-ops">
          <el-button
            size="small" text :type="item.known ? 'success' : 'primary'"
            @click="toggleKnown(i)"
          >{{ item.known ? '✓ 已掌握' : '标记掌握' }}</el-button>
          <el-button size="small" text type="danger" @click="removeAt(i)">删除</el-button>
        </div>
      </div>
      <div class="cy-meaning">{{ item[2] }}</div>
      <div v-if="item[3]" class="cy-example">例句：{{ item[3] }}</div>
    </div>

    <el-dialog v-model="dialogVisible" title="添加生词" width="420px">
      <el-form label-width="70px">
        <el-form-item label="词语"><el-input v-model="newWord" placeholder="如：勠力同心" /></el-form-item>
        <el-form-item label="拼音"><el-input v-model="newPy" placeholder="如：lù lì tóng xīn" /></el-form-item>
        <el-form-item label="释义"><el-input v-model="newMean" type="textarea" :rows="2" placeholder="释义" /></el-form-item>
        <el-form-item label="例句"><el-input v-model="newEx" type="textarea" :rows="2" placeholder="例句（可选）" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button size="small" @click="dialogVisible = false">取消</el-button>
        <el-button size="small" type="primary" @click="addWord">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import useUserStore from '@/store/modules/user'
import { load, save } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

// list 项：[word, py, meaning, example, known]
const list = ref([])
const kw = ref('')
const dialogVisible = ref(false)
const newWord = ref('')
const newPy = ref('')
const newMean = ref('')
const newEx = ref('')

const filtered = computed(() => {
  const k = kw.value.trim()
  if (!k) return list.value
  return list.value.filter(x => (x[0] + x[2]).includes(k))
})

function persist() {
  save(uid.value, 'mywords', list.value)
}
function toggleKnown(i) {
  list.value[i].known = !list.value[i].known
  persist()
}
function removeAt(i) {
  list.value.splice(i, 1)
  persist()
}
function clearAll() {
  ElMessageBox.confirm('确定清空整个生词锦囊吗？此操作不可恢复。', '提示', { type: 'warning' })
    .then(() => {
      list.value = []
      persist()
    })
    .catch(() => {})
}
function addWord() {
  const w = newWord.value.trim()
  if (!w || !newMean.value.trim()) {
    ElMessage.warning('词语和释义不能为空')
    return
  }
  list.value.push([w, newPy.value.trim(), newMean.value.trim(), newEx.value.trim(), false])
  persist()
  newWord.value = newPy.value = newMean.value = newEx.value = ''
  dialogVisible.value = false
  ElMessage.success('已添加')
}

onMounted(() => {
  list.value = load(uid.value, 'mywords', [])
})
</script>

<style scoped>
.search-bar { display: flex; gap: 12px; align-items: center; margin: 6px 0 14px; flex-wrap: wrap; }
.cy-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 10px;
}
.cy-card.known { opacity: .6; background: var(--el-fill-color-lighter); }
.cy-main { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cy-word { font-size: 17px; font-weight: 700; color: var(--el-color-primary); }
.cy-py { font-size: 12px; color: var(--el-text-color-secondary); }
.cy-ops { margin-left: auto; }
.cy-meaning { font-size: 14px; color: var(--el-text-color-primary); margin-top: 6px; line-height: 1.7; }
.cy-example { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 4px; line-height: 1.7; }
.empty-tip { text-align: center; padding: 50px 0; color: var(--el-text-color-secondary); line-height: 2; }
</style>
