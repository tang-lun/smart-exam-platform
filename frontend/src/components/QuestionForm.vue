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
      <div v-if="form.stem" class="field-preview" v-html="renderMath(form.stem)"></div>
      <el-input v-model="form.stem" type="textarea" :rows="3" />
    </el-form-item>
    <el-form-item v-if="form.type === 'choice'" label="选项">
      <el-input v-for="(_, i) in form.options" :key="i" v-model="form.options[i]" style="margin-bottom:4px">
        <template #prepend>{{ String.fromCharCode(65 + i) }}</template>
      </el-input>
    </el-form-item>
    <el-form-item label="答案">
      <div v-if="form.answer" class="field-preview" v-html="renderMath(form.answer)"></div>
      <el-input v-model="form.answer" />
    </el-form-item>
    <el-form-item label="解析">
      <div v-if="form.answer_analysis" class="field-preview" v-html="renderMath(form.answer_analysis)"></div>
      <el-input v-model="form.answer_analysis" type="textarea" :rows="2" />
    </el-form-item>
    <el-alert v-if="auditFeedback" :title="auditFeedback" :type="auditPassed ? 'success' : 'error'" :closable="false" style="margin-bottom:12px" />
    <el-form-item>
      <el-button :loading="auditing" @click="handleAudit">
        <el-icon><Check /></el-icon> AI 审核
      </el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { updateQuestion, validateQuestion } from '../api'
import { ElMessage } from 'element-plus'
import { renderMath } from '../utils/math'

const props = defineProps({
  question: { type: Object, required: true },
})

const emit = defineEmits(['saved'])

const form = reactive({
  type: 'choice',
  difficulty: 'medium',
  knowledge_points: [],
  stem: '',
  options: ['', '', '', ''],
  answer: '',
  answer_analysis: '',
})

const saving = ref(false)
const auditing = ref(false)
const auditFeedback = ref('')
const auditPassed = ref(false)

watch(() => props.question, (q) => {
  form.type = q.type || 'choice'
  form.difficulty = q.difficulty || 'medium'
  form.knowledge_points = [...(q.knowledge_points || [])]
  form.stem = q.stem || ''
  form.options = q.options?.length ? q.options.map(o => o.replace(/^[A-D][.、]\s*/, '')) : ['', '', '', '']
  form.answer = q.answer || ''
  form.answer_analysis = q.answer_analysis || ''
  auditFeedback.value = ''
  auditPassed.value = false
}, { immediate: true })

async function handleAudit() {
  auditing.value = true
  auditFeedback.value = ''
  try {
    const payload = { ...form }
    if (payload.type === 'choice' && payload.options?.length) {
      payload.options = payload.options.map((o, i) => String.fromCharCode(65 + i) + '. ' + o)
    }
    const { data } = await validateQuestion(payload)
    auditPassed.value = data.valid
    auditFeedback.value = data.feedback
    ElMessage[data.valid ? 'success' : 'warning'](data.valid ? '审核通过' : '审核发现问题')
  } catch (e) {
    auditFeedback.value = parseError(e)
    auditPassed.value = false
  } finally {
    auditing.value = false
  }
}

async function handleSave() {
  if (!auditPassed.value && auditFeedback.value) {
    // AI 审核不通过时给出提示但不阻止保存（AI 可能误判或不可用）
    ElMessage.warning('AI 审核发现问题，请确认后再保存')
  }
  saving.value = true
  try {
    const payload = { ...form }
    if (payload.type === 'choice' && payload.options?.length) {
      payload.options = payload.options.map((o, i) => String.fromCharCode(65 + i) + '. ' + o)
    }
    await updateQuestion(props.question.id, payload)
    ElMessage.success('保存成功')
    emit('saved')
  } catch (e) {
    ElMessage.error(parseError(e))
  } finally {
    saving.value = false
  }
}

function parseError(e) {
  const d = e.response?.data?.detail
  if (!d) return '保存失败'
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map(i => i.msg).join('；')
  return JSON.stringify(d)
}
</script>

<style scoped>
.field-preview {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  max-height: 120px;
  overflow-y: auto;
}
.field-preview :deep(.katex) {
  font-size: 1.05em;
}
</style>
