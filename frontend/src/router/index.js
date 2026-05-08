import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'questions',
        name: 'QuestionBank',
        component: () => import('../views/QuestionBank.vue'),
        meta: { title: '题库管理' },
      },
      {
        path: 'questions/generate',
        name: 'GenerateQuestion',
        component: () => import('../views/GenerateQuestion.vue'),
        meta: { title: 'AI 出题' },
      },
      {
        path: 'exams',
        name: 'ExamPapers',
        component: () => import('../views/ExamPapers.vue'),
        meta: { title: '试卷管理' },
      },
      {
        path: 'exams/create',
        name: 'CreateExam',
        component: () => import('../views/CreateExam.vue'),
        meta: { title: '创建试卷' },
      },
      {
        path: 'exams/:id',
        name: 'ExamDetail',
        component: () => import('../views/ExamDetail.vue'),
        meta: { title: '试卷详情' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
