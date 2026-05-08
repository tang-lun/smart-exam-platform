<template>
  <el-card class="question-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="card-index">第 {{ index }} 题</span>
        <el-tag size="small">{{ typeLabel(question.type) }}</el-tag>
        <el-tag size="small" :type="diffType(question.difficulty)">{{ diffLabel(question.difficulty) }}</el-tag>
        <div class="kp-tags">
          <el-tag
            v-for="kp in (question.knowledge_points || [])"
            :key="kp"
            size="small"
            type="info"
          >{{ kp }}</el-tag>
        </div>
      </div>
    </template>
    <div class="stem">{{ question.stem }}</div>

    <div v-if="question.options?.length" class="options">
      <div v-for="(opt, i) in question.options" :key="i" class="option-item">{{ opt }}</div>
    </div>

    <template v-if="showAnswer">
      <el-divider />
      <div class="answer-section">
        <div class="answer-label">答案：</div>
        <div class="answer-content">{{ question.answer }}</div>
      </div>
      <div v-if="question.answer_analysis" class="analysis-section">
        <div class="analysis-label">解析：</div>
        <div class="analysis-content">{{ question.answer_analysis }}</div>
      </div>
    </template>
  </el-card>
</template>

<script setup>
const props = defineProps({
  question: { type: Object, required: true },
  index: { type: Number, default: 1 },
  showAnswer: { type: Boolean, default: false },
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
</script>

<style scoped>
.question-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-index {
  font-weight: 600;
  color: #409eff;
}

.kp-tags {
  margin-left: auto;
  display: flex;
  gap: 4px;
}

.stem {
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
}

.options {
  margin-top: 12px;
}

.option-item {
  padding: 8px 16px;
  margin: 4px 0;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 15px;
}

.answer-section {
  display: flex;
  gap: 8px;
}

.answer-label {
  font-weight: 600;
  color: #67c23a;
}

.answer-content {
  color: #67c23a;
  font-weight: 500;
}

.analysis-section {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.analysis-label {
  font-weight: 600;
  color: #409eff;
  white-space: nowrap;
}

.analysis-content {
  color: #606266;
  line-height: 1.6;
}
</style>
