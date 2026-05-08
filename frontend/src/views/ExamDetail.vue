<template>
  <div class="exam-detail" v-loading="loading">
    <el-button text @click="$router.back()" style="margin-bottom: 16px">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>

    <template v-if="exam">
      <el-card shadow="never" class="exam-info">
        <template #header>
          <div class="info-header">
            <h2>{{ exam.title }}</h2>
            <el-tag size="large">总分 {{ exam.total_score }} 分</el-tag>
          </div>
        </template>
        <p v-if="exam.description" class="exam-desc">{{ exam.description }}</p>
        <div class="exam-meta">
          <span>题量：{{ exam.question_ids?.length || 0 }} 题</span>
          <span>时长：{{ exam.duration_minutes }} 分钟</span>
          <span>创建时间：{{ new Date(exam.created_at).toLocaleString('zh-CN') }}</span>
        </div>
      </el-card>

      <div class="question-list" style="margin-top: 20px">
        <QuestionCard
          v-for="(q, i) in exam.questions"
          :key="q.id"
          :question="q"
          :index="i + 1"
          :show-answer="true"
        />
      </div>

      <el-empty v-if="!exam.questions?.length" description="试卷中没有题目" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExam } from '../api'
import { ElMessage } from 'element-plus'
import QuestionCard from '../components/QuestionCard.vue'

const route = useRoute()
const exam = ref(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await getExam(route.params.id)
    exam.value = data
  } catch (e) {
    ElMessage.error('获取试卷详情失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exam-desc {
  color: #606266;
  margin-bottom: 12px;
}

.exam-meta {
  display: flex;
  gap: 24px;
  color: #909399;
  font-size: 14px;
}
</style>
