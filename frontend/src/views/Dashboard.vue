<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <el-icon class="stat-icon" :size="36"><component :is="stat.icon" /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>快速入口</template>
          <el-space wrap>
            <el-button type="primary" @click="$router.push('/questions/generate')">
              <el-icon><MagicStick /></el-icon> AI 出题
            </el-button>
            <el-button type="success" @click="$router.push('/exams/create')">
              <el-icon><DocumentAdd /></el-icon> 创建试卷
            </el-button>
            <el-button @click="$router.push('/questions')">
              <el-icon><Collection /></el-icon> 管理题库
            </el-button>
          </el-space>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>最新试卷</template>
          <el-empty v-if="!recentExams.length" description="暂无试卷" :image-size="60" />
          <el-table v-else :data="recentExams" size="small">
            <el-table-column prop="title" label="试卷名称" />
            <el-table-column prop="total_score" label="总分" width="80" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" @click="$router.push(`/exams/${row.id}`)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="myResults.length" shadow="hover" style="margin-top:20px">
      <template #header>我的答题记录</template>
      <el-table :data="myResults" size="small">
        <el-table-column prop="score" label="得分" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.score / row.total_score >= 0.8 ? '#67c23a' : row.score / row.total_score >= 0.6 ? '#e6a23c' : '#f56c6c', fontWeight: 'bold' }">
              {{ row.score }} / {{ row.total_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="correct_count" label="正确" width="120">
          <template #default="{ row }">{{ row.correct_count }} / {{ row.total_count }} 题</template>
        </el-table-column>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/exams/${row.exam_id}`)">查看试卷</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getExams, getStats, getMyResults } from '../api'

const stats = ref([
  { label: '题库总量', value: 0, icon: 'Collection' },
  { label: 'AI 生成题目', value: 0, icon: 'MagicStick' },
  { label: '试卷数量', value: 0, icon: 'Files' },
  { label: '今日新增', value: 0, icon: 'CirclePlus' },
])

const recentExams = ref([])
const myResults = ref([])

onMounted(async () => {
  try {
    const [sRes, eRes, rRes] = await Promise.allSettled([
      getStats(),
      getExams(),
      getMyResults(),
    ])

    if (sRes.status === 'fulfilled') {
      const d = sRes.value.data
      stats.value[0].value = d.total_questions
      stats.value[1].value = d.ai_generated
      stats.value[3].value = d.today_new
    }
    if (eRes.status === 'fulfilled') {
      stats.value[2].value = eRes.value.data.total
      recentExams.value = eRes.value.data.items.slice(0, 5)
    }
    if (rRes.status === 'fulfilled') {
      myResults.value = rRes.value.data.items.slice(0, 10)
    }
  } catch (e) {
    // Backend not reachable — display zeros
  }
})
</script>

<style scoped>
.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #e6e8eb;
}
</style>
