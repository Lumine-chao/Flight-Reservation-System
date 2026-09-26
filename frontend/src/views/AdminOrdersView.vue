<template>
  <div class="page">
    <AdminNavbar active="/admin/orders" />

    <div class="content">
      <el-card shadow="never">
        <div class="toolbar">
          <div class="search-box">
            <el-select v-model="searchType" style="width: 120px">
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
            <el-select v-model="statusFilter" style="width: 110px" placeholder="订单状态">
              <el-option v-for="s in ORDER_STATUS_FILTERS" :key="s.value" :label="s.label" :value="s.value" />
            </el-select>
            <el-button type="primary" @click="doSearch">查询</el-button>
            <el-button v-if="searched" @click="resetSearch">重置</el-button>
          </div>
        </div>

        <el-table :data="orders" v-loading="loading" empty-text="暂无订单">
          <el-table-column prop="orderNo" label="订单号" width="160" />
          <el-table-column prop="userName" label="下单用户" width="100" />
          <el-table-column prop="flightNo" label="航班号" width="90" />
          <el-table-column label="航线" min-width="130">
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
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="openDetail(row)">详情</el-button>
              <el-button
                v-if="row.status === 'TICKETED'"
                size="small"
                text
                type="danger"
                @click="openCancel(row)"
              >
                取消
              </el-button>
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
          <el-descriptions-item label="下单用户">{{ detail.userName }}</el-descriptions-item>
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
      </template>
    </el-dialog>

    <!-- 异常订单处置 -->
    <el-dialog v-model="cancelVisible" title="取消订单（异常处置）" width="480px">
      <div v-if="cancelTarget" class="cancel-tip">
        即将取消订单 <b>{{ cancelTarget.orderNo }}</b>（{{ cancelTarget.flightNo }}，
        {{ cancelTarget.fromCityName }} → {{ cancelTarget.toCityName }}，{{ cancelTarget.flightDate }}），
        请填写处置备注，操作将记录在状态流转中。
      </div>
      <el-input
        v-model="cancelRemark"
        type="textarea"
        :rows="3"
        maxlength="255"
        show-word-limit
        placeholder="请填写取消原因（必填）"
      />
      <template #footer>
        <el-button @click="cancelVisible = false">再想想</el-button>
        <el-button type="danger" :loading="canceling" @click="submitCancel">确定取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import AdminNavbar from '@/components/AdminNavbar.vue'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import { adminHandleOrder, adminListOrders } from '@/api/admin'
import { ORDER_STATUS_FILTERS } from '@/utils/constants'

const loading = ref(false)
const orders = ref([])
const searchType = ref('orderNo')
const searchText = ref('')
const statusFilter = ref('')
const searched = ref(false)

const detailVisible = ref(false)
const detail = ref(null)
const cancelVisible = ref(false)
const cancelTarget = ref(null)
const cancelRemark = ref('')
const canceling = ref(false)

async function loadOrders(params = {}) {
  loading.value = true
  try {
    const res = await adminListOrders(params)
    orders.value = res.data || []
  } catch {
    orders.value = []
  } finally {
    loading.value = false
  }
}
loadOrders()

async function doSearch() {
  const params = {}
  if (searchText.value) params[searchType.value] = searchText.value
  if (statusFilter.value) params.status = statusFilter.value
  if (!params.orderNo && !params.passengerName && !params.flightDate && !params.status) {
    ElMessage.warning('请输入检索条件')
    return
  }
  searched.value = true
  await loadOrders(params)
}

function resetSearch() {
  searchText.value = ''
  statusFilter.value = ''
  searched.value = false
  loadOrders()
}

function openDetail(row) {
  detail.value = row
  detailVisible.value = true
}

function openCancel(row) {
  cancelTarget.value = row
  cancelRemark.value = ''
  cancelVisible.value = true
}

async function submitCancel() {
  if (!cancelRemark.value.trim()) {
    ElMessage.warning('请填写处置备注')
    return
  }
  canceling.value = true
  try {
    await adminHandleOrder(cancelTarget.value.orderNo, {
      action: 'cancel',
      remark: cancelRemark.value.trim(),
    })
    ElMessage.success('订单已取消')
    cancelVisible.value = false
    loadOrders(searchText.value || statusFilter.value
      ? { [searchType.value]: searchText.value, status: statusFilter.value }
      : {})
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    canceling.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
}
.content {
  max-width: 1120px;
  margin: 0 auto;
  padding: 20px 16px 40px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.search-box {
  display: flex;
  gap: 8px;
}
.cancel-tip {
  color: var(--el-text-color-regular);
  margin-bottom: 12px;
  line-height: 1.6;
}
</style>
