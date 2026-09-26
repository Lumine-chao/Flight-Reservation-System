import request from './request'

export const createOrder = (data) => request.post('/orders', data)
export const listOrders = (params) => request.get('/orders', { params })
export const searchOrders = (params) => request.get('/orders/search', { params, silent: true })
export const getOrderDetail = (orderNo) => request.get(`/orders/${orderNo}`)
export const updateOrder = (orderNo, data) => request.put(`/orders/${orderNo}`, data)
export const cancelOrder = (orderNo) => request.post(`/orders/${orderNo}/cancel`)
