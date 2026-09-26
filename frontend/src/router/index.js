import { createRouter, createWebHistory } from 'vue-router'

import { loadAdminAuth, loadCustomerAuth } from '@/stores/token'

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue') },
  { path: '/reset-password', name: 'reset', component: () => import('@/views/ResetPasswordView.vue') },
  { path: '/', name: 'home', component: () => import('@/views/FlightSearchView.vue'), meta: { requiresAuth: true } },
  { path: '/orders', name: 'orders', component: () => import('@/views/MyOrdersView.vue'), meta: { requiresAuth: true } },
  { path: '/admin/login', name: 'adminLogin', component: () => import('@/views/AdminLoginView.vue') },
  { path: '/admin/data', name: 'adminData', component: () => import('@/views/AdminDataView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/orders', name: 'adminOrders', component: () => import('@/views/AdminOrdersView.vue'), meta: { requiresAdmin: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !loadCustomerAuth()) return { name: 'login' }
  if (to.meta.requiresAdmin && !loadAdminAuth()) return { name: 'adminLogin' }
  return true
})

export default router
