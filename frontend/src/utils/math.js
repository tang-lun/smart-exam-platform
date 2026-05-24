import katex from 'katex'
import 'katex/dist/katex.min.css'

// LaTeX 命令 → Unicode 符号（在 KaTeX 渲染前做，兜底 $...$ 外的漏网 LaTeX）
const LATEX_TO_UNICODE = [
  [/\\triangle/g, '△'],
  [/\\angle/g, '∠'],
  [/\\pi/g, 'π'],
  [/\\alpha/g, 'α'],
  [/\\beta/g, 'β'],
  [/\\gamma/g, 'γ'],
  [/\\delta/g, 'δ'],
  [/\\theta/g, 'θ'],
  [/\\lambda/g, 'λ'],
  [/\\mu/g, 'μ'],
  [/\\sigma/g, 'σ'],
  [/\\omega/g, 'ω'],
  [/\\Omega/g, 'Ω'],
  [/\\Delta/g, 'Δ'],
  [/\\infty/g, '∞'],
  [/\\pm/g, '±'],
  [/\\circ/g, '°'],
  [/\\leq/g, '≤'],
  [/\\geq/g, '≥'],
  [/\\neq/g, '≠'],
  [/\\approx/g, '≈'],
  [/\\equiv/g, '≡'],
  [/\\times/g, '×'],
  [/\\div/g, '÷'],
  [/\\cdot/g, '·'],
  [/\\cdots/g, '⋯'],
  [/\\ldots/g, '…'],
  [/\\Rightarrow/g, '⇒'],
  [/\\Leftrightarrow/g, '⇔'],
  [/\\rightarrow/g, '→'],
  [/\\leftarrow/g, '←'],
  [/\\parallel/g, '∥'],
  [/\\perp/g, '⊥'],
  [/\\cup/g, '∪'],
  [/\\cap/g, '∩'],
  [/\\subset/g, '⊂'],
  [/\\supset/g, '⊃'],
  [/\\notin/g, '∉'],
  [/\\in/g, '∈'],
  [/\\forall/g, '∀'],
  [/\\exists/g, '∃'],
  [/\\sum/g, 'Σ'],
  [/\\prod/g, 'Π'],
  [/\\emptyset/g, '∅'],
  [/\\square/g, '□'],
]

// $...$ 外的格式命令，转为普通空格/连接符
const LATEX_FORMAT_CLEANUP = [
  [/\\(?:quad|qquad)/g, '  '],
  [/\\[;,]/g, ' '],
  [/\\text\{([^}]*)\}/g, '$1'],
  [/\\textbf\{([^}]*)\}/g, '$1'],
  [/\\dfrac/g, '\\frac'],
  [/\\[nr](?![a-zA-Z])/g, ' '],  // 残余的 \n \r（不含 \neq \nsubseteq 等有效命令）
]

/**
 * 渲染混合了 LaTeX 公式的文本，返回 HTML 字符串
 */
export function renderMath(text) {
  if (!text) return ''

  let r = text
  // 清理旧数据可能残留的 JSON 转义污染（\t \n \r 被错误解码为控制字符）
  r = r.replace(/\t/g, ' ')
  r = r.replace(/\n/g, ' ')
  r = r.replace(/\r/g, ' ')
  // 清理 AI 可能生成的不规范填空标记
  r = r.replace(/\\text\{_{3,}\}/g, '______')

  // ===== 第一步：LaTeX 命令 → Unicode（在 KaTeX 之前做，兜底 $...$ 外的公式）=====
  for (const [pattern, replacement] of LATEX_TO_UNICODE) {
    r = r.replace(pattern, replacement)
  }

  // ===== 第二步：KaTeX 渲染 $...$ / $$...$$ / \[...\] / \(...\) 内的公式 =====

  // $$...$$ block math
  r = r.replace(/\$\$([\s\S]+?)\$\$/g, (_, f) => {
    try { return katex.renderToString(f, { throwOnError: false, displayMode: true }) } catch { return '' }
  })

  // \[...\] display LaTeX
  r = r.replace(/\\\[([\s\S]+?)\\\]/g, (_, f) => {
    try { return katex.renderToString(f, { throwOnError: false, displayMode: true }) } catch { return '' }
  })

  // \(...\) inline LaTeX
  r = r.replace(/\\\(([\s\S]+?)\\\)/g, (_, f) => {
    try { return katex.renderToString(f, { throwOnError: false, displayMode: false }) } catch { return '' }
  })

  // $...$ inline math（必须在 $$ 之后处理，避免误匹配）
  r = r.replace(/(?<!\$)\$([^$]+)\$(?!\$)/g, (_, f) => {
    try { return katex.renderToString(f, { throwOnError: false, displayMode: false }) } catch { return '' }
  })

  // \begin{xxx}...\end{xxx} 块
  r = r.replace(/\\begin\{(\w+)\}([\s\S]*?)\\end\{\1\}/g, m => {
    try { return katex.renderToString(m, { throwOnError: false, displayMode: true }) } catch { return '' }
  })

  // 兜底：AI 偶尔把 \frac{}{} \sqrt{} 写在 $...$ 外面，KaTeX 跳过后仍是原始文本
  r = r.replace(/\\(frac|sqrt|sum|prod|int|lim)\b(\{[^{}]*(?:\{[^}]*\}[^{}]*)*\})*/g, m => {
    try { return katex.renderToString(m, { throwOnError: false, displayMode: false }) } catch { return m }
  })

  // ===== 第三步：清理残余格式命令 =====
  for (const [pattern, replacement] of LATEX_FORMAT_CLEANUP) {
    r = r.replace(pattern, replacement)
  }

  return r
}
