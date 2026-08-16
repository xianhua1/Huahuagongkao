<template>
  <div class="tab">
    <PageHead icon="collection" title="申论素材库" desc="金句 + 事例 + 高分范文（含亮点解析），按主题分类；还有大作文模板。" />
<div class="theme-tabs">
      <div
        v-for="(th, ti) in sucai"
        :key="ti"
        class="theme-tab"
        :class="{ active: theme === ti }"
        @click="theme = ti"
      >
        {{ th.t }}
      </div>
      <div class="theme-tab" :class="{ active: theme === sucai.length + 1 }" @click="theme = sucai.length + 1">
        🧩 万能模板
      </div>
      <div class="theme-tab" :class="{ active: theme === sucai.length }" @click="theme = sucai.length">
        📝 大作文
      </div>
    </div>

    <!-- 万能模板 -->
    <template v-if="theme === sucai.length + 1">
      <div class="block">
        <div class="block-title">🧩 申论万能模板（{{ moban.length }} 篇 · 换掉【主题词】就是一篇完整的申论）</div>
        <p class="mb-tip">用法：选一篇最接近考点的模板 → 把【】里的主题词替换成材料主题 → 开头/分论点/结尾的句式框架原样保留 → 30 分钟出一篇结构完整的文章。</p>
        <div v-for="(m, i) in moban" :key="i" class="fw-card">
          <div class="fw-head" @click="toggleMoban(i)">
            <el-icon :class="{ open: openMoban.includes(i) }"><ArrowRight /></el-icon>
            <span class="fw-title">{{ m.name }}</span>
            <el-tag size="small" type="warning">{{ m.fit.split('：')[1] || '通用' }}</el-tag>
          </div>
          <div v-show="openMoban.includes(i)" class="fw-body">
            <div class="mb-row"><span class="mb-label">标题</span><span class="mb-text">《{{ m.title }}》</span></div>
            <div class="mb-row"><span class="mb-label">可选标题</span><span class="mb-text">{{ m.titleAlt }}</span></div>
            <div class="mb-row"><span class="mb-label">开头</span><span class="mb-text">{{ m.head }}</span></div>
            <div class="mb-row"><span class="mb-label">分论点</span>
              <div class="mb-points">
                <div v-for="(p, pi) in m.points" :key="pi" class="mb-point">【{{ pi + 1 }}】{{ p }}</div>
              </div>
            </div>
            <div class="mb-row"><span class="mb-label">结尾</span><span class="mb-text">{{ m.tail }}</span></div>
            <div class="mb-row tip"><span class="mb-label">替换说明</span><span class="mb-text">{{ m.tip }}</span></div>
          </div>
        </div>
      </div>
    </template>

    <!-- 主题素材 -->
    <template v-if="theme < sucai.length">
      <div class="block">
        <div class="block-title">✨ 金句（可直接引用）</div>
        <div v-for="(j, i) in sucai[theme].jq" :key="i" class="jq-item">
          <span class="jq-num">{{ i + 1 }}</span>
          <span class="jq-text">"{{ j }}"</span>
        </div>
      </div>
      <div class="block">
        <div class="block-title">🌟 事例（用于论证）</div>
        <div v-for="(s, i) in sucai[theme].sj" :key="i" class="sj-item">
          <div class="sj-name">{{ s.name }}</div>
          <div class="sj-detail">{{ s.detail }}</div>
        </div>
      </div>
      <div class="block use-box">
        <div class="block-title">💡 运用提示</div>
        <div class="use-text">{{ sucai[theme].use }}</div>
      </div>

      <!-- 高分范文 -->
      <div class="block">
        <div class="block-title">🏆 高分范文（{{ currentFanwen.length }} 篇 · 含亮点解析）</div>
        <div v-for="(fw, i) in currentFanwen" :key="i" class="fw-card">
          <div class="fw-head" @click="toggleFanwen(i)">
            <el-icon :class="{ open: openFanwen.includes(i) }"><ArrowRight /></el-icon>
            <span class="fw-title">范文 {{ i + 1 }}：{{ fw.title }}</span>
            <el-tag size="small" type="success">高分示范</el-tag>
          </div>
          <div v-show="openFanwen.includes(i)" class="fw-body">
            <div class="fw-text">{{ fw.body }}</div>
            <div class="fw-points-title">📌 好在哪里（写作技法解析）</div>
            <div v-for="(p, pi) in fw.points" :key="pi" class="fw-point">
              <span class="fp-w">{{ p.w }}</span>
              <span class="fp-y">{{ p.y }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 大作文 -->
    <template v-if="theme === sucai.length">
      <div class="block" v-for="(p, i) in dazuwen.parts" :key="i">
        <div class="block-title">{{ p.name }}</div>
        <div class="use-text">{{ p.tips }}</div>
      </div>
      <div class="block">
        <div class="block-title">📄 范文骨架</div>
        <div v-for="(f, i) in dazuwen.fanwen" :key="i" class="fw-item">
          <div class="sj-name">{{ f.title }}</div>
          <div class="sj-detail">{{ f.structure }}</div>
        </div>
      </div>
    </template>

    <!-- 参考资源 -->
    <div class="ref-box">
      <div class="block-title">🔗 更多范文参考（机构网站公开资源）</div>
      <a href="https://m.qh.huatu.com/2024/1216/1762947.html" target="_blank" rel="noopener">华图教育 · 发挥三治融合之力 擘画社会治理蓝图</a>
      <a href="http://www.offcn.com/scgwy/2023/1030/39261.html" target="_blank" rel="noopener">中公教育 · 推动乡村善治 留住乡土风韵</a>
      <a href="https://www.huatu.com/2023/0505/2645886.html" target="_blank" rel="noopener">华图教育 · 扎根基层 实现乡村振兴</a>
      <a href="https://cq.m.jinbiaochi.com/cqgwy/news_867263.html" target="_blank" rel="noopener">金标尺 · 以"千万工程"经验为引领推进乡村全面振兴</a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
import { sucai, dazuwen } from './data/sucai'
import { fanwen } from './data/fanwen'
import { moban } from './data/moban'
import PageHead from './PageHead.vue'

const theme = ref(0)
const openFanwen = ref([0])
const openMoban = ref([0])

const currentFanwen = computed(() => fanwen[sucai[theme.value].t] || [])

function toggleFanwen(i) {
  openFanwen.value = openFanwen.value.includes(i)
    ? openFanwen.value.filter(x => x !== i)
    : [...openFanwen.value, i]
}
function toggleMoban(i) {
  openMoban.value = openMoban.value.includes(i)
    ? openMoban.value.filter(x => x !== i)
    : [...openMoban.value, i]
}
</script>

<style scoped>
.theme-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.theme-tab {
  padding: 7px 14px; border-radius: 16px; cursor: pointer;
  font-size: 13px; color: var(--el-text-color-regular);
  background: var(--el-fill-color-light);
  transition: all .15s;
}
.theme-tab.active { background: var(--el-color-primary); color: #fff; font-weight: 600; }
.block { margin-bottom: 18px; max-width: 860px; }
.block-title { font-size: 15px; font-weight: 700; color: var(--el-color-primary); margin-bottom: 10px; }
.jq-item {
  display: flex; gap: 10px; align-items: flex-start;
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
  background: var(--el-color-primary-light-9);
}
.jq-num {
  flex-shrink: 0; width: 22px; height: 22px; border-radius: 50%;
  background: var(--el-color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; margin-top: 2px;
}
.jq-text { font-size: 14px; color: var(--el-text-color-primary); line-height: 1.8; }
.sj-item {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
}
.sj-name { font-size: 14px; font-weight: 700; color: var(--el-text-color-primary); margin-bottom: 4px; }
.sj-detail { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.8; }
.use-box { background: var(--el-color-warning-light-9); border: 1px dashed var(--el-color-warning); border-radius: 10px; padding: 14px 16px; }
.use-text { font-size: 14px; color: var(--el-text-color-regular); line-height: 1.9; }
.fw-item { border: 1px solid var(--el-border-color-light); border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; }

/* 范文卡片 */
.fw-card { border: 1px solid var(--el-border-color-light); border-radius: 12px; margin-bottom: 12px; overflow: hidden; }
.fw-head {
  display: flex; align-items: center; gap: 10px;
  padding: 13px 16px; cursor: pointer;
  background: linear-gradient(90deg, var(--el-color-primary-light-9), var(--el-bg-color));
  transition: all .15s;
}
.fw-head:hover { background: var(--el-color-primary-light-8); }
.fw-head .el-icon { transition: transform .2s; color: var(--el-color-primary); }
.fw-head .el-icon.open { transform: rotate(90deg); }
.fw-title { flex: 1; font-size: 14px; font-weight: 700; color: var(--el-text-color-primary); }
.fw-body { padding: 16px 18px; border-top: 1px dashed var(--el-border-color-lighter); }
.fw-text { font-size: 14px; line-height: 2; color: var(--el-text-color-regular); white-space: pre-wrap; }
.fw-points-title { font-size: 13px; font-weight: 700; color: #e6a23c; margin: 14px 0 8px; }
.fw-point {
  display: flex; gap: 10px; align-items: flex-start;
  background: var(--el-color-warning-light-9);
  border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;
}
.fp-w {
  flex-shrink: 0; font-size: 12px; font-weight: 700; color: #fff;
  background: #e6a23c; border-radius: 6px; padding: 2px 8px; margin-top: 2px;
}
.fp-y { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.7; }
.ref-box { margin-top: 24px; border-top: 1px dashed var(--el-border-color); padding-top: 14px; max-width: 860px; }
.ref-box a {
  display: block; font-size: 13px; color: var(--el-color-primary);
  text-decoration: none; margin-bottom: 6px; line-height: 1.7;
}
.ref-box a:hover { text-decoration: underline; }
.mb-tip { font-size: 13px; color: var(--el-text-color-secondary); line-height: 1.8; margin: 0 0 12px; }
.mb-row { display: flex; gap: 12px; margin-bottom: 10px; align-items: flex-start; }
.mb-label {
  flex-shrink: 0; width: 62px; text-align: center;
  font-size: 12px; font-weight: 700; color: #fff;
  background: var(--el-color-primary); border-radius: 6px; padding: 3px 0; margin-top: 3px;
}
.mb-row.tip .mb-label { background: #e6a23c; }
.mb-text { font-size: 14px; color: var(--el-text-color-regular); line-height: 1.9; flex: 1; }
.mb-points { flex: 1; }
.mb-point {
  font-size: 13px; color: var(--el-text-color-regular); line-height: 1.8;
  background: var(--el-fill-color-lighter); border-radius: 8px;
  padding: 8px 12px; margin-bottom: 6px;
}
</style>
