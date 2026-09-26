<template>
  <div class="page">
    <AdminNavbar active="/admin/data" />

    <div class="content">
      <el-card shadow="never">
        <el-tabs v-model="activeTab">
          <!-- ============ 城市管理 ============ -->
          <el-tab-pane label="城市管理" name="cities">
            <div class="toolbar">
              <span class="toolbar-tip">城市停用后，新建与修改订单时不可再选择该城市</span>
              <el-button type="primary" @click="openCityDialog">新增城市</el-button>
            </div>
            <el-table :data="cities" v-loading="cityLoading" empty-text="暂无城市">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="province" label="省份" min-width="140" />
              <el-table-column prop="cityCode" label="城市编码" width="140" />
              <el-table-column prop="cityName" label="城市名称" min-width="140" />
              <el-table-column label="状态" width="120" align="center">
                <template #default="{ row }">
                  <el-switch
                    :model-value="row.status === 1"
                    :loading="switchingId === row.id"
                    @change="(val) => toggleCity(row, val)"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- ============ 航班管理 ============ -->
          <el-tab-pane label="航班管理" name="flights">
            <div class="toolbar">
              <span class="toolbar-tip">航班停用后，客户下单时不可再选择该航班</span>
              <el-button type="primary" @click="openFlightDialog()">新增航班</el-button>
            </div>
            <el-table :data="flights" v-loading="flightLoading" empty-text="暂无航班">
              <el-table-column prop="flightNo" label="航班号" width="100" />
              <el-table-column prop="airline" label="航空公司" width="140" />
              <el-table-column label="航线" min-width="140">
                <template #default="{ row }">{{ row.fromCityName }} → {{ row.toCityName }}</template>
              </el-table-column>
              <el-table-column label="起降时间" width="140">
                <template #default="{ row }">{{ row.departTime }} → {{ row.arriveTime }}</template>
              </el-table-column>
              <el-table-column label="经济/商务/头等" width="190" align="right">
                <template #default="{ row }">
                  ¥{{ Number(row.priceEconomy).toFixed(0) }} / ¥{{ Number(row.priceBusiness).toFixed(0) }} /
                  ¥{{ Number(row.priceFirst).toFixed(0) }}
                </template>
              </el-table-column>
              <el-table-column prop="seatRemain" label="余票" width="80" align="center" />
              <el-table-column label="状态" width="120" align="center">
                <template #default="{ row }">
                  <el-switch
                    :model-value="row.status === 1"
                    :loading="switchingId === row.id"
                    @change="(val) => toggleFlight(row, val)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button size="small" text type="primary" @click="openFlightDialog(row)">编辑</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <!-- 新增城市 -->
    <el-dialog v-model="cityDialogVisible" title="新增城市" width="420px">
      <el-form label-width="90px">
        <el-form-item label="省份">
          <el-input v-model="cityForm.province" maxlength="32" placeholder="如：北京市" />
        </el-form-item>
        <el-form-item label="城市编码">
          <el-input v-model="cityForm.cityCode" maxlength="8" placeholder="如：BJS" />
        </el-form-item>
        <el-form-item label="城市名称">
          <el-input v-model="cityForm.cityName" maxlength="32" placeholder="如：北京" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cityDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="citySaving" @click="submitCity">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增 / 编辑航班 -->
    <el-dialog
      v-model="flightDialogVisible"
      :title="flightForm.id ? '编辑航班' : '新增航班'"
      width="640px"
      @closed="resetFlightForm"
    >
      <el-form label-width="110px">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="航班号">
              <el-input v-model="flightForm.flightNo" maxlength="10" placeholder="如：CA101" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="航空公司">
              <el-input v-model="flightForm.airline" maxlength="32" placeholder="如：中国国际航空" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出发城市">
              <el-cascader
                v-model="flightForm.fromCity"
                :options="fromOptions"
                :props="CASCADER_PROPS"
                filterable
                placeholder="选择省份/城市"
                style="width: 100%"
                @change="onRouteChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到达城市">
              <el-cascader
                v-model="flightForm.toCity"
                :options="toOptions"
                :props="CASCADER_PROPS"
                filterable
                placeholder="选择省份/城市"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="起飞时间">
              <el-time-picker
                v-model="flightForm.departTime"
                value-format="HH:mm"
                format="HH:mm"
                placeholder="HH:mm"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到达时间">
              <el-time-picker
                v-model="flightForm.arriveTime"
                value-format="HH:mm"
                format="HH:mm"
                placeholder="HH:mm"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="经济舱价">
              <el-input-number v-model="flightForm.priceEconomy" :min="0" :precision="2" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="商务舱价">
              <el-input-number v-model="flightForm.priceBusiness" :min="0" :precision="2" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="头等舱价">
              <el-input-number v-model="flightForm.priceFirst" :min="0" :precision="2" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="余票数">
              <el-input-number v-model="flightForm.seatRemain" :min="0" :max="999" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="航班状态">
              <el-radio-group v-model="flightForm.status">
                <el-radio :value="1">启用</el-radio>
                <el-radio :value="0">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="flightDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="flightSaving" @click="submitFlight">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import AdminNavbar from '@/components/AdminNavbar.vue'
import { CASCADER_PROPS, cityCascaderOptions } from '@/utils/cities'
import {
  adminCreateCity,
  adminListCities,
  adminListFlights,
  adminUpdateCityStatus,
  adminUpsertFlight,
} from '@/api/admin'

const activeTab = ref('cities')

const cities = ref([])
const cityLoading = ref(false)
const cityDialogVisible = ref(false)
const citySaving = ref(false)
const cityForm = reactive({ province: '', cityCode: '', cityName: '' })

const flights = ref([])
const flightLoading = ref(false)
const flightDialogVisible = ref(false)
const flightSaving = ref(false)
const switchingId = ref(null)

const emptyFlightForm = () => ({
  id: null,
  flightNo: '',
  fromCity: '',
  toCity: '',
  departTime: '',
  arriveTime: '',
  airline: '',
  priceEconomy: 0,
  priceBusiness: 0,
  priceFirst: 0,
  seatRemain: 100,
  status: 1,
})
const flightForm = reactive(emptyFlightForm())

const enabledCities = computed(() => cities.value.filter((c) => c.status === 1))
const fromOptions = computed(() => cityCascaderOptions(enabledCities.value))
const toOptions = computed(() =>
  cityCascaderOptions(enabledCities.value.filter((c) => c.cityCode !== flightForm.fromCity))
)

async function loadCities() {
  cityLoading.value = true
  try {
    const res = await adminListCities()
    cities.value = res.data || []
  } catch {
    cities.value = []
  } finally {
    cityLoading.value = false
  }
}

async function loadFlights() {
  flightLoading.value = true
  try {
    const res = await adminListFlights()
    flights.value = res.data || []
  } catch {
    flights.value = []
  } finally {
    flightLoading.value = false
  }
}

loadCities()
loadFlights()

function openCityDialog() {
  cityForm.province = ''
  cityForm.cityCode = ''
  cityForm.cityName = ''
  cityDialogVisible.value = true
}

async function submitCity() {
  const code = cityForm.cityCode.trim().toUpperCase()
  const name = cityForm.cityName.trim()
  if (!code || !name) {
    ElMessage.warning('请填写城市编码与名称')
    return
  }
  citySaving.value = true
  try {
    await adminCreateCity({ cityCode: code, cityName: name, province: cityForm.province.trim() })
    ElMessage.success('城市保存成功')
    cityDialogVisible.value = false
    loadCities()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    citySaving.value = false
  }
}

async function toggleCity(row, val) {
  switchingId.value = row.id
  try {
    await adminUpdateCityStatus(row.id, val ? 1 : 0)
    ElMessage.success(val ? '城市已启用' : '城市已停用')
    loadCities()
  } catch (e) {
    ElMessage.error(e.message)
    loadCities()
  } finally {
    switchingId.value = null
  }
}

function openFlightDialog(row) {
  if (row) {
    Object.assign(flightForm, {
      id: row.id,
      flightNo: row.flightNo,
      fromCity: row.fromCity,
      toCity: row.toCity,
      departTime: row.departTime,
      arriveTime: row.arriveTime,
      airline: row.airline,
      priceEconomy: Number(row.priceEconomy),
      priceBusiness: Number(row.priceBusiness),
      priceFirst: Number(row.priceFirst),
      seatRemain: row.seatRemain,
      status: row.status,
    })
  } else {
    Object.assign(flightForm, emptyFlightForm())
  }
  flightDialogVisible.value = true
}

function resetFlightForm() {
  Object.assign(flightForm, emptyFlightForm())
}

function onRouteChange() {
  if (flightForm.toCity === flightForm.fromCity) flightForm.toCity = ''
}

async function submitFlight() {
  const f = flightForm
  if (!f.flightNo.trim()) {
    ElMessage.warning('请输入航班号')
    return
  }
  if (!f.fromCity || !f.toCity) {
    ElMessage.warning('请选择出发城市与到达城市')
    return
  }
  if (!f.departTime || !f.arriveTime) {
    ElMessage.warning('请选择起飞与到达时间')
    return
  }
  if (!f.airline.trim()) {
    ElMessage.warning('请输入航空公司')
    return
  }
  flightSaving.value = true
  try {
    await adminUpsertFlight({ ...f })
    ElMessage.success('航班保存成功')
    flightDialogVisible.value = false
    loadFlights()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    flightSaving.value = false
  }
}

async function toggleFlight(row, val) {
  switchingId.value = row.id
  try {
    await adminUpsertFlight({
      id: row.id,
      flightNo: row.flightNo,
      fromCity: row.fromCity,
      toCity: row.toCity,
      departTime: row.departTime,
      arriveTime: row.arriveTime,
      airline: row.airline,
      priceEconomy: Number(row.priceEconomy),
      priceBusiness: Number(row.priceBusiness),
      priceFirst: Number(row.priceFirst),
      seatRemain: row.seatRemain,
      status: val ? 1 : 0,
    })
    ElMessage.success(val ? '航班已启用' : '航班已停用')
    loadFlights()
  } catch (e) {
    ElMessage.error(e.message)
    loadFlights()
  } finally {
    switchingId.value = null
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
.toolbar-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
