<template>
  <div class="page">
    <AppNavbar active="/orders" />

    <div class="hero">
      <div class="hero-decor decor-ring-1" />
      <div class="hero-inner">
        <h1 class="hero-title">我的订单</h1>
        <p class="hero-sub">订单状态全程留痕 · 已出票订单可修改或取消</p>
      </div>
    </div>

    <div class="content">
      <el-card shadow="never" class="orders-card">
        <div class="toolbar">
          <el-radio-group v-model="statusFilter" @change="loadOrders">
            <el-radio-button v-for="s in ORDER_STATUS_FILTERS" :key="s.value" :value="s.value">
              {{ s.label }}
            </el-radio-button>
          </el-radio-group>

          <div class="search-box">
            <el-select v-model="searchType" style="width: 110px">
              <el-option label="订单号" value="orderNo" />
              <el-option label="乘机人" value="passengerName" />
              <el-option label="航班日期" value="flightDate" />
            </el-select>
            <el-input
              v-model="searchText"
              :placeholder="searchType === 'flightDate' ? 'mm/dd/yy' : '请输入检索内容'"
              style="width: 180px"
              clearable
              @keyup.enter="doSearch"
            />
            <el-button type="primary" @click="doSearch">查询</el-button>
            <el-button v-if="searched" @click="resetSearch">重置</el-button>
          </div>
        </div>

        <el-table :data="orders" v-loading="loading" empty-text="暂无订单">
          <el-table-column prop="orderNo" label="订单号" width="160" />
          <el-table-column prop="flightNo" label="航班号" width="90" />
          <el-table-column label="航线" min-width="140">
            <template #default="{ row }">{{ row.fromCityName }} → {{ row.toCityName }}</template>
          </el-table-column>
          <el-table-column prop="flightDate" label="航班日期" width="100" />
          <el-table-column prop="passengerName" label="乘机人" width="90" />
          <el-table-column label="票数/舱位" width="110">
            <template #default="{ row }">{{ row.ticketCount }}张 · {{ row.seatClassName }}</template>
          </el-table-column>
          <el-table-column label="总价" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.totalPrice).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }"><OrderStatusTag :status="row.status" /></template>
          </el-table-column>
          <el-table-column prop="createdAt" label="下单时间" width="150" />
          <el-table-column label="操作" width="200" align="center" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="openDetail(row)">详情</el-button>
              <template v-if="canModify(row)">
                <el-button size="small" text type="warning" @click="openUpdate(row)">修改</el-button>
                <el-button size="small" plain type="danger" @click="openCancel(row)">取消</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 订单详情 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="640px">
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ detail.orderNo }}</el-descriptions-item>
          <el-descriptions-item label="状态"><OrderStatusTag :status="detail.status" /></el-descriptions-item>
          <el-descriptions-item label="航班号">{{ detail.flightNo }}</el-descriptions-item>
          <el-descriptions-item label="航空公司">{{ detail.airline }}</el-descriptions-item>
          <el-descriptions-item label="航线">{{ detail.fromCityName }} → {{ detail.toCityName }}</el-descriptions-item>
          <el-descriptions-item label="航班日期">{{ detail.flightDate }}</el-descriptions-item>
          <el-descriptions-item label="起降时间">{{ detail.departTime }} → {{ detail.arriveTime }}</el-descriptions-item>
          <el-descriptions-item label="乘机人">{{ detail.passengerName }}</el-descriptions-item>
          <el-descriptions-item label="票数">{{ detail.ticketCount }} 张</el-descriptions-item>
          <el-descriptions-item label="舱位">{{ detail.seatClassName }}</el-descriptions-item>
          <el-descriptions-item label="单价">¥{{ Number(detail.unitPrice).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="总价">¥{{ Number(detail.totalPrice).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="下单时间">{{ detail.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ detail.updatedAt }}</el-descriptions-item>
        </el-descriptions>
        <h4 class="log-title">状态流转记录</h4>
        <el-timeline>
          <el-timeline-item
            v-for="(log, i) in detail.statusLog"
            :key="i"
            :timestamp="log.operateTime"
            :type="i === detail.statusLog.length - 1 ? 'primary' : ''"
          >
            <span>
              {{ log.actionName }} → {{ log.toStatusName }}
              <span v-if="log.operatorType === 'SYSTEM'" class="log-remark">（系统自动）</span>
              <span v-if="log.remark" class="log-remark">备注：{{ log.remark }}</span>
            </span>
          </el-timeline-item>
        </el-timeline>
      </template>
    </el-dialog>

    <!-- 修改订单 -->
    <el-dialog v-model="updateVisible" title="修改订单" width="560px" @closed="resetUpdateForm">
      <el-form label-width="90px" v-if="updateForm">
        <el-form-item label="订单号">
          <el-input :model-value="updateForm.orderNo" disabled />
        </el-form-item>
        <el-form-item label="航班日期">
          <el-date-picker
            v-model="updateForm.flightDate"
            type="date"
            format="MM/DD/YY"
            value-format="MM/DD/YY"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="出发地">
          <el-cascader
            v-model="updateForm.fromCity"
            :options="updateFromOptions"
            :props="CASCADER_PROPS"
            filterable
            placeholder="选择省份/城市"
            style="width: 100%"
            @change="onUpdateRouteChange"
          />
        </el-form-item>
        <el-form-item label="目的地">
          <el-cascader
            v-model="updateForm.toCity"
            :options="updateToOptions"
            :props="CASCADER_PROPS"
            filterable
            placeholder="选择省份/城市"
            style="width: 100%"
            @change="onUpdateRouteChange"
          />
        </el-form-item>
        <el-form-item label="航班">
          <el-select v-model="updateForm.flightNo" style="width: 100%" placeholder="选择航班">
            <el-option
              v-for="f in routeFlights"
              :key="f.flightNo"
              :label="`${f.flightNo} ${f.departTime}→${f.arriveTime} ¥${Number(f.priceEconomy).toFixed(0)}起`"
              :value="f.flightNo"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="乘机人姓名">
          <el-input v-model="updateForm.passengerName" maxlength="64" />
        </el-form-item>
        <el-form-item label="票数">
          <el-input-number v-model="updateForm.ticketCount" :min="1" :max="9" />
        </el-form-item>
        <el-form-item label="舱位">
          <el-radio-group v-model="updateForm.seatClass">
            <el-radio v-for="s in SEAT_CLASSES" :key="s.value" :value="s.value">{{ s.label }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="updateVisible = false">取消</el-button>
        <el-button type="primary" :loading="updating" @click="submitUpdate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import AppNavbar from '@/components/AppNavbar.vue'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import { cancelOrder, getOrderDetail, listOrders, searchOrders, updateOrder } from '@/api/order'
import { getCities, searchFlights } from '@/api/flight'
import { ORDER_STATUS_FILTERS, SEAT_CLASSES } from '@/utils/constants'
import { todayMmDdYy } from '@/utils/date'
import { CASCADER_PROPS, cityCascaderOptions } from '@/utils/cities'

const ACTION_NAMES = {
  CREATE: '创建订单',
  UPDATE: '更新订单',
  CANCEL: '取消订单',
  AUTO_DONE: '自动完成',
  ADMIN_CANCEL: '管理员取消',
}

const loading = ref(false)
const orders = ref([])
const statusFilter = ref('')
const searchType = ref('orderNo')
const searchText = ref('')
const searched = ref(false)
const cities = ref([])

const detailVisible = ref(false)
const detail = ref(null)
const updateVisible = ref(false)
const updateForm = ref(null)
const updating = ref(false)
const routeFlights = ref([])
const updateTarget = ref(null)

const canModify = (row) => row.status === 'TICKETED' && row.flightDate > todayMmDdYy()

const updateFromOptions = computed(() => cityCascaderOptions(cities.value))
const updateToOptions = computed(() =>
  cityCascaderOptions(cities.value.filter((c) => c.cityCode !== updateForm.value?.fromCity))
)

async function loadCities() {
  try {
    const res = await getCities()
    cities.value = res.data || []
  } catch {
    // 拦截器已提示
  }
}
onMounted(loadCities)

async function loadOrders() {
  loading.value = true
  try {
    const res = await listOrders(statusFilter.value ? { status: statusFilter.value } : {})
    orders.value = res.data || []
  } catch {
    orders.value = []
  } finally {
    loading.value = false
  }
}
loadOrders()

async function doSearch() {
  if (!searchText.value) {
    ElMessage.warning('请输入检索内容')
    return
  }
  loading.value = true
  try {
    const res = await searchOrders({ [searchType.value]: searchText.value })
    orders.value = res.data || []
    searched.value = true
  } catch (e) {
    // 拦截器已提示（3002/3003/3004/3008）
    orders.value = []
  } finally {
    loading.value = false
  }
}

function resetSearch() {
  searchText.value = ''
  searched.value = false
  loadOrders()
}

async function openDetail(row) {
  try {
    const res = await getOrderDetail(row.orderNo)
    detail.value = {
      ...res.data,
      statusLog: (res.data.statusLog || []).map((l) => ({ ...l, actionName: ACTION_NAMES[l.action] || l.action })),
    }
    detailVisible.value = true
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function openUpdate(row) {
  updateTarget.value = row
  updateForm.value = {
    orderNo: row.orderNo,
    flightDate: row.flightDate,
    fromCity: row.fromCity,
    toCity: row.toCity,
    flightNo: row.flightNo,
    passengerName: row.passengerName,
    ticketCount: row.ticketCount,
    seatClass: row.seatClass,
  }
  await loadRouteFlights(row.fromCity, row.toCity)
  updateVisible.value = true
}

function resetUpdateForm() {
  updateForm.value = null
  routeFlights.value = []
  updateTarget.value = null
}

async function loadRouteFlights(fromCity, toCity) {
  try {
    const res = await searchFlights({ fromCity, toCity })
    routeFlights.value = res.data || []
  } catch {
    routeFlights.value = []
  }
}

async function onUpdateRouteChange() {
  if (updateForm.value.fromCity && updateForm.value.toCity) {
    updateForm.value.flightNo = ''
    await loadRouteFlights(updateForm.value.fromCity, updateForm.value.toCity)
  }
}

function disabledDate(date) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date.getTime() <= today.getTime()
}

async function submitUpdate() {
  const f = updateForm.value
  if (!f.flightDate || !f.fromCity || !f.toCity || !f.flightNo) {
    ElMessage.warning('请完整填写航班日期、起终点与航班')
    return
  }
  if (!f.passengerName.trim()) {
    ElMessage.error('请输入乘机人姓名')
    return
  }
  updating.value = true
  try {
    await updateOrder(f.orderNo, {
      flightDate: f.flightDate,
      fromCity: f.fromCity,
      toCity: f.toCity,
      flightNo: f.flightNo,
      passengerName: f.passengerName,
      ticketCount: f.ticketCount,
      seatClass: f.seatClass,
    })
    ElMessage.success('订单更新成功')
    updateVisible.value = false
    loadOrders()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    updating.value = false
  }
}

function openCancel(row) {
  // OR-23 / OR-25：展示「是否确定要取消该订单」，同时展示订单号与航班信息便于核对
  ElMessageBox.confirm(
    `是否确定要取消该订单？\n订单号：${row.orderNo}\n航班：${row.flightNo}（${row.fromCityName} → ${row.toCityName}，${row.flightDate}）`,
    '取消订单',
    {
      confirmButtonText: '确定取消',
      cancelButtonText: '再想想',
      type: 'warning',
      // OR-26：点击取消关闭弹窗且不发起请求，订单状态保持不变
    }
  ).then(async () => {
    try {
      await cancelOrder(row.orderNo)
      ElMessage.success('订单已取消')
      loadOrders()
    } catch (e) {
      ElMessage.error(e.message)
    }
  }).catch(() => {})
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
  padding: 44px 16px 76px;
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
  width: 400px;
  height: 400px;
  top: -170px;
  right: -110px;
}
.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 1120px;
  margin: 0 auto;
}
.hero-title {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 2px;
  margin: 0 0 8px;
}
.hero-sub {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.82);
  margin: 0;
}

/* ============ 内容区 ============ */
.content {
  max-width: 1120px;
  margin: -46px auto 0;
  padding: 0 16px 40px;
}
.orders-card {
  border: none;
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(11, 31, 75, 0.1);
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.search-box {
  display: flex;
  gap: 8px;
}
.log-title {
  margin: 20px 0 8px;
}
.log-remark {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
