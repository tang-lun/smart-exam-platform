<template>
  <div class="create-exam">
    <el-card shadow="never">
      <template #header>创建试卷</template>
      <el-form :model="form" label-width="120px" class="exam-form">
        <el-form-item label="试卷名称" required>
          <el-input v-model="form.title" placeholder="如：初一数学一元一次方程单元测试" />
        </el-form-item>
        <el-form-item label="试卷说明">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="可选填试卷说明" />
        </el-form-item>
        <el-form-item label="总分">
          <el-input-number v-model="form.total_score" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="建议时长(分钟)">
          <el-input-number v-model="form.duration_minutes" :min="5" :max="300" />
        </el-form-item>

        <el-divider />

        <el-radio-group v-model="composeMode" class="mode-switch">
          <el-radio-button value="auto">AI 自动组卷</el-radio-button>
          <el-radio-button value="manual">手动选题</el-radio-button>
        </el-radio-group>

        <!-- AI 组卷配置 -->
        <template v-if="composeMode === 'auto'">
          <el-form-item label="知识点范围" style="margin-top: 16px">
            <el-select
              v-model="form.knowledge_points"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="留空则从全题库选题"
              style="width: 100%"
            >
              <el-option v-for="kp in knowledgeOptions" :key="kp" :label="kp" :value="kp" />
            </el-select>
          </el-form-item>
          <el-form-item label="题目总数">
            <el-input-number v-model="form.question_count" :min="1" :max="50" />
          </el-form-item>
          <el-form-item label="难度分布">
            <div class="diff-bar">
              <span>基础: {{ form.difficulty_distribution.easy }}%</span>
              <el-slider
                v-model="form.difficulty_distribution.easy"
                :max="100"
                :show-input="false"
                @change="adjustDiff"
              />
              <span>中等: {{ form.difficulty_distribution.medium }}%</span>
              <el-slider
                v-model="form.difficulty_distribution.medium"
                :max="100"
                :show-input="false"
                @change="adjustDiff"
              />
              <span>较难: {{ form.difficulty_distribution.hard }}%</span>
              <el-slider
                v-model="form.difficulty_distribution.hard"
                :max="100"
                :show-input="false"
                @change="adjustDiff"
              />
            </div>
          </el-form-item>
        </template>

        <!-- 手动选题 -->
        <template v-if="composeMode === 'manual'">
          <el-form-item label="选择题目" style="margin-top: 16px">
            <div class="manual-select">
              <div class="select-toolbar">
                <el-input v-model="qKeyword" placeholder="搜索题目..." clearable style="width: 240px" />
                <el-select v-model="qType" placeholder="题型" clearable style="width: 120px">
                  <el-option label="选择题" value="choice" />
                  <el-option label="填空题" value="fill_blank" />
                  <el-option label="计算题" value="calculation" />
                  <el-option label="证明题" value="proof" />
                </el-select>
              </div>
              <el-table
                :data="availableQuestions"
                v-loading="qLoading"
                @selection-change="onSelectionChange"
                ref="tableRef"
                max-height="400"
                stripe
              >
                <el-table-column type="selection" width="50" />
                <el-table-column prop="id" label="ID" width="50" />
                <el-table-column label="题型" width="80">
                  <template #default="{ row }">
                    <el-tag size="small">{{ typeLabel(row.type) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="stem" label="题干" min-width="250" show-overflow-tooltip />
                <el-table-column label="难度" width="80">
                  <template #default="{ row }">
                    <el-tag :type="diffType(row.difficulty)" size="small">{{ diffLabel(row.difficulty) }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <div class="selected-count">已选 {{ selectedQuestions.length }} 题</div>
            </div>
          </el-form-item>
        </template>

        <el-form-item style="margin-top: 24px">
          <el-button type="primary" size="large" :loading="submitting" @click="handleCreate">
            创建试卷
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createExam, getQuestions } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()

const knowledgeOptions = [
  '一元一次方程', '二元一次方程组', '一元二次方程', '不等式', '勾股定理',
  '三角形', '四边形', '圆', '一次函数', '二次函数', '统计', '概率',
]

const composeMode = ref('auto')
const submitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  question_ids: [],
  total_score: 100,
  duration_minutes: 60,
  knowledge_points: [],
  difficulty_distribution: { easy: 30, medium: 50, hard: 20 },
  question_count: 10,
})

// Manual selection state
const availableQuestions = ref([])
const selectedQuestions = ref([])
const qKeyword = ref('')
const qType = ref('')
const qLoading = ref(false)
const tableRef = ref(null)

function typeLabel(type) {
  const map = { choice: '选择题', fill_blank: '填空题', calculation: '计算题', proof: '证明题' }
  return map[type] || type
}

function diffLabel(d) {
  const map = { easy: '基础', medium: '中等', hard: '较难' }
  return map[d] || d
}

function diffType(d) {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[d] || 'info'
}

function adjustDiff() {
  // Normalize to 100
  const { easy, medium, hard } = form.difficulty_distribution
  const total = easy + medium + hard
  if (total === 0) {
    form.difficulty_distribution = { easy: 33, medium: 34, hard: 33 }
  } else if (total !== 100) {
    const scale = 100 / total
    form.difficulty_distribution.easy = Math.round(easy * scale)
    form.difficulty_distribution.medium = Math.round(medium * scale)
    form.difficulty_distribution.hard = 100 - form.difficulty_distribution.easy - form.difficulty_distribution.medium
  }
}

function onSelectionChange(rows) {
  selectedQuestions.value = rows
}

async function fetchAvailableQuestions() {
  qLoading.value = true
  try {
    const params = { page_size: 100 }
    if (qKeyword.value) params.keyword = qKeyword.value
    if (qType.value) params.question_type = qType.value
    const { data } = await getQuestions(params)
    availableQuestions.value = data.items
  } catch (e) {
    ElMessage.error('获取题目列表失败')
  } finally {
    qLoading.value = false
  }
}

watch([qKeyword, qType], () => {
  fetchAvailableQuestions()
})

async function handleCreate() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入试卷名称')
    return
  }

  submitting.value = true

  try {
    const payload = { ...form }
    if (composeMode.value === 'manual') {
      payload.question_ids = selectedQuestions.value.map(q => q.id)
      payload.question_count = 0
      payload.knowledge_points = []
    }

    const { data } = await createExam(payload)
    ElMessage.success('试卷创建成功')
    router.push(`/exams/${data.id}`)
  } catch (e) {
    const detail = e.response?.data?.detail
    ElMessage.error(detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchAvailableQuestions()
})
</script>

<style scoped>
.exam-form {
  max-width: 800px;
}

.mode-switch {
  margin-bottom: 8px;
}

.diff-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.manual-select {
  width: 100%;
}

.select-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.selected-count {
  margin-top: 8px;
  color: #606266;
}
</style>
