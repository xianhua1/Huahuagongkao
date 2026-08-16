<template>
  <div class="app-container">
    <el-card shadow="never">
      <el-form :model="query" inline>
        <el-form-item label="标题">
          <el-input v-model="query.title" placeholder="搜索试卷" clearable style="width: 260px" @keyup.enter="getList" />
        </el-form-item>
        <el-form-item label="年份">
          <el-select v-model="query.year" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="y in years" :key="y" :label="y" :value="y" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getList">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="list">
        <el-table-column label="ID" prop="id" width="70" align="center" />
        <el-table-column label="卷代码" prop="paperCode" width="110" align="center" />
        <el-table-column label="试卷标题" prop="title" min-width="320" show-overflow-tooltip />
        <el-table-column label="年份" prop="year" width="80" align="center" />
        <el-table-column label="版本" prop="version" width="110" align="center" />
        <el-table-column label="题数" prop="questionCount" width="80" align="center" />
      </el-table>

      <pagination
        v-show="total > 0"
        :total="total"
        v-model:page="query.pageNum"
        v-model:limit="query.pageSize"
        @pagination="onPagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { paperPage } from '@/api/exam'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = ref({ title: undefined, year: undefined, pageNum: 1, pageSize: 10 })
const years = Array.from({ length: 23 }, (_, i) => 2000 + i)

async function getList() {
  loading.value = true
  try {
    const res = await paperPage(query.value)
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

onMounted(getList)
</script>
