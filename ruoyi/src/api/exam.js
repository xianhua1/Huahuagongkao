import request from '@/utils/request'

// 首页统计
export function dashboardStats() {
  return request({ url: '/exam/dashboard', method: 'get' }).then(res => res.data)
}

// 试卷列表
export function listPapers(data) {
  return request({ url: '/exam/paper/list', method: 'get', params: data }).then(res => res.data)
}

// 试卷详情（含材料与题目）
export function getPaperDetail(paperId) {
  return request({ url: '/exam/paper/' + paperId, method: 'get' }).then(res => res.data)
}

// 试卷管理分页（返回 {rows, total}）
export function paperPage(data) {
  return request({ url: '/exam/paper/page', method: 'get', params: data })
}

// 题目管理分页（返回 {rows, total}）
export function questionPage(data) {
  return request({ url: '/exam/question/page', method: 'get', params: data })
}

// 单题详情
export function getQuestion(questionId) {
  return request({ url: '/exam/question/' + questionId, method: 'get' }).then(res => res.data)
}

// 材料详情
export function getMaterial(materialId) {
  return request({ url: '/exam/material/' + materialId, method: 'get' }).then(res => res.data)
}

// 修改题目
export function updateQuestion(data) {
  return request({ url: '/exam/question', method: 'put', data }).then(res => res.data)
}

// 新增题目
export function addQuestion(data) {
  return request({ url: '/exam/question', method: 'post', data }).then(res => res.data)
}

// 新增试卷（自定义卷）
export function addPaper(data) {
  return request({ url: '/exam/paper', method: 'post', data }).then(res => res.data)
}

// 随机刷题
export function randomQuestions(data) {
  return request({ url: '/exam/random', method: 'get', params: data }).then(res => res.data)
}

// 提交答案
export function saveRecord(data) {
  return request({ url: '/exam/record/save', method: 'post', data }).then(res => res.data)
}

// 某卷答题统计
export function recordStats(paperId) {
  return request({ url: '/exam/record/stats', method: 'get', params: { paperId } }).then(res => res.data)
}

// 某卷已答记录
export function recordAnswered(paperId) {
  return request({ url: '/exam/record/answered', method: 'get', params: { paperId } }).then(res => res.data)
}

// 错题本
export function wrongList() {
  return request({ url: '/exam/record/wrong', method: 'get' }).then(res => res.data)
}

// 移出错题本
export function removeRecord(questionId) {
  return request({ url: '/exam/record/' + questionId, method: 'delete' }).then(res => res.data)
}

// 清空错题本
export function clearWrongRecords() {
  return request({ url: '/exam/record/wrong', method: 'delete' }).then(res => res.data)
}
