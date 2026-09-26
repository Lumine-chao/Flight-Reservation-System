<template>
  <el-form label-width="90px" class="passenger-form">
    <el-form-item label="航班">
      <div class="flight-info" v-if="flight">
        <span class="flight-no">{{ flight.flightNo }}</span>
        <span>{{ flight.airline }}</span>
        <span>{{ flight.departTime }} → {{ flight.arriveTime }}</span>
      </div>
    </el-form-item>
    <el-form-item label="舱位">
      <el-radio-group v-model="seatClass" @change="emit('change')">
        <el-radio v-for="s in SEAT_CLASSES" :key="s.value" :value="s.value">
          {{ s.label }} ¥{{ priceOf(s.value) }}
        </el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="机票数">
      <el-input-number v-model="ticketCount" :min="1" :max="9" @change="emit('change')" />
      <span class="hint">单次最多9张</span>
    </el-form-item>
    <el-form-item label="乘机人姓名">
      <el-input
        v-model="passengerName"
        placeholder="请输入乘机人姓名"
        style="width: 220px"
        maxlength="64"
        @input="emit('change')"
      />
    </el-form-item>
    <el-form-item label="总计">
      <span class="total-price">¥{{ totalPrice }}</span>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { computed } from 'vue'

import { SEAT_CLASSES } from '@/utils/constants'

const props = defineProps({
  flight: { type: Object, default: null },
})

const emit = defineEmits(['change'])

const seatClass = defineModel('seatClass', { default: 'ECONOMY' })
const ticketCount = defineModel('ticketCount', { default: 1 })
const passengerName = defineModel('passengerName', { default: '' })

function priceOf(value) {
  if (!props.flight) return 0
  const map = { ECONOMY: 'priceEconomy', BUSINESS: 'priceBusiness', FIRST: 'priceFirst' }
  return Number(props.flight[map[value]] || 0).toFixed(0)
}

const totalPrice = computed(() => {
  if (!props.flight) return '0'
  const map = { ECONOMY: 'priceEconomy', BUSINESS: 'priceBusiness', FIRST: 'priceFirst' }
  const unit = Number(props.flight[map[seatClass.value]] || 0)
  return (unit * ticketCount.value).toFixed(2)
})

defineExpose({ priceOf })
</script>

<style scoped>
.flight-info {
  display: flex;
  gap: 16px;
  align-items: center;
}
.flight-no {
  font-weight: 600;
  color: var(--el-color-primary);
}
.hint {
  margin-left: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.total-price {
  font-size: 20px;
  font-weight: 700;
  color: #f56c6c;
}
</style>
