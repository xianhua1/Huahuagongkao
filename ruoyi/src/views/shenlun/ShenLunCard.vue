<template>
  <div class="answer-card">
    <div class="grid-container">
      <div
        v-for="i in size"
        :key="i"
        class="cell"
        :class="{ active: cursorIndex === i - 1 }"
        @click="moveCursor(i - 1)"
      >
        <span>{{ displayChar(chars[i - 1]) }}</span>
        <span v-if="cursorIndex === i - 1" class="cursor"></span>
      </div>
    </div>
    <div class="mark-column">
      <div v-for="m in marks" :key="m" class="mark" :style="{ top: (m / PER_ROW) * ROW_H + 'px' }">▲{{ m }}</div>
    </div>
    <!-- 隐藏输入区：支持中文输入法合成事件 -->
    <textarea
      ref="inputArea"
      class="hidden-input"
      @compositionstart="onCompStart"
      @compositionend="onCompEnd"
      @input="onInput"
      @keydown="onKey"
    ></textarea>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  wordLimit: { type: Number, default: 400 }
})
const emit = defineEmits(['update:modelValue'])

const PER_ROW = 20
const CELL = 36
const GAP = 2
const ROW_H = CELL + GAP

const inputArea = ref(null)
const cursorIndex = ref(0)
let composing = false

const size = computed(() => {
  const lim = props.wordLimit || 400
  return Math.max(PER_ROW, Math.ceil(lim / PER_ROW) * PER_ROW)
})
const marks = computed(() => {
  const arr = []
  for (let m = 100; m <= size.value; m += 100) arr.push(m)
  return arr
})
const chars = computed(() => {
  const s = String(props.modelValue || '')
  const arr = []
  for (let i = 0; i < size.value; i++) arr.push(s[i] || '')
  return arr
})

// 空格在 HTML 中会被折叠，用不换行空格占位显示（中文段落首行空两格场景）
function displayChar(c) {
  if (c === ' ') return '\u00A0'
  return c || ''
}

function insert(str) {
  const s = String(props.modelValue || '')
  const max = size.value
  if (s.length >= max || !str) return
  const left = s.slice(0, cursorIndex.value)
  const right = s.slice(cursorIndex.value)
  const next = (left + str + right).slice(0, max)
  cursorIndex.value = Math.min(cursorIndex.value + str.length, max)
  emit('update:modelValue', next)
}

function focusInput() {
  if (inputArea.value) inputArea.value.focus()
}

function moveCursor(i) {
  cursorIndex.value = Math.max(0, Math.min(i, size.value - 1))
  focusInput()
}

function onCompStart() {
  composing = true
}
function onCompEnd(e) {
  composing = false
  if (e.data) insert(e.data)
  if (inputArea.value) inputArea.value.value = ''
}
function onInput(e) {
  if (composing) return
  const val = inputArea.value ? inputArea.value.value : e.target.value
  if (val) {
    insert(val)
    if (inputArea.value) inputArea.value.value = ''
  }
}
function onKey(e) {
  if (composing) return
  const s = String(props.modelValue || '')
  // 显式拦截空格键：直接插入空格（中文段落首行空两格），并阻止页面默认滚动
  if (e.key === ' ') {
    e.preventDefault()
    insert(' ')
    return
  }
  switch (e.key) {
    case 'Backspace':
      if (cursorIndex.value > 0) {
        const next = s.slice(0, cursorIndex.value - 1) + s.slice(cursorIndex.value)
        cursorIndex.value--
        emit('update:modelValue', next)
      }
      e.preventDefault()
      break
    case 'Delete':
      if (cursorIndex.value < s.length) {
        const next = s.slice(0, cursorIndex.value) + s.slice(cursorIndex.value + 1)
        emit('update:modelValue', next)
      }
      e.preventDefault()
      break
    case 'ArrowLeft':
      if (cursorIndex.value > 0) {
        cursorIndex.value--
      }
      e.preventDefault()
      break
    case 'ArrowRight':
      if (cursorIndex.value < Math.min(s.length, size.value - 1)) {
        cursorIndex.value++
      }
      e.preventDefault()
      break
  }
}
</script>

<style scoped>
.answer-card {
  display: flex;
  background: #fff;
  border: 2px solid #666;
  border-radius: 4px;
  padding: 14px;
  max-width: 100%;
  overflow-x: auto;
  position: relative;
}
.grid-container {
  display: grid;
  grid-template-columns: repeat(20, 36px);
  gap: 2px;
}
.cell {
  width: 36px;
  height: 36px;
  border: 1px solid #888;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-family: "SimSun", "宋体", serif;
  position: relative;
  cursor: text;
  user-select: none;
  color: #333;
}
.cell.active { background: #eaf3ff; }
.cursor {
  position: absolute;
  left: 50%;
  top: 4px;
  width: 2px;
  height: 26px;
  background: #000;
  animation: blink 1s step-end infinite;
  pointer-events: none;
}
@keyframes blink { 50% { opacity: 0; } }
.mark-column {
  width: 46px;
  margin-left: 8px;
  position: relative;
  flex-shrink: 0;
}
.mark {
  position: absolute;
  color: #444;
  font-size: 13px;
  white-space: nowrap;
}
.hidden-input {
  position: absolute;
  left: -9999px;
  top: 0;
  width: 1px;
  height: 1px;
  border: none;
  outline: none;
  background: transparent;
}
</style>
