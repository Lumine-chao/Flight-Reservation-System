<template>
  <div class="page">
    <AppNavbar active="/" />

    <div class="hero">
      <div class="hero-decor decor-ring-1" />
      <div class="hero-decor decor-ring-2" />
      <div class="hero-inner">
        <h1 class="hero-title">航班查询</h1>
        <p class="hero-sub">全国 34 个省级行政区 · 351 座城市 · 跨省航线一键查询，三舱任选</p>
      </div>
    </div>

    <div class="content">
      <el-card shadow="never" class="search-card">
        <FlightForm ref="flightFormRef" :cities="cities" :loading="searching" @search="onSearch" />
      </el-card>

      <el-card shadow="never" class="flight-card">
        <template #header>
          <div class="card-header">
            <span class="card-title-text">可选航班</span>
            <span v-if="searched" class="route-hint">{{ routeHint }}</span>
          </div>
        </template>
        <el-table :data="flights" highlight-current-row @current-change="onSelectFlight" empty-text="未查询到符合条件的航班">
          <el-table-column prop="flightNo" label="航班号" width="100" />
          <el-table-column label="起降时间" width="140">
            <template #default="{ row }">{{ row.departTime }} → {{ row.arriveTime }}</template>
          </el-table-column>
          <el-table-column prop="airline" label="航空公司" />
          <el-table-column label="经济舱" width="110" align="right">
            <template #default="{ row }"><span class="price">¥{{ Number(row.priceEconomy).toFixed(0) }}</span></template>
          </el-table-column>
          <el-table-column label="商务舱" width="110" align="right">
            <template #default="{ row }"><span class="price">¥{{ Number(row.priceBusiness).toFixed(0) }}</span></template>
          </el-table-column>
          <el-table-column label="头等舱" width="110" align="right">
            <template #default="{ row }"><span class="price">¥{{ Number(row.priceFirst).toFixed(0) }}</span></template>
          </el-table-column>
          <el-table-column prop="seatRemain" label="余票" width="80" align="center" />
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" plain @click.stop="onSelectFlight(row)">选择</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card v-if="selectedFlight" shadow="never" class="booking-card">
        <template #header>
          <span class="card-title-text">预订信息</span>
        </template>
        <PassengerForm
          v-model:seat-class="seatClass"
          v-model:ticket-count="ticketCount"
          v-model:passenger-name="passengerName"
          :flight="selectedFlight"
          @change="onPassengerChange"
        />
        <div class="booking-actions">
          <el-button
            type="primary"
            size="large"
            :disabled="!passengerName.trim()"
            :loading="submitting"
            @click="submitOrder"
          >
            提交订单
          </el-button>
          <span v-if="!passengerName.trim()" class="hint">填写乘机人姓名后可提交</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import AppNavbar from '@/components/AppNavbar.vue'
import FlightForm from '@/components/FlightForm.vue'
import PassengerForm from '@/components/PassengerForm.vue'
import { createOrder } from '@/api/order'
import { getCities, searchFlights } from '@/api/flight'

const router = useRouter()
const flightFormRef = ref()
const cities = ref([])
const flights = ref([])
const searching = ref(false)
const searched = ref(false)
const selectedFlight = ref(null)
const seatClass = ref('ECONOMY')
const ticketCount = ref(1)
const passengerName = ref('')
const submitting = ref(false)
const lastQuery = ref({})

const routeHint = computed(() => {
  if (!lastQuery.value.fromCity) return ''
  const fc = cities.value.find((c) => c.cityCode === lastQuery.value.fromCity)
  const tc = cities.value.find((c) => c.cityCode === lastQuery.value.toCity)
  return `${fc?.cityName || ''} → ${tc?.cityName || ''} · ${lastQuery.value.flightDate}`
})

async function loadCities() {
  try {
    const res = await getCities()
    cities.value = res.data || []
  } catch {
    // 已由拦截器提示
  }
}
loadCities()

async function onSearch(query) {
  lastQuery.value = query
  searching.value = true
  selectedFlight.value = null
  try {
    const res = await searchFlights(query)
    flights.value = res.data || []
    searched.value = true
    if (!flights.value.length) ElMessage.info('未查询到符合条件的航班')
  } catch (e) {
    if (e.code !== 3010) ElMessage.error(e.message)
    flights.value = []
    searched.value = true
  } finally {
    searching.value = false
  }
}

function onSelectFlight(row) {
  selectedFlight.value = row
  seatClass.value = 'ECONOMY'
  ticketCount.value = 1
  passengerName.value = ''
}

function onPassengerChange() {
  // OR-08：乘机人姓名为空时提交按钮 disabled，填写后启用（由模板绑定控制）
}

async function submitOrder() {
  submitting.value = true
  try {
    const res = await createOrder({
      flightNo: selectedFlight.value.flightNo,
      flightDate: lastQuery.value.flightDate,
      fromCity: lastQuery.value.fromCity,
      toCity: lastQuery.value.toCity,
      passengerName: passengerName.value.trim(),
      ticketCount: ticketCount.value,
      seatClass: seatClass.value,
    })
    const orderNo = res.data.orderNo
    ElMessageBox.confirm(
      `订单创建成功！订单号：${orderNo}，总价：¥${res.data.totalPrice}`,
      '预订成功',
      {
        confirmButtonText: '查看我的订单',
        cancelButtonText: '继续预订',
        distinguishCancelAndClose: true,
      }
    )
      .then(() => router.push('/orders'))
      .catch(() => {
        // 继续预订：清空已选航班
        selectedFlight.value = null
      })
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* ============ 页头横幅 ============ */
.hero {
  position: relative;
  padding: 48px 16px 84px;
  color: #fff;
  background: linear-gradient(140deg, #0b1f4b 0%, #15357f 45%, #1d4ed8 78%, #0ea5e9 115%);
  overflow: hidden;
}
.hero-decor {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.14);
  pointer-events: none;
}
.decor-ring-1 {
  width: 420px;
  height: 420px;
  top: -180px;
  right: -120px;
}
.decor-ring-2 {
  width: 240px;
  height: 240px;
  bottom: -120px;
  left: 30%;
  border-color: rgba(255, 255, 255, 0.1);
}
.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 1080px;
  margin: 0 auto;
}
.hero-title {
  font-size: 36px;
  font-weight: 700;
  letter-spacing: 2px;
  margin: 0 0 10px;
}
.hero-sub {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.82);
  margin: 0;
}

/* ============ 内容区 ============ */
.content {
  max-width: 1080px;
  margin: 20px auto 0;
  padding: 0 16px 40px;
  position: relative;
  z-index: 2;
}
.search-card {
  border: none;
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(11, 31, 75, 0.14);
  margin-bottom: 20px;
}
.flight-card,
.booking-card {
  border: none;
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(31, 45, 61, 0.08);
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}
.card-title-text {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}
.route-hint {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.price {
  font-weight: 600;
  color: #1d4ed8;
}
.booking-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 90px;
}
.hint {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
