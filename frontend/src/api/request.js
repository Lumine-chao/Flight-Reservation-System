import { ElMessage } from 'element-plus'
import axios from 'axios'

import { clearCustomerAuth, loadCustomerAuth } from '@/stores/token'

const request = axios.create({ baseURL: '/api', timeout: 15000 })

request.interceptors.request.use((config) => {
  const token = loadCustomerAuth()?.token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  (resp) => {
    const body = resp.data
    if (body && body.code === 0) return body
    // 业务失败：统一弹服务端中文提示语；页面可通过 silent 配置自行处理
    if (!resp.config?.silent) ElMessage.error(body?.message || '系统繁忙，请稍后再试')
    const err = new Error(body?.message || '系统繁忙，请稍后再试')
    err.code = body?.code
    err.data = body?.data
    return Promise.reject(err)
  },
  (error) => {
    const status = error.response?.status
    const cfg = error.config || {}
    if (status === 401) {
      clearCustomerAuth()
      if (!cfg.silent) ElMessage.error('未登录或登录已过期，请重新登录')
      if (window.location.pathname !== '/login') window.location.href = '/login'
    } else if (status === 403) {
      if (!cfg.silent) ElMessage.error(error.response?.data?.message || '无权访问')
    } else if (!cfg.silent) {
      ElMessage.error('系统繁忙，请稍后再试')
    }
    return Promise.reject(error)
  }
)

export default request
