<template>
  <header class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="brand">
        <span class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.5 20.5 21 3l-17.5 9.5 7 1.5 1.5 7z" />
            <path d="M10.5 12.5 21 3" />
          </svg>
        </span>
        <span class="brand-text">航班预订系统</span>
      </router-link>

      <nav class="nav-links">
        <router-link to="/" class="nav-link" :class="{ active: active === '/' }">航班查询</router-link>
        <router-link to="/orders" class="nav-link" :class="{ active: active === '/orders' }">我的订单</router-link>
      </nav>

      <div class="navbar-right">
        <span class="user-chip">
          <el-icon :size="15"><User /></el-icon>
          <span>{{ username }}</span>
        </span>
        <el-button text type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'

import { logout as logoutApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  active: { type: String, default: '/' },
})

const router = useRouter()
const store = useUserStore()
const username = store.username

async function handleLogout() {
  try {
    await logoutApi()
  } catch {
    // 令牌已失效也允许本地登出
  }
  store.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.navbar-inner {
  max-width: 1120px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 60px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  margin-right: 32px;
}
.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(135deg, #1d4ed8, #0ea5e9);
}
.brand-icon svg {
  width: 18px;
  height: 18px;
}
.brand-text {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: 1px;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
}
.nav-link {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 15px;
  color: var(--el-text-color-regular);
  text-decoration: none;
  transition: all 0.2s;
}
.nav-link:hover {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.nav-link.active {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  font-weight: 600;
}
.navbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-size: 14px;
  font-weight: 500;
}
</style>
