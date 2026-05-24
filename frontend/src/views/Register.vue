<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="always">
      <template #header>
        <div class="auth-header">
          <span class="logo-icon">&#9998;</span>
          <h2>注册账号</h2>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="再次输入密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="form.role">
            <el-radio value="teacher">教师</el-radio>
            <el-radio value="student">学生</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div style="text-align:center">
        <span style="color:#909399">已有账号？</span>
        <el-link type="primary" @click="$router.push('/login')">去登录</el-link>
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

const formRef = ref(null)
const form = reactive({ username: '', password: '', confirmPassword: '', role: 'teacher' })
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少2个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (_, v, cb) => v === form.password ? cb() : cb(new Error('两次密码不一致')), trigger: 'blur' },
  ],
}
const loading = ref(false)

async function handleRegister() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await auth.register(form.username, form.password, form.role)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (err) {
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      ElMessage.error(detail.map(e => e.msg).join('；') || '注册失败')
    } else {
      ElMessage.error(detail || '注册失败')
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
