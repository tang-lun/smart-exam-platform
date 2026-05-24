<template>
  <div class="math-pad">
    <div class="symbol-section">
      <span class="section-label">上下标</span>
      <button type="button" v-for="s in superscripts" :key="s" @click="insert(s)">{{ s }}</button>
    </div>
    <div class="symbol-section">
      <span class="section-label">运算符</span>
      <button type="button" v-for="s in operators" :key="s" @click="insert(s)">{{ s }}</button>
    </div>
    <div class="symbol-section">
      <span class="section-label">希腊/几何</span>
      <button type="button" v-for="s in greek" :key="s" @click="insert(s)">{{ s }}</button>
    </div>
    <div class="symbol-section">
      <span class="section-label">LaTeX</span>
      <button type="button" @click="insert('$x^2$')">x²</button>
      <button type="button" @click="insert('$\\frac{a}{b}$')">a/b</button>
      <button type="button" @click="insert('$\\sqrt{x}$')">√</button>
      <button type="button" @click="insert('$\\pm$')">±</button>
      <button type="button" @click="insert('$\\triangle$')">△</button>
      <button type="button" @click="insert('$\\angle$')">∠</button>
      <button type="button" @click="insert('$\\perp$')">⊥</button>
      <button type="button" @click="insert('$\\parallel$')">∥</button>
      <button type="button" @click="insert('$\\approx$')">≈</button>
      <button type="button" @click="insert('$\\neq$')">≠</button>
      <button type="button" @click="insert('$\\leq$')">≤</button>
      <button type="button" @click="insert('$\\geq$')">≥</button>
      <button type="button" @click="insert('$\\infty$')">∞</button>
      <button type="button" @click="insert('$\\cdot$')">·</button>
      <button type="button" @click="insert('$\\times$')">×</button>
      <button type="button" @click="insert('$\\div$')">÷</button>
      <button type="button" @click="insert('$\\therefore$')">∴</button>
      <button type="button" @click="insert('$\\because$')">∵</button>
      <button type="button" @click="insert('$\\circ$')">°</button>
      <button type="button" @click="insert('$\\sum$')">∑</button>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['insert'])

const superscripts = ['²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '⁰',
                       '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉', '₀']
const operators = ['+', '−', '×', '÷', '±', '=', '≠', '≈', '<', '>', '≤', '≥']
const greek = ['α', 'β', 'γ', 'θ', 'λ', 'μ', 'π', 'σ', 'φ', 'ω', '△', '∠', '⊥', '∥', '°', '√', '∞']

function insert(symbol) {
  emit('insert', symbol)
}
</script>

<style scoped>
.math-pad {
  background: #f8f9fb;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 0;
}

.symbol-section {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.symbol-section:last-child {
  margin-bottom: 0;
}

.section-label {
  font-size: 12px;
  color: #909399;
  margin-right: 8px;
  white-space: nowrap;
}

.symbol-section button {
  width: 32px;
  height: 28px;
  border: 1px solid #dcdfe6;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.symbol-section button:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}
</style>
