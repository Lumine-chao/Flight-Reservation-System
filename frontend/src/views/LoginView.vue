<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <div class="login-hero">
      <div class="hero-decor decor-ring-1" />
      <div class="hero-decor decor-ring-2" />
      <div class="hero-decor decor-ring-3" />
      <svg class="hero-plane" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10.5 20.5 21 3l-17.5 9.5 7 1.5 1.5 7z" />
        <path d="M10.5 12.5 21 3" />
      </svg>

      <div class="hero-inner">
        <div class="hero-brand">
          <span class="hero-brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.5 20.5 21 3l-17.5 9.5 7 1.5 1.5 7z" />
              <path d="M10.5 12.5 21 3" />
            </svg>
          </span>
          航班预订系统
        </div>
        <h1 class="hero-title">想飞就飞<br />说走就走</h1>
        <p class="hero-sub">
          覆盖全国 34 个省级行政区、351 座城市，经济 / 商务 / 头等三舱任选，在线预订、全程可查。
        </p>
        <ul class="hero-features">
          <li>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            全国 351 城 · 跨省航线一键查询
          </li>
          <li>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            三舱价格透明 · 余票实时可见
          </li>
          <li>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            订单状态全程留痕 · 可改可退
          </li>
        </ul>
      </div>
    </div>

    <!-- 右侧登录区 -->
    <div class="login-panel">
      <div class="login-card">
        <h2 class="card-title">欢迎回来</h2>
        <p class="card-sub">登录后即可查询航班、预订行程</p>

        <el-form label-position="top" @submit.prevent>
          <el-form-item>
            <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" @keyup.enter="submit" />
          </el-form-item>
          <el-form-item>
            <el-input
              ref="pwdRef"
              v-model="form.password"
              type="password"
              show-password
              placeholder="密码"
              size="large"
              :prefix-icon="Lock"
              @keyup.enter="submit"
            />
          </el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="submit">
            登 录
          </el-button>
        </el-form>

        <div class="card-actions">
          <el-button text @click="help">帮助</el-button>
          <span class="spacer" />
          <router-link class="auth-link" to="/register">注册</router-link>
          <router-link class="auth-link" to="/reset-password">忘记密码</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'

import { login } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { PASSWORD_RULE_TEXT } from '@/utils/constants'
import { validateUsernameLogin } from '@/utils/validators'

const router = useRouter()
const store = useUserStore()
const loading = ref(false)
const pwdRef = ref()
const form = reactive({ username: '', password: '' })

onMounted(() => {
  if (store.token) router.push('/')
})

async function submit() {
  const u = validateUsernameLogin(form.username)
  if (u) {
    ElMessage.error(u.message)
    return
  }
  if (!form.password) {
    ElMessage.error('请输入密码')
    return
  }
  loading.value = true
  try {
    const res = await login({ username: form.username, password: form.password }, true)
    store.setAuth(res.data)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    if (e.code === 1105) {
      // LR-11：清空密码框并将光标定位到密码框，展示剩余尝试次数
      form.password = ''
      pwdRef.value?.focus()
      if (e.data?.remainTimes != null) {
        ElMessage.warning(`密码错误，请重试（剩余 ${e.data.remainTimes} 次机会）`)
      }
    } else {
      ElMessage.error(e.message)
    }
  } finally {
    loading.value = false
  }
}

function help() {
  // LR-17：弹出提示框展示密码规则
  ElMessageBox.alert(PASSWORD_RULE_TEXT, '密码规则', { confirmButtonText: '知道了' })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  background: #fff;
}

/* ============ 左侧品牌区 ============ */
.login-hero {
  position: relative;
  flex: 1.15;
  min-width: 0;
  display: flex;
  align-items: center;
  padding: 56px 64px;
  color: #fff;
  background: linear-gradient(140deg, #0b1f4b 0%, #15357f 40%, #1d4ed8 72%, #0ea5e9 115%);
  overflow: hidden;
}
.hero-decor {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.14);
  pointer-events: none;
}
.decor-ring-1 {
  width: 480px;
  height: 480px;
  top: -160px;
  right: -140px;
}
.decor-ring-2 {
  width: 300px;
  height: 300px;
  bottom: -90px;
  left: -80px;
  border-color: rgba(255, 255, 255, 0.1);
}
.decor-ring-3 {
  width: 150px;
  height: 150px;
  bottom: 16%;
  right: 10%;
  border-color: rgba(255, 255, 255, 0.12);
}
.hero-plane {
  position: absolute;
  top: 12%;
  right: 12%;
  width: 96px;
  height: 96px;
  color: rgba(255, 255, 255, 0.28);
  transform: rotate(-12deg);
}
.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 460px;
}
.hero-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 40px;
}
.hero-brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(4px);
}
.hero-brand-icon svg {
  width: 26px;
  height: 26px;
}
.hero-title {
  font-size: 44px;
  line-height: 1.3;
  margin: 0 0 20px;
  font-weight: 700;
  letter-spacing: 2px;
}
.hero-sub {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.82);
  margin: 0 0 32px;
}
.hero-features {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.hero-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
}
.hero-features svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: #7dd3fc;
}

/* ============ 右侧登录区 ============ */
.login-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}
.login-card {
  width: 100%;
  max-width: 360px;
}
.card-title {
  font-size: 30px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px;
}
.card-sub {
  font-size: 15px;
  color: #9ca3af;
  margin: 0 0 32px;
}
.card-actions {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.spacer {
  flex: 1;
}
.auth-link {
  font-size: 15px;
  color: var(--el-color-primary);
  text-decoration: none;
  margin-left: 12px;
}

/* Element 组件内文字放大 */
.login-card :deep(.el-input__inner) {
  font-size: 16px;
  height: 44px;
}
.login-card :deep(.el-button--primary) {
  font-size: 17px;
  height: 46px;
  letter-spacing: 4px;
}

/* ============ 窄屏适配 ============ */
@media (max-width: 880px) {
  .login-hero {
    display: none;
  }
  .login-panel {
    padding: 24px;
  }
}
</style>
