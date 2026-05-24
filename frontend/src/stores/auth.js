import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { loginApi, registerApi } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')
  const role = computed(() => user.value?.role || '')

  function setAuth(t, u) {
    token.value = t
    user.value = u
    localStorage.setItem('token', t)
    localStorage.setItem('user', JSON.stringify(u))
    api.defaults.headers.common['Authorization'] = `Bearer ${t}`
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete api.defaults.headers.common['Authorization']
  }

  async function login(username, password) {
    const { data } = await loginApi({ username, password })
    setAuth(data.access_token, data.user)
    return data
  }

  async function register(username, password, role) {
    const { data } = await registerApi({ username, password, role })
    setAuth(data.access_token, data.user)
    return data
  }

  async function fetchMe() {
    try {
      const { data } = await api.get('/auth/me')
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
    } catch {
      clearAuth()
    }
  }

  function logout() {
    clearAuth()
  }

  // init axios header if token exists
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  return { token, user, isLoggedIn, username, role, login, register, fetchMe, logout }
})
