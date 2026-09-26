<template>
  <div class="auth-page">
    <!-- 左侧品牌区 -->
    <div class="auth-hero">
      <div class="hero-decor decor-ring-1" />
      <div class="hero-decor decor-ring-2" />

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
        <h1 class="hero-title">加入航班预订</h1>
        <p class="hero-sub">
          注册一个账号，即可查询全国 34 个省级行政区、351 座城市的航班，在线预订、全程可查。
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

    <!-- 右侧注册表单 -->
    <div class="auth-panel">
      <div class="auth-card">
        <h2 class="card-title">创建账号</h2>
        <p class="card-sub">填写以下信息完成注册</p>
        <el-form label-position="top" @submit.prevent>
          <el-form-item label="用户名（4～8位，字母和数字，不能纯数字或数字开头）">
            <el-input v-model="form.username" maxlength="8" size="large" @blur="checkUsername" />
          </el-form-item>
          <el-form-item label="密码（8～20位，需同时包含字母与数字）">
            <el-input v-model="form.password" type="password" show-password size="large" @blur="checkPassword" />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="form.confirmPassword" type="password" show-password size="large" @blur="checkConfirm" />
          </el-form-item>
          <el-form-item label="安全问题">
            <el-select v-model="form.securityQuestion" placeholder="请选择安全问题" size="large" style="width: 100%">
              <el-option v-for="q in SECURITY_QUESTIONS" :key="q" :label="q" :value="q" />
            </el-select>
          </el-form-item>
          <el-form-item label="答案（2～30位）">
            <el-input v-model="form.securityAnswer" maxlength="30" size="large" />
          </el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="submit">
            注 册
          </el-button>
          <div class="auth-footer">
            已有账号？<router-link class="auth-link" to="/login">去登录</router-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { register } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { SECURITY_QUESTIONS } from '@/utils/constants'
import { validateAnswerLength, validatePasswordStrength, validateUsername } from '@/utils/validators'

const router = useRouter()
const store = useUserStore()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  securityQuestion: '',
  securityAnswer: '',
})

function checkUsername() {
  const r = validateUsername(form.username)
  if (r) ElMessage.error(r.message)
  return r
}

function checkPassword() {
  const r = validatePasswordStrength(form.password)
  if (r) ElMessage.error(r.message)
  return r
}

function checkConfirm() {
  if (form.confirmPassword && form.password !== form.confirmPassword) {
    ElMessage.error('两次输入的密码不一致，请重新输入')
    return { code: 1008 }
  }
  return null
}

async function submit() {
  if (checkUsername()) return
  if (checkPassword()) return
  if (checkConfirm()) return
  const answer = validateAnswerLength(form.securityAnswer)
  if (answer) {
    ElMessage.error(answer.message)
    return
  }
  if (!form.securityQuestion) {
    ElMessage.error('请选择安全问题并填写答案')
    return
  }
  loading.value = true
  try {
    const res = await register({ ...form })
    store.setAuth(res.data)
    ElMessage.success('注册成功，已自动登录')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  background: #fff;
}

/* ============ 左侧品牌区 ============ */
.auth-hero {
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
.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 460px;
}
.hero-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 36px;
}
.hero-brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(4px);
}
.hero-brand-icon svg {
  width: 22px;
  height: 22px;
}
.hero-title {
  font-size: 44px;
  line-height: 1.25;
  margin: 0 0 20px;
  font-weight: 700;
  letter-spacing: 2px;
}
.hero-sub {
  font-size: 15px;
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
  gap: 14px;
}
.hero-features li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}
.hero-features svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: #7dd3fc;
}

/* ============ 右侧表单区 ============ */
.auth-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}
.auth-card {
  width: 100%;
  max-width: 420px;
}
.card-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px;
}
.card-sub {
  font-size: 14px;
  color: #9ca3af;
  margin: 0 0 28px;
}
.auth-footer {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
.auth-link {
  color: var(--el-color-primary);
  text-decoration: none;
}
.auth-card :deep(.el-input__inner) {
  font-size: 15px;
  height: 42px;
}
.auth-card :deep(.el-button--primary) {
  font-size: 16px;
  height: 44px;
  letter-spacing: 4px;
}

/* ============ 窄屏适配 ============ */
@media (max-width: 880px) {
  .auth-hero {
    display: none;
  }
  .auth-panel {
    padding: 24px;
  }
}
</style>
