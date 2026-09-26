<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">管理后台登录</h1>
      <el-form label-position="top" @submit.prevent>
        <el-form-item>
          <el-input v-model="form.username" placeholder="管理员账号" size="large" @keyup.enter="submit" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="密码"
            size="large"
            @keyup.enter="submit"
          />
        </el-form-item>
        <el-button type="danger" size="large" style="width: 100%" :loading="loading" @click="submit">
          登录
        </el-button>
        <div class="auth-actions">
          <el-button text @click="help">帮助</el-button>
          <span class="spacer" />
          <router-link class="auth-link" to="/login">返回客户入口</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { adminLogin } from '@/api/admin'
import { useAdminStore } from '@/stores/admin'

const router = useRouter()
const store = useAdminStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

onMounted(() => {
  if (store.token) router.push('/admin/data')
})

async function submit() {
  if (!form.username.trim()) {
    ElMessage.error('请输入管理员账号')
    return
  }
  if (!form.password) {
    ElMessage.error('请输入密码')
    return
  }
  loading.value = true
  try {
    const res = await adminLogin({ username: form.username, password: form.password })
    store.setAuth(res.data)
    ElMessage.success('登录成功')
    router.push('/admin/data')
  } catch (e) {
    // 拦截器已提示（5001/5002）
  } finally {
    loading.value = false
  }
}

function help() {
  ElMessageBox.alert('管理员账号由系统初始化创建，请联系系统管理员获取账号信息。', '帮助', {
    confirmButtonText: '知道了',
  })
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fdeeee 0%, #f5f7fa 100%);
}
.auth-card {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px 28px;
  box-shadow: 0 8px 30px rgba(31, 45, 61, 0.12);
}
.auth-title {
  text-align: center;
  font-size: 22px;
  margin: 0 0 28px;
  color: var(--el-color-danger);
}
.auth-actions {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.spacer {
  flex: 1;
}
.auth-link {
  font-size: 14px;
  color: var(--el-color-primary);
  text-decoration: none;
}
</style>
