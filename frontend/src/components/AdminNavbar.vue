<template>
  <el-menu mode="horizontal" :default-active="active" router :ellipsis="false" class="admin-navbar">
    <el-menu-item index="/admin/data" class="brand">
      <span class="brand-title">航班预订系统 · 管理后台</span>
    </el-menu-item>
    <el-menu-item index="/admin/data">基础数据</el-menu-item>
    <el-menu-item index="/admin/orders">订单管理</el-menu-item>
    <div class="navbar-right">
      <el-tag type="danger" effect="plain">{{ username }}</el-tag>
      <el-button text type="danger" @click="handleLogout">退出登录</el-button>
    </div>
  </el-menu>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useAdminStore } from '@/stores/admin'

defineProps({
  active: { type: String, default: '/admin/data' },
})

const router = useRouter()
const store = useAdminStore()
const username = store.username

function handleLogout() {
  store.logout()
  ElMessage.success('已退出登录')
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-navbar {
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: #fff;
}
.brand {
  pointer-events: none;
  margin-right: 24px;
}
.brand-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-color-danger);
}
.navbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
