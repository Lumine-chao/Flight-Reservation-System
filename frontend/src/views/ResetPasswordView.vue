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
        <h1 class="hero-title">找回密码</h1>
        <p class="hero-sub">
          通过回答注册时设置的安全问题验证身份，即可安全重置登录密码。全程加密，放心使用。
        </p>
        <ul class="hero-features">
          <li>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            安全问题验证 · 两步完成
          </li>
          <li>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            密码加密存储 · 全程安全
          </li>
          <li>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            重置后即可重新登录
          </li>
        </ul>
      </div>
    </div>

    <!-- 右侧重置表单 -->
    <div class="auth-panel">
      <div class="auth-card">
        <h2 class="card-title">重置密码</h2>
        <p class="card-sub">{{ step === 'username' ? '输入用户名开始验证' : '回答安全问题并设置新密码' }}</p>

        <template v-if="step === 'username'">
          <el-input v-model="username" placeholder="用户名" size="large" @keyup.enter="fetchQuestion" />
          <el-button type="primary" size="large" style="width: 100%; margin-top: 16px" :loading="loading" @click="fetchQuestion">
            下一步
          </el-button>
          <el-button text type="info" style="width: 100%; margin-top: 8px" @click="goLogin">返回登录</el-button>
        </template>

        <template v-else-if="step === 'answer'">
          <el-form label-position="top" @submit.prevent>
            <el-form-item label="安全问题">
              <el-input :model-value="question" disabled />
            </el-form-item>
            <el-form-item label="答案">
              <el-input v-model="answer" placeholder="请输入安全问题答案" size="large" @keyup.enter="submit" />
            </el-form-item>
            <el-form-item label="新密码（8～20位，需同时包含字母与数字）">
              <el-input v-model="newPassword" type="password" show-password size="large" />
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="confirmPassword" type="password" show-password size="large" />
            </el-form-item>
            <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="submit">
              重置密码
            </el-button>
            <el-button text type="info" style="width: 100%; margin-top: 8px" @click="back">返回上一步</el-button>
          </el-form>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { getSecurityQuestion, resetPassword } from '@/api/auth'
import { validatePasswordStrength } from '@/utils/validators'

const router = useRouter()
const step = ref('username')
const loading = ref(false)
const username = ref('')
const question = ref('')
const answer = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

async function fetchQuestion() {
  if (!username.value) {
    ElMessage.error('请输入用户名')
    return
  }
  loading.value = true
  try {
    const res = await getSecurityQuestion(username.value)
    question.value = res.data.securityQuestion
    step.value = 'answer'
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

function back() {
  step.value = 'username'
  answer.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
}

function goLogin() {
  router.push('/login')
}

async function submit() {
  if (!answer.value) {
    ElMessage.error('请输入安全问题答案')
    return
  }
  const p = validatePasswordStrength(newPassword.value)
  if (p) {
    ElMessage.error(p.message)
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    ElMessage.error('两次输入的密码不一致，请重新输入')
    return
  }
  loading.value = true
  try {
    const res = await resetPassword({
      username: username.value,
      securityAnswer: answer.value,
      newPassword: newPassword.value,
    })
    ElMessage.success(res.message)
    router.push('/login')
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
  max-width: 400px;
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
.auth-card :deep(.el-input__inner) {
  font-size: 15px;
  height: 42px;
}
.auth-card :deep(.el-button--primary) {
  font-size: 16px;
  height: 44px;
  letter-spacing: 2px;
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
