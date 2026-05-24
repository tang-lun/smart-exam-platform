<template>
  <div class="favorites">
    <el-card shadow="never">
      <template #header>我的收藏</template>
      <el-table :data="questions" v-loading="loading" stripe>
        <el-table-column label="#" width="60" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column label="题型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="题干" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="stem-cell" v-html="renderMath(row.stem || '')"></span>
          </template>
        </el-table-column>
        <el-table-column label="学段" width="70">
          <template #default="{ row }">{{ gradeLabel(row.grade_level) }}</template>
        </el-table-column>
        <el-table-column label="知识点" width="180">
          <template #default="{ row }">
            <el-tag v-for="kp in row.knowledge_points" :key="kp" size="small" type="info" style="margin:2px">{{ kp }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="难度" width="80">
          <template #default="{ row }">
            <el-tag :type="diffType(row.difficulty)" size="small">{{ diffLabel(row.difficulty) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="取消" width="70" align="center">
          <template #default="{ row }">
            <el-button type="warning" :icon="'StarFilled'" size="small" text @click="handleUnfavorite(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !questions.length" description="还没有收藏任何题目" />
      <div class="pagination" v-if="total">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchFavorites"
          @current-change="fetchFavorites"
        />
      </div>
    </el-card>

    <el-drawer v-model="drawerVisible" title="题目详情" size="550px" @closed="showEditForm = false">
      <template v-if="currentQuestion">
        <QuestionCard :question="currentQuestion" :index="currentIndex" :show-answer="true" />
        <div style="margin-top:16px; text-align:center">
          <el-button v-if="!showEditForm" text type="primary" @click="showEditForm = true">
            <el-icon><Edit /></el-icon> 编辑题目
          </el-button>
        </div>
        <template v-if="showEditForm">
          <el-divider />
          <h4 style="margin-bottom:12px">编辑题目</h4>
          <QuestionForm :question="currentQuestion" @saved="onSaved" />
        </template>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFavorites, toggleFavorite } from '../api'
import { ElMessage } from 'element-plus'
import QuestionForm from '../components/QuestionForm.vue'
import QuestionCard from '../components/QuestionCard.vue'
import { renderMath } from '../utils/math'

const questions = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const drawerVisible = ref(false)
const currentQuestion = ref(null)
const currentIndex = ref(0)
const showEditForm = ref(false)

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
function gradeLabel(g) {
  const map = { grade_7: '初一', grade_8: '初二', grade_9: '初三' }
  return map[g] || g
}

async function fetchFavorites() {
  loading.value = true
  try {
    const { data } = await getFavorites({ page: page.value, page_size: pageSize.value })
    questions.value = data.items
    total.value = data.total
  } catch { ElMessage.error('获取收藏列表失败') }
  finally { loading.value = false }
}

async function handleUnfavorite(row) {
  try {
    await toggleFavorite(row.id)
    fetchFavorites()
  } catch { ElMessage.error('操作失败') }
}

function viewDetail(q) {
  currentQuestion.value = { ...q }
  const idx = questions.value.findIndex(item => item.id === q.id)
  currentIndex.value = idx >= 0 ? (page.value - 1) * pageSize.value + idx + 1 : 1
  showEditForm.value = false
  drawerVisible.value = true
}

function onSaved() {
  drawerVisible.value = false
  fetchFavorites()
}

onMounted(fetchFavorites)
</script>

<style scoped>
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
.stem-cell {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}
.stem-cell :deep(.katex) { font-size: 0.95em; }
</style>
