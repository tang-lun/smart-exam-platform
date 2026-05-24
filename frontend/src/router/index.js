import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册', guest: true },
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'favorites',
        name: 'Favorites',
        component: () => import('../views/Favorites.vue'),
        meta: { title: '我的收藏' },
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
      {
        path: 'exams/:id/take',
        name: 'ExamTake',
        component: () => import('../views/ExamTake.vue'),
        meta: { title: '在线答卷' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return '/login'
  }
  if (to.meta.guest && token) {
    return '/'
  }
})

export default router
