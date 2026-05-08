<template>
  <div class="question-bank">
    <el-card shadow="never">
      <template #header>
        <div class="bank-header">
          <span>题库管理</span>
          <el-button type="primary" @click="$router.push('/questions/generate')">
            <el-icon><MagicStick /></el-icon> AI 出题
          </el-button>
        </div>
      </template>

      <div class="toolbar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索题干关键词..."
          clearable
          style="width: 240px"
          @change="fetchQuestions"
        />
        <el-select
          v-model="filters.question_type"
          placeholder="题型筛选"
          clearable
          style="width: 140px"
          @change="fetchQuestions"
        >
          <el-option label="选择题" value="choice" />
          <el-option label="填空题" value="fill_blank" />
          <el-option label="计算题" value="calculation" />
          <el-option label="证明题" value="proof" />
        </el-select>
        <el-select
          v-model="filters.difficulty"
          placeholder="难度筛选"
          clearable
          style="width: 140px"
          @change="fetchQuestions"
        >
          <el-option label="基础" value="easy" />
          <el-option label="中等" value="medium" />
          <el-option label="较难" value="hard" />
        </el-select>
      </div>

      <el-table :data="questions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="题型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="stem" label="题干" min-width="300" show-overflow-tooltip />
        <el-table-column label="知识点" width="180">
          <template #default="{ row }">
            <el-tag
              v-for="kp in row.knowledge_points"
              :key="kp"
              size="small"
              type="info"
              style="margin: 2px"
            >{{ kp }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="难度" width="80">
          <template #default="{ row }">
            <el-tag :type="diffType(row.difficulty)" size="small">{{ diffLabel(row.difficulty) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="90">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.source === 'ai_generated' ? 'AI' : '手动' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-popconfirm title="确定删除该题目？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchQuestions"
          @current-change="fetchQuestions"
        />
      </div>
    </el-card>

    <!-- Detail drawer -->
    <el-drawer v-model="drawerVisible" title="题目详情" size="500px">
      <template v-if="currentQuestion">
        <QuestionForm :question="currentQuestion" @saved="onSaved" />
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getQuestions, deleteQuestion } from '../api'
import { ElMessage } from 'element-plus'
import QuestionForm from '../components/QuestionForm.vue'

const questions = ref([])
const loading = ref(false)
const drawerVisible = ref(false)
const currentQuestion = ref(null)

const filters = ref({
  keyword: '',
  question_type: '',
  difficulty: '',
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
})

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

async function fetchQuestions() {
  loading.value = true
  try {
    const { data } = await getQuestions({
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      keyword: filters.value.keyword,
      question_type: filters.value.question_type,
      difficulty: filters.value.difficulty,
    })
    questions.value = data.items
    pagination.value.total = data.total
  } catch (e) {
    ElMessage.error('获取题库失败')
  } finally {
    loading.value = false
  }
}

function viewDetail(q) {
  currentQuestion.value = { ...q }
  drawerVisible.value = true
}

async function handleDelete(id) {
  try {
    await deleteQuestion(id)
    ElMessage.success('删除成功')
    fetchQuestions()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

function onSaved() {
  drawerVisible.value = false
  fetchQuestions()
}

onMounted(fetchQuestions)
</script>

<style scoped>
.bank-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
