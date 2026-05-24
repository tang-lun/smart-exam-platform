<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="always">
      <template #header>
        <div class="auth-header">
          <span class="logo-icon">&#9998;</span>
          <h2>智能题库平台</h2>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div style="text-align:center">
        <span style="color:#909399">还没有账号？</span>
        <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const loading = ref(false)

const formRef = ref(null)

async function handleLogin() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (err) {
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      ElMessage.error(detail.map(e => e.msg).join('；') || '登录失败')
    } else {
      ElMessage.error(detail || '登录失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
.auth-card {
  width: 400px;
}
.auth-header {
  text-align: center;
}
.auth-header .logo-icon {
  font-size: 36px;
}
.auth-header h2 {
  margin: 8px 0 0;
  font-size: 20px;
  color: #303133;
}
</style>
