<template>
  <div class="tab">
    <PageHead icon="search" title="词语查询" :desc="`查词库 ${allWords.length} 条：成语 + 高频词语。支持词语、释义、拼音模糊搜索。`" />

    <div class="search-bar">
      <el-input
        v-model="kw" size="large" clearable placeholder="输入词语 / 释义关键词，如：砥砺、团结、dǐ lì…"
        @keyup.enter="doSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
        <template #append><el-button @click="doSearch">查询</el-button></template>
      </el-input>
    </div>

    <div v-if="!searched" class="search-tip">
      <p>💡 试试查询：</p>
      <div class="hot-tags">
        <el-tag v-for="h in hot" :key="h" class="hot-tag" @click="kw = h; doSearch()">{{ h }}</el-tag>
      </div>
    </div>

    <template v-else>
      <div v-if="!results.length" class="empty-tip">
        <p>没有找到匹配「{{ kw }}」的词条，换个关键词试试。</p>
      </div>
      <div v-for="(r, i) in results" :key="i" class="cy-card">
        <div class="cy-main">
          <span class="cy-word">{{ r[0] }}</span>
          <span class="cy-py">{{ r[1] }}</span>
          <el-tag v-if="r[4]" size="small" :type="tagType(r[4])">{{ tagText(r[4]) }}</el-tag>
          <el-button size="small" text type="primary" class="cy-add" @click="collect(r)">+ 生词锦囊</el-button>
        </div>
        <div class="cy-meaning">{{ r[2] }}</div>
        <div v-if="r[3]" class="cy-example">例句：{{ r[3] }}</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import useUserStore from '@/store/modules/user'
import { chengyu } from './data/chengyu'
import { words } from './data/words'
import { load, save } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

// chengyu 数据为 5 列 [词, 拼音, 释义, 例句, 分类]，words 为 4 列
const allWords = computed(() => [
  ...chengyu.map(x => [x[0], x[1], x[2], x[3], x[4] || 'gao']),
  ...words.map(x => [x[0], x[1], x[2], x[3], 'gao'])
])

const kw = ref('')
const searched = ref(false)
const results = ref([])
const hot = ['砥砺前行', '踔厉奋发', '未雨绸缪', '相辅相成', '推陈出新', '相得益彰']

function doSearch() {
  const k = kw.value.trim()
  searched.value = true
  if (!k) {
    results.value = []
    return
  }
  results.value = allWords.value.filter(x =>
    x[0].includes(k) || x[1].replace(/\s/g, '').includes(k.replace(/\s/g, '')) || x[2].includes(k)
  )
}

function tagType(t) {
  return t === 'yicuo' ? 'danger' : t === 'bianxi' ? 'warning' : 'success'
}
function tagText(t) {
  return t === 'yicuo' ? '易错' : t === 'bianxi' ? '辨析' : '高频'
}
function collect(item) {
  const list = load(uid.value, 'mywords', [])
  if (!list.some(x => x[0] === item[0])) {
    list.push([item[0], item[1], item[2], item[3], false])
    save(uid.value, 'mywords', list)
    ElMessage.success('已加入生词锦囊')
  } else {
    ElMessage.info('已在生词锦囊中')
  }
}
</script>

<style scoped>
.search-bar { margin: 6px 0 16px; max-width: 560px; }
.search-tip { text-align: center; padding: 40px 0 60px; color: var(--el-text-color-secondary); }
.hot-tags { margin-top: 14px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
.hot-tag { cursor: pointer; }
.empty-tip { text-align: center; padding: 40px 0; color: var(--el-text-color-secondary); }
.cy-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 10px;
}
.cy-main { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cy-word { font-size: 17px; font-weight: 700; color: var(--el-color-primary); }
.cy-py { font-size: 12px; color: var(--el-text-color-secondary); }
.cy-add { margin-left: auto; }
.cy-meaning { font-size: 14px; color: var(--el-text-color-primary); margin-top: 6px; line-height: 1.7; }
.cy-example { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 4px; line-height: 1.7; }
</style>
