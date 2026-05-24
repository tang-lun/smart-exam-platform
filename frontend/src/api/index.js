import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// 响应拦截：401 跳转登录页
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

// Auth APIs
export function loginApi(data) {
  return api.post('/auth/login', data)
}
export function registerApi(data) {
  return api.post('/auth/register', data)
}

// Question APIs
export function generateQuestions(data) {
  return api.post('/questions/generate', data)
}
export function createManualQuestion(data) {
  return api.post('/questions/manual', data)
}
export function validateQuestion(data) {
  return api.post('/questions/validate', data)
}
export function getQuestions(params) {
  return api.get('/questions', { params })
}
export function getQuestion(id) {
  return api.get(`/questions/${id}`)
}
export function updateQuestion(id, data) {
  return api.put(`/questions/${id}`, data)
}
export function deleteQuestion(id) {
  return api.delete(`/questions/${id}`)
}
export function toggleFavorite(id) {
  return api.post(`/questions/${id}/favorite`)
}
export function getFavorites(params) {
  return api.get('/questions/favorites/list', { params })
}
export function importQuestions(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/questions/import', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export function downloadTemplate() {
  return api.get('/questions/template/download', { responseType: 'blob' })
}

// Exam APIs
export function createExam(data) {
  return api.post('/exams', data)
}
export function getExams() {
  return api.get('/exams')
}
export function getExam(id) {
  return api.get(`/exams/${id}`)
}
export function deleteExam(id) {
  return api.delete(`/exams/${id}`)
}

export function getStats() {
  return api.get('/stats')
}

export function exportExam(id) {
  return api.get(`/exams/${id}/export`, { responseType: 'blob' })
}
export function analyzeExam(id) {
  return api.get(`/exams/${id}/analyze`)
}
export function submitExam(id, data) {
  return api.post(`/exams/${id}/submit`, data)
}
export function getExamResults(id) {
  return api.get(`/exams/${id}/results`)
}
export function getMyResults() {
  return api.get('/exams/results/mine')
}

export default api
