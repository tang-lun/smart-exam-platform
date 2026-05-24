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
          <el-form-item label="学段" style="margin-top: 16px">
            <el-select v-model="form.grade_levels" multiple placeholder="留空则不限学段" style="width: 100%">
              <el-option label="初一" value="grade_7" />
              <el-option label="初二" value="grade_8" />
              <el-option label="初三" value="grade_9" />
            </el-select>
          </el-form-item>
          <el-form-item label="知识点范围">
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
          <el-form-item label="难度分布">
            <div class="diff-bar">
              <span>基础：</span>
              <el-input-number v-model="form.difficulty_distribution.easy" :min="0" :max="100" style="width:100px" />
              <span>%</span>
              <span style="margin-left:16px">中等：</span>
              <el-input-number v-model="form.difficulty_distribution.medium" :min="0" :max="100" style="width:100px" />
              <span>%</span>
              <span style="margin-left:16px">较难：</span>
              <el-input-number v-model="form.difficulty_distribution.hard" :min="0" :max="100" style="width:100px" />
              <span>%</span>
            </div>
          </el-form-item>
          <el-form-item label="题型分布">
            <div class="diff-bar">
              <span>选择题: {{ form.type_distribution.choice }} 题</span>
              <el-slider v-model="form.type_distribution.choice" :max="16" :min="0" :show-input="false" />
              <span>填空题: {{ form.type_distribution.fill_blank }} 题</span>
              <el-slider v-model="form.type_distribution.fill_blank" :max="10" :min="0" :show-input="false" />
              <span>计算题: {{ form.type_distribution.calculation }} 题</span>
              <el-slider v-model="form.type_distribution.calculation" :max="10" :min="0" :show-input="false" />
              <span>证明题: {{ form.type_distribution.proof }} 题</span>
              <el-slider v-model="form.type_distribution.proof" :max="3" :min="0" :show-input="false" />
              <span style="color:#909399">总题数：{{ totalQuestionCount }}</span>
            </div>
          </el-form-item>
        </template>

        <!-- 手动选题 -->
        <template v-if="composeMode === 'manual'">
          <el-form-item label="选择题目" style="margin-top: 16px">
            <div class="manual-select">
              <div class="select-toolbar">
                <el-input v-model="qKeyword" placeholder="搜索..." clearable style="width: 160px" />
                <el-select v-model="qType" placeholder="题型" clearable style="width: 100px">
                  <el-option label="选择题" value="choice" />
                  <el-option label="填空题" value="fill_blank" />
                  <el-option label="计算题" value="calculation" />
                  <el-option label="证明题" value="proof" />
                </el-select>
                <el-select v-model="qGrade" placeholder="学段" clearable style="width: 100px" @change="fetchAvailableQuestions">
                  <el-option label="初一" value="grade_7" />
                  <el-option label="初二" value="grade_8" />
                  <el-option label="初三" value="grade_9" />
                </el-select>
                <el-select v-model="qKnowledge" placeholder="知识点" clearable filterable style="width: 140px" @change="fetchAvailableQuestions">
                  <el-option v-for="kp in manualKnowledgeOptions" :key="kp" :label="kp" :value="kp" />
                </el-select>
                <el-checkbox v-model="qFavOnly" @change="fetchAvailableQuestions" border size="small" style="height:32px">
                  只看收藏
                </el-checkbox>
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
                <el-table-column label="#" width="50" align="center">
                  <template #default="{ $index }">{{ $index + 1 }}</template>
                </el-table-column>
                <el-table-column label="题型" width="80">
                  <template #default="{ row }">
                    <el-tag size="small">{{ typeLabel(row.type) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="题干" min-width="250" show-overflow-tooltip>
                  <template #default="{ row }">
                    <span class="stem-cell" v-html="renderMath(row.stem || '')"></span>
                  </template>
                </el-table-column>
                <el-table-column label="难度" width="80">
                  <template #default="{ row }">
                    <el-tag :type="diffType(row.difficulty)" size="small">{{ diffLabel(row.difficulty) }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <div class="selected-count">
                已选 {{ pickedQuestions.length }} 题
                <el-button v-if="pickedQuestions.length" size="small" text @click="pickedQuestions=[]">清空</el-button>
              </div>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createExam, getQuestions, getFavorites } from '../api'
import { ElMessage } from 'element-plus'
import { GRADE_KNOWLEDGE } from '../constants'
import { renderMath } from '../utils/math'

const router = useRouter()

const composeMode = ref('auto')
const submitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  question_ids: [],
  total_score: 150,
  duration_minutes: 120,
  knowledge_points: [],
  difficulty_distribution: { easy: 30, medium: 40, hard: 30 },
  type_distribution: { choice: 12, fill_blank: 4, calculation: 3, proof: 3 },
  grade_levels: [],
})

// AI 组卷知识点：根据已选学段动态过滤
const knowledgeOptions = computed(() => {
  const grades = form.grade_levels
  if (!grades.length) return Object.values(GRADE_KNOWLEDGE).flat()
  const set = new Set()
  grades.forEach(g => (GRADE_KNOWLEDGE[g] || []).forEach(kp => set.add(kp)))
  return [...set]
})

// 学段变化时清除不兼容的知识点
watch(() => form.grade_levels, () => {
  const valid = new Set(knowledgeOptions.value)
  form.knowledge_points = form.knowledge_points.filter(kp => valid.has(kp))
})

const totalQuestionCount = computed(() => {
  const td = form.type_distribution
  return td.choice + td.fill_blank + td.calculation + td.proof
})

// Manual selection state
const availableQuestions = ref([])
const pickedQuestions = ref([])  // 持久保存，不随筛选切换丢失
const pickedIds = computed(() => new Set(pickedQuestions.value.map(q => q.id)))
const qKeyword = ref('')
const qType = ref('')
const qGrade = ref('')
const qKnowledge = ref('')
const qFavOnly = ref(false)
const qLoading = ref(false)

// 手动选题知识点：跟学段联动
const manualKnowledgeOptions = computed(() => {
  if (qGrade.value) return GRADE_KNOWLEDGE[qGrade.value] || []
  return Object.values(GRADE_KNOWLEDGE).flat()
})
const tableRef = ref(null)
const isRestoringSelection = ref(false)

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
// renderMath imported from ../utils/math

function normalizeDiff() {
  const { easy, medium, hard } = form.difficulty_distribution
  const total = easy + medium + hard
  if (total !== 100) {
    const scale = 100 / (total || 1)
    form.difficulty_distribution.easy = Math.round(easy * scale)
    form.difficulty_distribution.medium = Math.round(medium * scale)
    form.difficulty_distribution.hard = 100 - form.difficulty_distribution.easy - form.difficulty_distribution.medium
  }
}
watch(() => form.difficulty_distribution, normalizeDiff, { deep: true })

function onSelectionChange(rows) {
  if (isRestoringSelection.value) return
  // 合并新选中的到持久列表
  const newIds = new Set(rows.map(r => r.id))
  // 移除当前页中取消勾选的
  const currentPageIds = new Set(availableQuestions.value.map(r => r.id))
  pickedQuestions.value = pickedQuestions.value.filter(q => !currentPageIds.has(q.id))
  // 加入当前页勾选的
  for (const r of rows) {
    if (!pickedQuestions.value.find(q => q.id === r.id)) {
      pickedQuestions.value.push(r)
    }
  }
}

async function fetchAvailableQuestions() {
  qLoading.value = true
  try {
    const params = { page_size: 100 }
    if (qKeyword.value) params.keyword = qKeyword.value
    let data
    if (qFavOnly.value) {
      const res = await getFavorites(params)
      data = res.data
    } else {
      if (qType.value) params.question_type = qType.value
      if (qGrade.value) params.grade_level = qGrade.value
      if (qKnowledge.value) params.knowledge_point = qKnowledge.value
      const res = await getQuestions(params)
      data = res.data
    }
    availableQuestions.value = data.items
    // 恢复之前已勾选的题目状态（屏蔽 selection-change 事件避免误清）
    setTimeout(() => {
      isRestoringSelection.value = true
      if (tableRef.value) {
        availableQuestions.value.forEach(row => {
          if (pickedIds.value.has(row.id)) {
            tableRef.value.toggleRowSelection(row, true)
          }
        })
      }
      setTimeout(() => { isRestoringSelection.value = false }, 0)
    }, 0)
  } catch (e) {
    ElMessage.error('获取题目列表失败')
  } finally {
    qLoading.value = false
  }
}

watch([qKeyword, qType, qGrade, qKnowledge], () => {
  fetchAvailableQuestions()
})

async function handleCreate() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入试卷名称')
    return
  }

  submitting.value = true

  try {
    const payload = {
      ...form,
      question_count: totalQuestionCount.value,
    }
    if (composeMode.value === 'manual') {
      payload.question_ids = pickedQuestions.value.map(q => q.id)
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
