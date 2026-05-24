<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span class="logo-icon">✏️</span>
        <span class="logo-text">智能题库平台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#1a1a2e"
        text-color="#a0a0b8"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/questions/generate">
          <el-icon><MagicStick /></el-icon>
          <span>AI 出题</span>
        </el-menu-item>
        <el-menu-item index="/favorites">
          <el-icon><Star /></el-icon>
          <span>我的收藏</span>
        </el-menu-item>
        <el-menu-item index="/questions">
          <el-icon><Collection /></el-icon>
          <span>题库管理</span>
        </el-menu-item>
        <el-menu-item index="/exams/create">
          <el-icon><DocumentAdd /></el-icon>
          <span>创建试卷</span>
        </el-menu-item>
        <el-menu-item index="/exams">
          <el-icon><Files /></el-icon>
          <span>试卷管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="topbar">
        <h2 class="page-title">{{ $route.meta.title }}</h2>
        <div style="flex:1" />
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="user-area">
            <el-icon style="margin-right:4px"><UserFilled /></el-icon>
            {{ auth.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const activeMenu = computed(() => route.path)

function handleCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f0f2f5;
}

.app-layout {
  min-height: 100vh;
}

.sidebar {
  background: #1a1a2e !important;
  overflow-x: hidden;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  color: #fff;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar .el-menu {
  border-right: none;
}

.sidebar .el-menu-item {
  font-size: 14px;
}

.sidebar .el-menu-item.is-active {
  background-color: #16213e !important;
}

.topbar {
  background: #fff;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  height: 56px;
}

.user-area {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}
.user-area:hover {
  color: #409eff;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.main-content {
  padding: 24px;
  min-height: calc(100vh - 56px);
}
</style>
