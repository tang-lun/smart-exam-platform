<template>
  <div class="exam-papers">
    <el-card shadow="never">
      <template #header>
        <div class="paper-header">
          <span>试卷列表</span>
          <el-button type="primary" @click="$router.push('/exams/create')">
            <el-icon><DocumentAdd /></el-icon> 创建试卷
          </el-button>
        </div>
      </template>

      <el-table :data="exams" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="试卷名称" min-width="250" />
        <el-table-column label="题量" width="80">
          <template #default="{ row }">{{ row.question_ids?.length || 0 }} 题</template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" width="80" />
        <el-table-column prop="duration_minutes" label="时长(分)" width="100" />
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/exams/${row.id}`)">查看</el-button>
            <el-popconfirm title="确定删除该试卷？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && !exams.length" description="暂无试卷" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getExams, deleteExam } from '../api'
import { ElMessage } from 'element-plus'

const exams = ref([])
const loading = ref(false)

async function fetchExams() {
  loading.value = true
  try {
    const { data } = await getExams()
    exams.value = data.items
  } catch (e) {
    ElMessage.error('获取试卷列表失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteExam(id)
    ElMessage.success('删除成功')
    fetchExams()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchExams)
</script>

<style scoped>
.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
