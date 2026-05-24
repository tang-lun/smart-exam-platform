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
            <div>
              <el-button type="success" @click="$router.push(`/exams/${exam.id}/take`)">
                <el-icon><EditPen /></el-icon> 在线答卷
              </el-button>
              <el-button :loading="analyzing" @click="handleAnalyze">
                <el-icon><DataAnalysis /></el-icon> AI 分析
              </el-button>
              <el-button type="primary" :loading="exporting" @click="handleExport">
                <el-icon><Download /></el-icon> 导出 Word
              </el-button>
              <el-tag size="large" style="margin-left: 12px">总分 {{ exam.total_score }} 分</el-tag>
            </div>
          </div>
        </template>
        <p v-if="exam.description" class="exam-desc">{{ exam.description }}</p>
        <div class="exam-meta">
          <span>题量：{{ exam.question_ids?.length || 0 }} 题</span>
          <span>时长：{{ exam.duration_minutes }} 分钟</span>
          <span>创建时间：{{ new Date(exam.created_at).toLocaleString('zh-CN') }}</span>
        </div>
      </el-card>

      <el-card v-if="analysis" shadow="hover" class="analysis-card" style="margin-top: 20px">
        <template #header>📊 试卷分析报告</template>
        <el-row :gutter="24">
          <el-col :span="8">
            <div class="metric">
              <div class="metric-value" :style="{ color: diffColor(analysis.difficulty_score) }">{{ analysis.difficulty_score || 0 }}</div>
              <div class="metric-label">难度指数 / 100</div>
              <el-tag :type="diffTag(analysis.difficulty_score)">{{ analysis.difficulty_label }}</el-tag>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric">
              <div class="metric-value" style="color:#409eff">{{ analysis.overall_score || 0 }}</div>
              <div class="metric-label">综合质量 / 100</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric">
              <div class="metric-text">{{ analysis.suitable_for || '--' }}</div>
              <div class="metric-label">适合学生群体</div>
            </div>
          </el-col>
        </el-row>
        <el-divider />
        <p style="color:#606266; margin-bottom:12px">{{ analysis.summary }}</p>
        <el-row :gutter="24">
          <el-col :span="12">
            <h4 style="color:#67c23a; margin-bottom:8px">✅ 优点</h4>
            <ul v-if="analysis.strengths?.length">
              <li v-for="s in analysis.strengths" :key="s" style="margin-bottom:4px">{{ s }}</li>
            </ul>
            <span v-else style="color:#909399">暂无</span>
          </el-col>
          <el-col :span="12">
            <h4 style="color:#f56c6c; margin-bottom:8px">⚠️ 不足</h4>
            <ul v-if="analysis.weaknesses?.length">
              <li v-for="w in analysis.weaknesses" :key="w" style="margin-bottom:4px">{{ w }}</li>
            </ul>
            <span v-else style="color:#909399">暂无</span>
          </el-col>
        </el-row>
      </el-card>

      <div class="question-list" style="margin-top: 20px">
        <QuestionCard
          v-for="(q, i) in exam.questions"
          :key="q.id"
          :question="q"
          :index="i + 1"
          :score="Number(exam.question_scores?.[i] || 0)"
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
import { getExam, exportExam, analyzeExam } from '../api'
import { ElMessage } from 'element-plus'
import QuestionCard from '../components/QuestionCard.vue'

const route = useRoute()
const exam = ref(null)
const loading = ref(false)
const analyzing = ref(false)
const exporting = ref(false)
const analysis = ref(null)

async function handleAnalyze() {
  analyzing.value = true
  try {
    const { data } = await analyzeExam(route.params.id)
    analysis.value = data
    ElMessage.success('分析完成')
  } catch { ElMessage.error('分析失败') }
  finally { analyzing.value = false }
}

function diffColor(score) {
  if (score < 35) return '#67c23a'
  if (score < 65) return '#e6a23c'
  return '#f56c6c'
}
function diffTag(score) {
  if (score < 35) return 'success'
  if (score < 65) return 'warning'
  return 'danger'
}

async function handleExport() {
  exporting.value = true
  try {
    const { data, headers } = await exportExam(route.params.id)
    const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    // Extract filename from Content-Disposition header
    const disposition = headers['content-disposition'] || ''
    const match = disposition.match(/filename\*=UTF-8''(.+)/)
    a.download = match ? decodeURIComponent(match[1]) : '试卷.docx'
    a.href = url
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

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
