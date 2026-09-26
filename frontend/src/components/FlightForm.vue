<template>
  <div class="flight-form">
    <div class="field">
      <span class="field-label">出发地</span>
      <el-cascader
        v-model="form.fromCity"
        :options="fromOptions"
        :props="CASCADER_PROPS"
        filterable
        placeholder="选择省份/城市"
        style="width: 200px"
        @change="onFromChange"
      />
    </div>
    <div class="field">
      <span class="field-label">目的地</span>
      <!-- OR-04：目的地下拉过滤掉与出发地相同的城市 -->
      <el-cascader
        v-model="form.toCity"
        :options="toOptions"
        :props="CASCADER_PROPS"
        filterable
        placeholder="选择省份/城市"
        style="width: 200px"
      />
    </div>
    <div class="field">
      <span class="field-label">航班日期</span>
      <el-date-picker
        v-model="form.flightDate"
        type="date"
        format="MM/DD/YY"
        value-format="MM/DD/YY"
        placeholder="mm/dd/yy"
        :disabled-date="disabledDate"
        style="width: 160px"
      />
    </div>
    <div class="field search-field">
      <span class="field-label invisible">查询</span>
      <el-button type="primary" size="large" :loading="loading" @click="onSearch">查询航班</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'

import { validateFlightDate } from '@/utils/validators'
import { CASCADER_PROPS, cityCascaderOptions } from '@/utils/cities'

const props = defineProps({
  cities: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['search'])

const form = reactive({ fromCity: '', toCity: '', flightDate: '' })

const fromOptions = computed(() => cityCascaderOptions(props.cities))
const toOptions = computed(() =>
  cityCascaderOptions(props.cities.filter((c) => c.cityCode !== form.fromCity))
)

function onFromChange() {
  // 出发地变化后若目的地与之相同则清空
  if (form.toCity === form.fromCity) form.toCity = ''
}

function disabledDate(date) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date.getTime() <= today.getTime()
}

function onSearch() {
  if (!form.fromCity || !form.toCity) {
    ElMessage.warning('请选择出发地和目的地')
    return
  }
  if (!form.flightDate) {
    ElMessage.warning('请选择航班日期')
    return
  }
  const err = validateFlightDate(form.flightDate)
  if (err) {
    ElMessage.error(err.message)
    return
  }
  emit('search', { ...form })
}

defineExpose({ reset: () => { form.fromCity = ''; form.toCity = ''; form.flightDate = '' } })
</script>

<style scoped>
.flight-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
}
.field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}
.field-label {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
  margin: 0;
}
.field-label.invisible {
  visibility: hidden;
}
.search-field .el-button {
  height: 40px;
}
</style>