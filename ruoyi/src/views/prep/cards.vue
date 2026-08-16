<template>
  <div class="tab">
    <PageHead icon="tickets" title="速记卡片" desc="公式、口诀、考点闪卡：先想答案，再点卡片翻面核对。" />
<div class="card-bar">
      <el-select v-model="cat" size="small" style="width: 160px">
        <el-option label="全部分类" value="all" />
        <el-option v-for="c in cats" :key="c" :label="c" :value="c" />
      </el-select>
      <el-button size="small" @click="shuffleCards">🔀 打乱顺序</el-button>
      <el-button size="small" type="primary" plain @click="resetKnown">重置进度</el-button>
      <span class="card-hint">点击卡片翻面查看答案</span>
    </div>

    <div class="card-grid">
      <div
        v-for="(card, i) in displayCards"
        :key="i"
        class="flash"
        :class="{ flipped: flipped.has(i), known: known.has(cardKey(card)) }"
        @click="flip(i)"
      >
        <div class="flash-inner">
          <div class="flash-face flash-front">
            <div class="flash-cat">{{ card.c }}</div>
            <div class="flash-q">{{ card.f }}</div>
            <div class="flash-hint">点我翻面</div>
          </div>
          <div class="flash-face flash-back">
            <div class="flash-a">{{ card.b }}</div>
            <div class="flash-btns" @click.stop>
              <el-button size="small" type="success" plain @click="markKnown(card, true)">✓ 认识</el-button>
              <el-button size="small" @click="markKnown(card, false)">✗ 不认识</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!displayCards.length" class="empty-tip">该分类暂无卡片</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import useUserStore from '@/store/modules/user'
import { cards } from './data/cards'
import { load, save } from './store'
import PageHead from './PageHead.vue'

const userStore = useUserStore()
const uid = computed(() => userStore.userId || 'guest')

const cat = ref('all')
const known = ref(new Set())
const flipped = ref(new Set())
const shuffled = ref(null)

const cats = computed(() => [...new Set(cards.map(c => c.c))])
const filtered = computed(() => (cat.value === 'all' ? cards : cards.filter(c => c.c === cat.value)))
const displayCards = computed(() => {
  if (cat.value !== 'all' || !shuffled.value) return filtered.value
  return shuffled.value
})
const knownPct = computed(() => {
  const total = cards.length
  return total ? Math.round(known.value.size / total * 100) : 0
})

function cardKey(c) {
  return c.c + '|' + c.f
}
function flip(i) {
  const s = new Set(flipped.value)
  if (s.has(i)) s.delete(i)
  else s.add(i)
  flipped.value = s
}
function markKnown(card, isKnown) {
  const s = new Set(known.value)
  if (isKnown) s.add(cardKey(card))
  else s.delete(cardKey(card))
  known.value = s
  save(uid.value, 'cardKnown', [...s])
}
function shuffleCards() {
  const arr = [...cards]
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  shuffled.value = arr
  flipped.value = new Set()
  cat.value = 'all'
}
function resetKnown() {
  known.value = new Set()
  save(uid.value, 'cardKnown', [])
}

onMounted(() => {
  known.value = new Set(load(uid.value, 'cardKnown', []))
})
</script>

<style scoped>
.card-bar { display: flex; align-items: center; gap: 10px; margin: 12px 0 16px; flex-wrap: wrap; }
.card-hint { font-size: 12px; color: var(--el-text-color-secondary); }
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 14px;
}
.flash { perspective: 1000px; height: 190px; cursor: pointer; }
.flash-inner {
  position: relative; width: 100%; height: 100%;
  transition: transform .35s;
  transform-style: preserve-3d;
}
.flash.flipped .flash-inner { transform: rotateY(180deg); }
.flash-face {
  position: absolute; inset: 0;
  backface-visibility: hidden;
  border-radius: 12px;
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
  padding: 14px; text-align: center;
  border: 1px solid var(--el-border-color-light);
}
.flash-front {
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-bg-color));
}
.flash-back {
  background: var(--el-color-primary);
  color: #fff;
  transform: rotateY(180deg);
}
.flash-cat {
  position: absolute; top: 10px; left: 12px;
  font-size: 11px; color: var(--el-color-primary);
  background: var(--el-bg-color);
  border-radius: 8px; padding: 1px 8px;
}
.flash-q { font-size: 14px; font-weight: 600; color: var(--el-text-color-primary); line-height: 1.7; }
.flash-hint { position: absolute; bottom: 10px; font-size: 11px; color: var(--el-text-color-placeholder); }
.flash-a { font-size: 14px; line-height: 1.8; font-weight: 600; }
.flash-btns { display: flex; gap: 8px; margin-top: 12px; }
.flash-btns .el-button { background: rgba(255,255,255,.15); border-color: rgba(255,255,255,.4); color: #fff; }
.flash.known .flash-front { opacity: .55; }
.empty-tip { text-align: center; padding: 50px 0; color: var(--el-text-color-secondary); }
</style>
