import { ElMessage } from 'element-plus'
import axios from 'axios'

import { clearAdminAuth, loadAdminAuth } from '@/stores/token'

const adminRequest = axios.create({ baseURL: '/api', timeout: 15000 })

adminRequest.interceptors.request.use((config) => {
  const token = loadAdminAuth()?.token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

adminRequest.interceptors.response.use(
  (resp) => {
    const body = resp.data
    if (body && body.code === 0) return body
    if (!resp.config?.silent) ElMessage.error(body?.message || '系统繁忙，请稍后再试')
    const err = new Error(body?.message || '系统繁忙，请稍后再试')
    err.code = body?.code
    return Promise.reject(err)
  },
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      clearAdminAuth()
      ElMessage.error('登录已过期，请重新登录')
      if (window.location.pathname !== '/admin/login') window.location.href = '/admin/login'
    } else {
      ElMessage.error(error.response?.data?.message || '系统繁忙，请稍后再试')
    }
    return Promise.reject(error)
  }
)

export const adminLogin = (data) => adminRequest.post('/admin/login', data, { silent: true })
export const adminListCities = () => adminRequest.get('/admin/cities')
export const adminCreateCity = (data) => adminRequest.post('/admin/cities', data)
export const adminUpdateCityStatus = (id, status) => adminRequest.put(`/admin/cities/${id}/status`, { status })
export const adminListFlights = () => adminRequest.get('/admin/flights')
export const adminUpsertFlight = (data) => adminRequest.post('/admin/flights', data)
export const adminListOrders = (params) => adminRequest.get('/admin/orders', { params })
export const adminHandleOrder = (orderNo, data) => adminRequest.post(`/admin/orders/${orderNo}/handle`, data)

export default adminRequest
