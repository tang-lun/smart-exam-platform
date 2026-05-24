<template>
  <div class="exam-take" v-loading="loading">
    <template v-if="!submitted">
      <!-- 倒计时条 -->
      <div class="timer-bar" :class="timerClass" v-if="remainingSeconds > 0 || !timerExpired">
        <div class="timer-inner">
          <span class="timer-icon">⏱</span>
          <span class="timer-label">{{ timerExpired ? '考试结束' : '剩余时间' }}</span>
          <span class="timer-clock">{{ timerDisplay }}</span>
        </div>
      </div>

      <el-card shadow="never" class="exam-header">
        <template #header>
          <div class="take-header">
            <h2>{{ exam?.title }}</h2>
            <div>
              <el-tag>总分 {{ exam?.total_score }} 分</el-tag>
              <el-tag type="warning" style="margin-left:8px">{{ exam?.duration_minutes }} 分钟</el-tag>
              <el-tag type="info" style="margin-left:8px">{{ exam?.questions?.length || 0 }} 题</el-tag>
            </div>
          </div>
        </template>
        <p v-if="exam?.description" style="color:#606266">{{ exam.description }}</p>
      </el-card>

      <div class="question-list">
        <el-card v-for="(q, i) in exam?.questions || []" :key="q.id" shadow="hover" class="q-card">
          <template #header>
            <div class="q-header">
              <span class="q-index">第 {{ i + 1 }} 题</span>
              <el-tag size="small">{{ typeLabel(q.type) }}</el-tag>
              <el-tag size="small" :type="diffType(q.difficulty)" style="margin-left:4px">{{ diffLabel(q.difficulty) }}</el-tag>
              <span style="margin-left:auto; color:#909399; font-size:12px">{{ scorePerQuestion(i) }} 分</span>
            </div>
          </template>
          <div class="stem" v-html="renderMath(q.stem)"></div>

          <!-- 选择题 -->
          <template v-if="q.type === 'choice' && q.options?.length">
            <el-radio-group v-model="answers[i]" class="options-group">
              <el-radio
                v-for="(opt, oi) in q.options"
                :key="oi"
                :value="String.fromCharCode(65 + oi)"
                class="option-radio"
              >
                <span v-html="renderMath(opt)"></span>
              </el-radio>
            </el-radio-group>
          </template>

          <!-- 填空题 -->
          <template v-else-if="q.type === 'fill_blank'">
            <el-input v-model="answers[i]" placeholder="请输入答案" style="max-width:400px" />
          </template>

          <!-- 计算题/证明题 -->
          <template v-else>
            <el-input v-model="answers[i]" type="textarea" :rows="3" placeholder="请输入答案或证明过程" style="max-width:600px" />
          </template>
        </el-card>
      </div>

      <div style="text-align:center; margin:24px 0">
        <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
          提交答卷
        </el-button>
      </div>
    </template>

    <!-- 成绩页 -->
    <template v-else>
      <el-card shadow="never">
        <template #header>
          <div style="text-align:center">
            <h2>答卷成绩</h2>
          </div>
        </template>
        <div style="text-align:center; padding:40px 0">
          <div class="score-circle" :style="{ borderColor: scoreColor }">
            <div class="score-num" :style="{ color: scoreColor }">{{ score }}</div>
            <div class="score-label">得分</div>
          </div>
          <p style="font-size:18px; margin-top:16px">
            共 {{ exam?.questions?.length || 0 }} 题，答对 <span style="color:#67c23a; font-weight:bold">{{ correct }}</span> 题，
            得分率 <span :style="{ color: scoreColor, fontWeight:'bold' }">{{ pct }}%</span>
          </p>
          <el-button type="primary" style="margin-top:16px" @click="$router.back()">返回试卷</el-button>
        </div>
      </el-card>

      <el-card shadow="hover" style="margin-top:20px">
        <template #header>答题详情</template>
        <div v-for="(q, i) in exam?.questions || []" :key="q.id" class="review-item">
          <div class="review-header">
            <span :class="results[i]?.correct ? 'correct' : 'wrong'">
              {{ results[i]?.correct ? '✅' : '❌' }} 第 {{ i + 1 }} 题
            </span>
            <el-tag size="small">{{ typeLabel(q.type) }}</el-tag>
          </div>
          <div class="stem" v-html="renderMath(q.stem)"></div>
          <div v-if="!results[i]?.correct" style="margin-top:4px">
            <span style="color:#909399">你的答案：</span>
            <span style="color:#f56c6c" v-html="renderMath(answers[i] || '未作答')"></span>
          </div>
          <div style="margin-top:4px">
            <span style="color:#909399">正确答案：</span>
            <span style="color:#67c23a; font-weight:500" v-html="renderMath(q.answer)"></span>
          </div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { getExam, submitExam } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { renderMath } from '../utils/math'

const route = useRoute()
const exam = ref(null)
const loading = ref(false)
const answers = ref({})
const submitted = ref(false)
const submitting = ref(false)
const score = ref(0)
const correct = ref(0)
const results = ref([])
const examStartedAt = ref(null)  // ISO 时间戳，提交时送服务端校验超时

// 倒计时
const remainingSeconds = ref(0)
const timerExpired = ref(false)
let timerInterval = null
let timerPaused = false

const timerDisplay = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60)
  const s = remainingSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const timerClass = computed(() => {
  if (timerExpired.value) return 'timer-danger'
  if (remainingSeconds.value <= 300) return 'timer-danger'  // < 5 分钟
  if (remainingSeconds.value <= 600) return 'timer-warning' // < 10 分钟
  return 'timer-normal'
})

function startTimer() {
  const examId = exam.value?.id
  const key = `exam_timer_${examId}`
  const minutes = exam.value?.duration_minutes || 60

  // 检查是否有已保存的截止时间（刷新恢复）
  const saved = localStorage.getItem(key)
  const savedStart = localStorage.getItem(key + '_start')
  if (saved) {
    const endTime = parseInt(saved, 10)
    const now = Date.now()
    if (now < endTime) {
      remainingSeconds.value = Math.ceil((endTime - now) / 1000)
      examStartedAt.value = savedStart || new Date(now - (minutes * 60 - remainingSeconds.value) * 1000).toISOString()
    } else {
      // 时间已过，直接交卷
      remainingSeconds.value = 0
      timerExpired.value = true
      examStartedAt.value = savedStart || null
      doSubmit(true)
      return
    }
  } else {
    // 首次开始：保存截止时间和开始时间
    const startedAt = new Date().toISOString()
    const endTime = Date.now() + minutes * 60 * 1000
    localStorage.setItem(key, String(endTime))
    localStorage.setItem(key + '_start', startedAt)
    remainingSeconds.value = minutes * 60
    examStartedAt.value = startedAt
  }

  timerInterval = setInterval(() => {
    if (timerPaused) return
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--
    }
    if (remainingSeconds.value <= 0) {
      clearInterval(timerInterval)
      timerExpired.value = true
      doSubmit(true)
    }
  }, 1000)
}

const scorePerQuestion = computed(() => {
  const scores = exam.value?.question_scores || {}
  const qs = exam.value?.questions || []
  const fallback = Math.round((exam.value?.total_score || 100) / (qs.length || 1))
  return (i) => {
    const val = scores[i]
    return val != null ? Number(val) : fallback
  }
})

const pct = computed(() => {
  const n = exam.value?.questions?.length || 1
  return Math.round(correct.value / n * 100)
})

const scoreColor = computed(() => {
  if (pct.value >= 80) return '#67c23a'
  if (pct.value >= 60) return '#e6a23c'
  return '#f56c6c'
})

function typeLabel(t) {
  const map = { choice: '选择题', fill_blank: '填空题', calculation: '计算题', proof: '证明题' }
  return map[t] || t
}
function diffLabel(d) {
  const map = { easy: '基础', medium: '中等', hard: '较难' }
  return map[d] || d
}
function diffType(d) {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[d] || 'info'
}
function handleSubmit() {
  // 立刻停表
  timerPaused = true
  ElMessageBox.confirm('确定提交答卷？提交后不可修改。', '确认提交', {
    confirmButtonText: '确定', cancelButtonText: '继续检查', type: 'warning'
  }).then(() => {
    if (timerInterval) clearInterval(timerInterval)
    doSubmit(false)
  }).catch(() => {
    timerPaused = false // 取消，恢复计时
  })
}

async function doSubmit(isAuto) {
  if (submitted.value) return
  if (timerInterval) clearInterval(timerInterval)
  timerPaused = true

  // 清除本地计时器
  const examId = exam.value?.id
  if (examId) {
    localStorage.removeItem(`exam_timer_${examId}`)
    localStorage.removeItem(`exam_timer_${examId}_start`)
  }

  submitting.value = true
  const qs = exam.value?.questions || []

  // 先提交到后端，使用后端返回的权威评分
  try {
    const answerMap = {}
    for (let i = 0; i < qs.length; i++) {
      answerMap[i] = answers.value[i] || ''
    }
    const { data } = await submitExam(route.params.id, {
      answers: answerMap,
      started_at: examStartedAt.value,
    })

    score.value = data.score
    correct.value = data.correct_count
    // 从后端返回的 answers 重建结果展示（后端 key 为字符串，前端 key 为数字）
    const rawAnswers = data.answers || {}
    results.value = qs.map((q, i) => {
      const entry = rawAnswers[i] || rawAnswers[String(i)] || {}
      return {
        correct: entry.correct || false,
        userAns: entry.user_ans || (answers.value[i] || ''),
        correctAns: entry.correct_ans || q.answer || '',
      }
    })
    submitted.value = true
  } catch {
    ElMessage.error('提交失败，请重试')
    submitted.value = false
    return
  } finally {
    submitting.value = false
  }

  if (isAuto) {
    ElMessage.warning('考试时间到，系统已自动交卷')
  } else {
    ElMessage.success(`得分：${score.value} 分`)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await getExam(route.params.id)
    exam.value = data
    startTimer()
  } catch { ElMessage.error('加载试卷失败') }
  finally { loading.value = false }
})

onBeforeUnmount(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.timer-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 12px 24px;
  margin-bottom: 16px;
  border-radius: 8px;
  text-align: center;
  transition: background 0.3s;
}
.timer-normal { background: #e1f3d8; }
.timer-warning { background: #fff3cd; }
.timer-danger {
  background: #fde2e2;
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.timer-inner { display: flex; align-items: center; justify-content: center; gap: 8px; }
.timer-icon { font-size: 20px; }
.timer-label { font-size: 14px; color: #606266; }
.timer-clock {
  font-size: 28px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
}
.timer-danger .timer-clock { color: #f56c6c; }
.timer-warning .timer-clock { color: #e6a23c; }
.timer-normal .timer-clock { color: #67c23a; }

.take-header { display: flex; justify-content: space-between; align-items: center; }
.q-card { margin-bottom: 16px; }
.q-header { display: flex; align-items: center; gap: 8px; }
.q-index { font-weight: 600; color: #409eff; }
.stem { font-size: 16px; line-height: 1.8; color: #303133; margin-bottom: 12px; }
.stem :deep(.katex) { font-size: 1.1em; }
.options-group { display: flex; flex-direction: column; gap: 8px; }
.option-radio { padding: 10px 16px; background: #f5f7fa; border-radius: 6px; margin: 0; width: 100%; }
.score-circle {
  width: 140px; height: 140px; border-radius: 50%; border: 6px solid;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  margin: 0 auto;
}
.score-num { font-size: 40px; font-weight: 700; }
.score-label { font-size: 14px; color: #909399; }
.review-item { padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.review-item:last-child { border-bottom: none; }
.review-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.correct { color: #67c23a; font-weight: 600; }
.wrong { color: #f56c6c; font-weight: 600; }
</style>
