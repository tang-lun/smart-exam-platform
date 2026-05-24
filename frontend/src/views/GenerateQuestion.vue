<template>
  <div class="generate-question">
    <el-card shadow="never">
      <template #header>AI 智能出题</template>
      <el-form :model="form" label-width="100px" class="generate-form">
        <el-form-item label="知识点">
          <el-select
            v-model="form.knowledge_points"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入知识点后按回车，如：一元一次方程"
            style="width: 100%"
          >
            <el-option
              v-for="kp in knowledgeOptions"
              :key="kp"
              :label="kp"
              :value="kp"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="题型">
              <el-select v-model="form.question_type" style="width: 100%">
                <el-option label="选择题" value="choice" />
                <el-option label="填空题" value="fill_blank" />
                <el-option label="计算题" value="calculation" />
                <el-option label="证明题" value="proof" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="数量">
              <el-input-number v-model="form.count" :min="1" :max="maxCount" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="难度">
              <el-select v-model="form.difficulty" style="width: 100%">
                <el-option label="基础" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="较难" value="hard" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="学段">
              <el-select v-model="form.grade_level" style="width: 100%">
                <el-option label="初一" value="grade_7" />
                <el-option label="初二" value="grade_8" />
                <el-option label="初三" value="grade_9" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleGenerate">
            <el-icon><MagicStick /></el-icon> 开始生成
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div v-if="generatedQuestions.length" class="result-section">
      <div class="result-header">
        <h3>生成结果（{{ generatedQuestions.length }} 题）</h3>
        <el-tag type="success">已自动保存到题库</el-tag>
      </div>
      <QuestionCard
        v-for="(q, i) in generatedQuestions"
        :key="i"
        :question="q"
        :index="i + 1"
        :show-answer="true"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { generateQuestions } from '../api'
import { ElMessage } from 'element-plus'
import QuestionCard from '../components/QuestionCard.vue'
import { GRADE_KNOWLEDGE } from '../constants'

const form = ref({
  knowledge_points: [],
  question_type: 'choice',
  count: 5,
  difficulty: 'medium',
  grade_level: 'grade_7',
})

const knowledgeOptions = computed(() => GRADE_KNOWLEDGE[form.value.grade_level] || [])

// 切换年级时清空知识点
watch(() => form.value.grade_level, () => {
  form.value.knowledge_points = []
})

const maxCount = computed(() => {
  if (form.value.question_type === 'proof') return 3
  if (form.value.question_type === 'calculation') return 5
  return 10
})

watch(() => form.value.question_type, (t) => {
  if (t === 'proof' && form.value.count > 3) form.value.count = 3
  if (t === 'calculation' && form.value.count > 5) form.value.count = 5
})

const loading = ref(false)
const generatedQuestions = ref([])

async function handleGenerate() {
  if (!form.value.knowledge_points.length) {
    ElMessage.warning('请至少输入一个知识点')
    return
  }

  loading.value = true

  try {
    const { data } = await generateQuestions(form.value)
    generatedQuestions.value = data
    ElMessage.success(`成功生成 ${data.length} 道题目`)
  } catch (e) {
    let msg = e.response?.data?.detail
    if (msg) {
      // Pydantic 422: detail is an array, extract the first item's msg
      if (Array.isArray(msg)) {
        msg = msg[0]?.msg || JSON.stringify(msg)
      }
      // Strip "Value error, " prefix from Pydantic
      if (typeof msg === 'string') {
        msg = msg.replace(/^Value error,\s*/, '')
      }
      ElMessage.error(msg)
    } else {
      ElMessage.error(e.message || '生成失败，请确认后端服务已启动且 API Key 已配置')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.generate-form {
  max-width: 900px;
}

.result-section {
  margin-top: 24px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.result-header h3 {
  margin: 0;
}
</style>
