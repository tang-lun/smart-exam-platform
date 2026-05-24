<template>
  <div class="question-bank">
    <el-card shadow="never">
      <template #header>
        <div class="bank-header">
          <span>题库管理</span>
          <div>
            <el-button
              v-if="selectedIds.length"
              type="danger"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon> 批量删除 ({{ selectedIds.length }})
            </el-button>
            <el-button @click="showManualDialog">
              <el-icon><Edit /></el-icon> 手动添加
            </el-button>
            <el-button @click="showImportDialog">
              <el-icon><Upload /></el-icon> 导入题目
            </el-button>
            <el-button type="primary" @click="$router.push('/questions/generate')">
              <el-icon><MagicStick /></el-icon> AI 出题
            </el-button>
          </div>
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
        <el-select
          v-model="filters.grade_level"
          placeholder="学段"
          clearable
          style="width: 120px"
          @change="fetchQuestions"
        >
          <el-option label="初一" value="grade_7" />
          <el-option label="初二" value="grade_8" />
          <el-option label="初三" value="grade_9" />
        </el-select>
        <el-select
          v-model="filters.knowledge_point"
          placeholder="知识点筛选"
          clearable
          filterable
          style="width: 160px"
          @change="fetchQuestions"
        >
          <el-option v-for="kp in knowledgeOptions" :key="kp" :label="kp" :value="kp" />
        </el-select>
      </div>

      <el-table :data="questions" v-loading="loading" stripe @selection-change="onSelect">
        <el-table-column type="selection" width="50" />
        <el-table-column label="#" width="60" align="center">
          <template #default="{ $index }">{{ (pagination.page - 1) * pagination.pageSize + $index + 1 }}</template>
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
            <el-tag size="small" effect="plain">{{ sourceLabel(row.source) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="收藏" width="70" align="center">
          <template #default="{ row }">
            <el-button
              :icon="row.is_favorited ? 'StarFilled' : 'Star'"
              :type="row.is_favorited ? 'warning' : ''"
              size="small"
              text
              @click="handleFavorite(row)"
            />
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

    <!-- Import dialog -->
    <el-dialog v-model="importVisible" title="批量导入题目" width="720px" destroy-on-close @closed="importFile=null; importResult=null">
      <el-steps :active="importStep" simple style="margin-bottom:24px">
        <el-step title="下载模板" />
        <el-step title="上传文件" />
        <el-step title="查看结果" />
      </el-steps>

      <template v-if="importStep === 1">
        <p style="color:#606266; margin-bottom:16px">请先下载导入模板，按模板格式填写题目后上传。支持 .csv / .xlsx 格式。</p>
        <el-button type="primary" :loading="downloadingTemplate" @click="handleDownloadTemplate">
          <el-icon><Download /></el-icon> 下载 CSV 模板
        </el-button>
        <div style="margin-top: 16px; padding: 12px; background: #f5f7fa; border-radius: 6px; font-size: 13px; color: #909399">
          <strong>模板说明：</strong><br />
          题型：选择题 / 填空题 / 计算题 / 证明题（或英文 choice/fill_blank/calculation/proof）<br />
          难度：基础 / 中等 / 较难（或英文 easy/medium/hard）<br />
          年级：初一 / 初二 / 初三（或英文 grade_7/grade_8/grade_9）<br />
          知识点：多个用逗号分隔；选择题需填写选项A-D列；中英文均可识别
        </div>
      </template>

      <template v-if="importStep === 2">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".csv,.xlsx,.xls"
          :on-change="onFileChange"
          :on-remove="() => { importFile = null }"
          drag
        >
          <el-icon style="font-size:40px"><UploadFilled /></el-icon>
          <div style="margin-top:8px">将 CSV 或 Excel 文件拖到此处，或点击选择</div>
          <template #tip>
            <div style="margin-top: 8px; color: #909399">仅支持 .csv / .xlsx / .xls 格式</div>
          </template>
        </el-upload>
      </template>

      <template v-if="importStep === 3 && importResult">
        <div style="text-align:center; margin-bottom:16px">
          <span style="font-size:18px; font-weight:600; color:#67c23a">成功导入 {{ importResult.success }} 题</span>
          <span v-if="importResult.errors?.length" style="font-size:14px; color:#f56c6c; margin-left:16px">
            失败 {{ importResult.errors.length }} 行
          </span>
        </div>
        <el-table v-if="importResult.errors?.length" :data="importResult.errors" max-height="240" size="small">
          <el-table-column prop="row" label="行号" width="80" />
          <el-table-column prop="error" label="错误原因" show-overflow-tooltip />
        </el-table>
      </template>

      <template #footer>
        <template v-if="importStep < 3">
          <el-button @click="importVisible = false">取消</el-button>
          <el-button v-if="importStep === 1" type="primary" @click="importStep = 2">已下载，下一步</el-button>
          <el-button
            v-if="importStep === 2"
            type="primary"
            :loading="importing"
            :disabled="!importFile"
            @click="handleImport"
          >开始导入</el-button>
        </template>
        <el-button v-if="importStep === 3" type="primary" @click="onImportDone">完成</el-button>
      </template>
    </el-dialog>

    <!-- Manual add dialog -->
    <el-dialog v-model="manualVisible" title="手动添加题目" width="640px" destroy-on-close>
      <el-form :model="manualForm" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="题型"><el-select v-model="manualForm.type" style="width:100%">
              <el-option label="选择题" value="choice" />
              <el-option label="填空题" value="fill_blank" />
              <el-option label="计算题" value="calculation" />
              <el-option label="证明题" value="proof" />
            </el-select></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="难度"><el-select v-model="manualForm.difficulty" style="width:100%">
              <el-option label="基础" value="easy" />
              <el-option label="中等" value="medium" />
              <el-option label="较难" value="hard" />
            </el-select></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学段"><el-select v-model="manualForm.grade_level" style="width:100%">
              <el-option label="初一" value="grade_7" />
              <el-option label="初二" value="grade_8" />
              <el-option label="初三" value="grade_9" />
            </el-select></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="知识点">
          <el-select v-model="manualForm.knowledge_points" multiple filterable allow-create default-first-option placeholder="输入知识点" style="width:100%">
            <el-option v-for="kp in manualKnowledgeOptions" :key="kp" :label="kp" :value="kp" />
          </el-select>
        </el-form-item>
        <el-form-item label="题干">
          <el-input v-model="manualForm.stem" type="textarea" :rows="3" placeholder="输入题目题干" ref="stemRef" @focus="onFieldFocus" />
          <MathSymbolPad style="margin-top: 8px" @insert="s => insertAtCursor('stem', s)" />
        </el-form-item>
        <el-form-item v-if="manualForm.type === 'choice'" label="选项">
          <el-input v-for="(_, i) in manualForm.options" :key="i" v-model="manualForm.options[i]" style="margin-bottom:4px">
            <template #prepend>{{ String.fromCharCode(65 + i) }}</template>
          </el-input>
        </el-form-item>
        <el-form-item label="答案">
          <el-input v-model="manualForm.answer" placeholder="选择题填字母如 B，其他题型填写最终答案" @focus="onFieldFocus" />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="manualForm.answer_analysis" type="textarea" :rows="2" placeholder="可选填写解题过程或知识点说明" ref="analysisRef" @focus="onFieldFocus" />
          <MathSymbolPad style="margin-top: 8px" @insert="s => insertAtCursor('answer_analysis', s)" />
        </el-form-item>
        <el-alert v-if="auditResult" :title="auditResult.feedback" :type="auditResult.valid ? 'success' : 'error'" :closable="false" style="margin-bottom:12px" />
      </el-form>
      <template #footer>
        <el-button @click="manualVisible = false">取消</el-button>
        <el-button type="warning" :loading="auditing" @click="handleAudit">
          <el-icon><Check /></el-icon> AI 审核
        </el-button>
        <el-button type="primary" :loading="manualSaving" @click="handleManualSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getQuestions, deleteQuestion, createManualQuestion, validateQuestion, toggleFavorite, importQuestions, downloadTemplate } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import QuestionForm from '../components/QuestionForm.vue'
import QuestionCard from '../components/QuestionCard.vue'
import MathSymbolPad from '../components/MathSymbolPad.vue'
import { GRADE_KNOWLEDGE } from '../constants'
import { renderMath } from '../utils/math'

const questions = ref([])
const loading = ref(false)
const drawerVisible = ref(false)
const currentQuestion = ref(null)
const currentIndex = ref(0)
const showEditForm = ref(false)
const selectedIds = ref([])

function onSelect(rows) {
  selectedIds.value = rows.map(r => r.id)
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedIds.value.length} 道题目？此操作不可恢复。`,
      '批量删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch { return }

  loading.value = true
  let done = 0
  for (const id of selectedIds.value) {
    try { await deleteQuestion(id); done++ } catch {}
  }
  ElMessage.success(`已删除 ${done} 道题目`)
  selectedIds.value = []
  fetchQuestions()
}

const filters = ref({
  keyword: '',
  question_type: '',
  difficulty: '',
  grade_level: '',
  knowledge_point: '',
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

function gradeLabel(g) {
  const map = { grade_7: '初一', grade_8: '初二', grade_9: '初三' }
  return map[g] || g
}

function sourceLabel(s) {
  const map = { ai_generated: 'AI', manual: '手动', imported: '导入' }
  return map[s] || s
}

// renderMath imported from ../utils/math

async function fetchQuestions() {
  loading.value = true
  try {
    const { data } = await getQuestions({
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      keyword: filters.value.keyword,
      question_type: filters.value.question_type,
      difficulty: filters.value.difficulty,
      grade_level: filters.value.grade_level,
      knowledge_point: filters.value.knowledge_point,
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
  const idx = questions.value.findIndex(item => item.id === q.id)
  currentIndex.value = idx >= 0 ? (pagination.value.page - 1) * pagination.value.pageSize + idx + 1 : 1
  drawerVisible.value = true
}

async function handleFavorite(row) {
  try {
    const { data } = await toggleFavorite(row.id)
    row.is_favorited = data.is_favorited
  } catch {
    ElMessage.error('操作失败')
  }
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

// Manual question creation
const manualVisible = ref(false)
const auditing = ref(false)
const manualSaving = ref(false)
const auditResult = ref(null)
const stemRef = ref(null)
const lastFocused = ref(null)

function onFieldFocus(e) {
  lastFocused.value = e.target
}

function insertAtCursor(field, symbol) {
  const textarea = lastFocused.value
  if (!textarea || (textarea.tagName !== 'TEXTAREA' && textarea.tagName !== 'INPUT')) {
    manualForm.value[field] += symbol
    return
  }
  const start = textarea.selectionStart ?? 0
  const end = textarea.selectionEnd ?? 0
  const val = manualForm.value[field]
  manualForm.value[field] = val.slice(0, start) + symbol + val.slice(end)
  setTimeout(() => {
    textarea.focus()
    textarea.selectionStart = textarea.selectionEnd = start + symbol.length
  }, 50)
}

const manualForm = ref({
  type: 'choice',
  difficulty: 'medium',
  grade_level: 'grade_7',
  knowledge_points: [],
  stem: '',
  options: ['', '', '', ''],
  answer: '',
  answer_analysis: '',
})

watch(() => manualForm.value.type, (t) => {
  if (t === 'choice' && !manualForm.value.options?.length) {
    manualForm.value.options = ['', '', '', '']
  }
})

// 筛选用的知识点列表：如果选了年级则显示对应年级的
const knowledgeOptions = computed(() => {
  if (filters.value.grade_level) return GRADE_KNOWLEDGE[filters.value.grade_level] || []
  return Object.values(GRADE_KNOWLEDGE).flat()
})

// 手动添加用的知识点列表：根据弹窗中的年级动态切换
const manualKnowledgeOptions = computed(() => {
  return GRADE_KNOWLEDGE[manualForm.value.grade_level] || []
})

watch(() => manualForm.value.grade_level, () => {
  manualForm.value.knowledge_points = []
})

function showManualDialog() {
  auditResult.value = null
  manualForm.value = {
    type: 'choice',
    difficulty: 'medium',
    grade_level: 'grade_7',
    knowledge_points: [],
    stem: '',
    options: ['', '', '', ''],
    answer: '',
    answer_analysis: '',
  }
  manualVisible.value = true
}

async function handleAudit() {
  const err = validateManual()
  if (err) { ElMessage.warning(err); return }

  auditing.value = true
  auditResult.value = null

  try {
    const payload = { ...manualForm.value }
    if (payload.type === 'choice' && payload.options?.length) {
      payload.options = payload.options.map((o, i) => String.fromCharCode(65 + i) + '. ' + o)
    }
    const { data } = await validateQuestion(payload)
    auditResult.value = { valid: data.valid, feedback: data.feedback }
  } catch (e) {
    auditResult.value = { valid: false, feedback: parseErr(e) }
  } finally {
    auditing.value = false
  }
}

function validateManual() {
  if (!manualForm.value.knowledge_points?.length) return '请至少选择一个知识点'
  if (!manualForm.value.stem.trim()) return '请填写题干'
  if (manualForm.value.type === 'choice' && (!manualForm.value.options?.length || manualForm.value.options.every(o => !o.trim()))) return '选择题请填写选项'
  if (!manualForm.value.answer.trim()) return '请填写答案'
  return ''
}

async function handleManualSave() {
  const err = validateManual()
  if (err) { ElMessage.warning(err); return }

  manualSaving.value = true
  try {
    const payload = { ...manualForm.value }
    if (payload.type === 'choice' && payload.options?.length) {
      payload.options = payload.options.map((o, i) => String.fromCharCode(65 + i) + '. ' + o)
    }
    await createManualQuestion(payload)
    ElMessage.success('题目添加成功')
    manualVisible.value = false
    fetchQuestions()
  } catch (e) {
    ElMessage.error(parseErr(e))
  } finally {
    manualSaving.value = false
  }
}

function parseErr(e) {
  const d = e.response?.data?.detail
  if (!d) return '操作失败'
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map(i => i.msg).join('；')
  return JSON.stringify(d)
}

// Batch import
const importVisible = ref(false)
const importStep = ref(1)
const importFile = ref(null)
const importing = ref(false)
const importingTemplate = ref(false)
const downloadTemplateLoading = ref(false)
const importResult = ref(null)

function showImportDialog() {
  importStep.value = 1
  importFile.value = null
  importResult.value = null
  importVisible.value = true
}

function onFileChange(file) {
  importFile.value = file.raw
}

async function handleDownloadTemplate() {
  downloadTemplateLoading.value = true
  try {
    const { data } = await downloadTemplate()
    const blob = new Blob([data], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.download = '题目导入模板.csv'
    a.href = url
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch {
    ElMessage.error('下载失败')
  } finally {
    downloadTemplateLoading.value = false
  }
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  try {
    const { data } = await importQuestions(importFile.value)
    importResult.value = data
    importStep.value = 3
    if (data.success > 0) {
      ElMessage.success(`成功导入 ${data.success} 题`)
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

function onImportDone() {
  importVisible.value = false
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

.stem-cell {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}
.stem-cell :deep(.katex) {
  font-size: 0.95em;
}
</style>
