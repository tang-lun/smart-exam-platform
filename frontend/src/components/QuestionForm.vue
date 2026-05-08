<template>
  <el-form :model="form" label-width="80px">
    <el-form-item label="题型">
      <el-select v-model="form.type" style="width: 100%">
        <el-option label="选择题" value="choice" />
        <el-option label="填空题" value="fill_blank" />
        <el-option label="计算题" value="calculation" />
        <el-option label="证明题" value="proof" />
      </el-select>
    </el-form-item>
    <el-form-item label="难度">
      <el-select v-model="form.difficulty" style="width: 100%">
        <el-option label="基础" value="easy" />
        <el-option label="中等" value="medium" />
        <el-option label="较难" value="hard" />
      </el-select>
    </el-form-item>
    <el-form-item label="知识点">
      <el-select
        v-model="form.knowledge_points"
        multiple
        filterable
        allow-create
        default-first-option
        style="width: 100%"
        placeholder="输入知识点"
      />
    </el-form-item>
    <el-form-item label="题干">
      <el-input v-model="form.stem" type="textarea" :rows="3" />
    </el-form-item>
    <el-form-item v-if="form.type === 'choice'" label="选项">
      <div v-for="(_, i) in form.options" :key="i" style="margin-bottom: 4px">
        <el-input v-model="form.options[i]" placeholder="选项格式：A. xxx" />
      </div>
    </el-form-item>
    <el-form-item label="答案">
      <el-input v-model="form.answer" />
    </el-form-item>
    <el-form-item label="解析">
      <el-input v-model="form.answer_analysis" type="textarea" :rows="2" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { updateQuestion } from '../api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  question: { type: Object, required: true },
})

const emit = defineEmits(['saved'])

const form = reactive({
  type: 'choice',
  difficulty: 'medium',
  knowledge_points: [],
  stem: '',
  options: ['A. ', 'B. ', 'C. ', 'D. '],
  answer: '',
  answer_analysis: '',
})

const saving = reactive({ value: false })

watch(() => props.question, (q) => {
  form.type = q.type || 'choice'
  form.difficulty = q.difficulty || 'medium'
  form.knowledge_points = [...(q.knowledge_points || [])]
  form.stem = q.stem || ''
  form.options = q.options?.length ? [...q.options] : ['A. ', 'B. ', 'C. ', 'D. ']
  form.answer = q.answer || ''
  form.answer_analysis = q.answer_analysis || ''
}, { immediate: true })

async function handleSave() {
  saving.value = true
  try {
    await updateQuestion(props.question.id, { ...form })
    ElMessage.success('保存成功')
    emit('saved')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>
