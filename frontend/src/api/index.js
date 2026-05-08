import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// Question APIs
export function generateQuestions(data) {
  return api.post('/questions/generate', data)
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

export default api
