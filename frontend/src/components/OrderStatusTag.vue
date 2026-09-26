<template>
  <el-tag :type="meta.type" effect="light" size="small">{{ meta.label }}</el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: '' },
})

const MAP = {
  TICKETED: { type: 'warning', label: '已出票' },
  DONE: { type: 'success', label: '已完成' },
  CANCELLED: { type: 'info', label: '已取消' },
}

const meta = computed(() => MAP[props.status] || { type: 'info', label: props.status })
</script>
