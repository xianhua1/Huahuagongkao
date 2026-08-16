<template>
  <div class="page-head">
    <span class="ph-deco d1"></span>
    <span class="ph-deco d2"></span>
    <span class="ph-deco d3"></span>
    <div class="ph-icon"><el-icon :size="26"><component :is="iconComp" /></el-icon></div>
    <div class="ph-text">
      <div class="ph-title">{{ title }}</div>
      <div class="ph-desc">{{ desc }}</div>
    </div>
    <div class="ph-extra"><slot /></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { EditPen, Calendar, Reading, Notebook, Clock, Tickets, Collection, TrendCharts } from '@element-plus/icons-vue'

const props = defineProps({
  icon: { type: String, default: 'edit' },
  title: { type: String, required: true },
  desc: { type: String, default: '' }
})

const ICONS = {
  edit: EditPen,
  calendar: Calendar,
  reading: Reading,
  notebook: Notebook,
  clock: Clock,
  tickets: Tickets,
  collection: Collection,
  trend: TrendCharts
}
const iconComp = computed(() => ICONS[props.icon] || EditPen)
</script>

<style scoped>
.page-head {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px 26px;
  border-radius: 16px;
  margin-bottom: 20px;
  overflow: hidden;
  color: #fff;
  background: linear-gradient(120deg, #409eff 0%, #36cfc9 55%, #3fb68b 100%);
  box-shadow: 0 6px 18px rgba(64, 158, 255, .28);
}
.ph-icon {
  flex-shrink: 0;
  width: 54px; height: 54px;
  border-radius: 16px;
  background: rgba(255, 255, 255, .22);
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}
.ph-text { flex: 1; min-width: 0; }
.ph-title { font-size: 22px; font-weight: 800; letter-spacing: 1px; text-shadow: 0 1px 4px rgba(0, 0, 0, .12); }
.ph-desc { font-size: 13px; margin-top: 5px; opacity: .92; line-height: 1.6; }
.ph-extra { flex-shrink: 0; }
.ph-deco { position: absolute; border-radius: 50%; background: rgba(255, 255, 255, .14); pointer-events: none; }
.ph-deco.d1 { width: 130px; height: 130px; right: -30px; top: -50px; }
.ph-deco.d2 { width: 70px; height: 70px; right: 120px; bottom: -30px; }
.ph-deco.d3 { width: 34px; height: 34px; right: 240px; top: 12px; }
@media (max-width: 700px) {
  .page-head { flex-wrap: wrap; padding: 16px 18px; }
  .ph-extra { width: 100%; }
}
</style>
