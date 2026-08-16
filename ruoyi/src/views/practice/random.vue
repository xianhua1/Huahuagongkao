<template>
  <div class="app-container random-page">
    <el-card shadow="never" style="max-width: 560px; margin: 40px auto;">
      <h2 class="random-title">随机练习</h2>
      <p class="random-desc">按题型随机抽取历年真题进行练习，做完即出答案与解析</p>
      <el-form label-width="80px">
        <el-form-item label="题型">
          <el-select v-model="section" style="width: 100%">
            <el-option label="全部题型（混刷）" value="" />
            <el-option v-for="s in sections" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="题量">
          <el-radio-group v-model="count">
            <el-radio-button :value="10">10 题</el-radio-button>
            <el-radio-button :value="20">20 题</el-radio-button>
            <el-radio-button :value="30">30 题</el-radio-button>
            <el-radio-button :value="50">50 题</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" @click="start">
            开始练习
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const section = ref('')
const count = ref(10)
const sections = ['常识判断', '言语理解与表达', '数量关系', '判断推理', '资料分析']

function start() {
  router.push({
    path: '/practice/session',
    query: { mode: 'random', section: section.value, count: count.value }
  })
}
</script>

<style scoped>
.random-title { text-align: center; margin: 0 0 6px; }
.random-desc { text-align: center; color: var(--el-text-color-secondary); font-size: 13px; margin-bottom: 26px; }
</style>
