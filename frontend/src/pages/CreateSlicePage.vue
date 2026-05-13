<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { saveGuestStardust } from '../data/guestStardust'
import type { Card } from '../types/card'
import KanshanGuide from '../components/KanshanGuide.vue'

type AnalysisState = 'idle' | 'loading' | 'ready' | 'empty'
type GeneratedNode = {
  id: string
  title: string
  description: string
  emotion: string
  reading_links?: string[]
}

const router = useRouter()

const now = new Date()
const endDefault = new Date(now.getFullYear(), now.getMonth(), 0)
const startDefault = new Date(now.getFullYear(), now.getMonth() - 3, 1)

const toInputDate = (date: Date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const formatCnDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}年${date.getMonth() + 1}月`
}

const form = reactive({
  startDate: toInputDate(startDefault),
  endDate: toInputDate(endDefault),
  storyTitle: '',
  story: '',
})

const analysisState = ref<AnalysisState>('idle')
const analysisSource = ref<'online' | 'fallback'>('fallback')
const analysisError = ref('')
const analysisProgress = ref(0)
const analysisStepIndex = ref(0)
const showPreviewModal = ref(false)
const isGenerating = ref(false)
const hasGeneratedStardust = ref(false)
const generationSource = ref<'online' | 'fallback'>('fallback')
const generationError = ref('')
const generationProgress = ref(0)
const generationStepIndex = ref(0)

const modelSrc = '/model/kanshan.glb'
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const suggestionTopics = ref<string[]>([])
const analysisSteps = [
  '正在读取游客模式下的知乎行为轨迹。',
  '正在聚合浏览、搜索、点赞与收藏线索。',
  '正在识别深夜搜索里的兴趣变化。',
  '正在推断这段时间的认知轨迹。',
  '正在推演星尘标签建议。',
  '即将完成轨迹观察。',
]
const generationSteps = [
  '正在封存这段认知记忆。',
  '正在拆分关键人生节点。',
  '正在寻找内容影响的转折点。',
  '正在整理阶段总结。',
  '正在推演你的阶段看山形象。',
  '正在准备人生星尘预览。',
]
const analysisStepText = computed(() => analysisSteps[analysisStepIndex.value % analysisSteps.length])
const generationStepText = computed(() => generationSteps[generationStepIndex.value % generationSteps.length])

let analysisProgressTimer: number | undefined
let analysisStepTimer: number | undefined
let generationProgressTimer: number | undefined
let generationStepTimer: number | undefined

const startProgress = (progress: typeof analysisProgress, stepIndex: typeof analysisStepIndex) => {
  progress.value = 8
  stepIndex.value = 0
  return {
    progressTimer: window.setInterval(() => {
      if (progress.value < 90) {
        progress.value = Math.min(90, progress.value + Math.ceil(Math.random() * 5))
      }
    }, 700),
    stepTimer: window.setInterval(() => {
      stepIndex.value += 1
    }, 2600),
  }
}

const stopProgress = (
  progress: typeof analysisProgress,
  progressTimer?: number,
  stepTimer?: number,
) => {
  if (progressTimer) window.clearInterval(progressTimer)
  if (stepTimer) window.clearInterval(stepTimer)
  progress.value = 100
}

const guestStory = `那段时间其实是从一个很普通的深夜开始的。我偶然刷到了一篇关于《星际穿越》的长影评，本来只是想随便看看，结果那天凌晨一点，我坐在电脑前，一口气读完了两万多字。里面有一句话让我记了很久：“人真正害怕的，不是宇宙，而是时间。”

后来几周，我开始疯狂搜索诺兰相关内容。《盗梦空间》《信条》《致命魔术》……我几乎每天深夜都会刷知乎上的解析和讨论。很多时候看着看着，窗外已经天亮了。

但慢慢地，我发现自己真正沉迷的已经不是电影，而是那些关于“另一种人生可能”的讨论。那段时间我刚好也处于一种说不上来的迷茫里：每天重复一样的生活，工作稳定，却总觉得自己像被困在某条早就写好的轨道上。

有一天凌晨，我刷到一个回答，里面有人写：“很多人不是突然改变人生的，而是在无数次深夜浏览之后，终于承认自己想换一种活法。”

那天晚上，我第一次认真打开电脑，开始写自己一直想做却不敢做的东西。我重新整理了过去几年记下的想法，辞掉了原本准备继续待下去的工作，开始尝试做内容、学新东西、接触以前完全不敢碰的领域。

后来当然也有焦虑，也有后悔的时候。但至少现在回头看，我已经不是当初那个只是机械重复生活的人了。而一切的开始，只是某个凌晨，我点开了一篇关于诺兰电影的影评。`

const fallbackAnalysisSummary = computed(() => {
  if (analysisState.value === 'empty') {
    return {
      theme: '暂无行为痕迹',
      overview: '那段时间，知乎没有留下足够痕迹。你仍然可以讲述故事，创建属于自己的星尘。',
      metrics: ['可手动补充故事', '仍可生成星尘'],
      sections: [
        { label: '轨迹状态', items: ['系统没有读取到稳定的浏览与搜索线索。'] },
      ],
      shift: '这次星尘将更多依赖你的主动讲述，而不是行为数据。',
      question: '那段时期发生了什么？',
    }
  }

  return {
    theme: '深夜科幻与人生重启',
    overview: `从 ${formatCnDate(form.startDate)} 到 ${formatCnDate(form.endDate)}，你的注意力从诺兰电影解析，逐渐转向时间、选择与人生可能。`,
    metrics: ['深夜浏览集中出现', '科幻长文反复阅读', '人生选择类内容升温'],
    sections: [
      { label: '高频浏览', items: ['反复停留在《星际穿越》与诺兰解析。'] },
      { label: '深夜搜索', items: ['23:00 后更常搜索电影顺序与时间主题。'] },
      { label: '点赞倾向', items: ['更偏向收藏迷茫、选择与重启人生回答。'] },
    ],
    shift: '兴趣从电影本身，迁移到“另一种人生可能”的讨论。',
    question: '你是否正在想换一种活法？',
  }
})
const analysisReport = ref({
  theme: '',
  overview: '',
  metrics: [] as string[],
  sections: [] as { label: string; items: string[] }[],
  shift: '',
  question: '',
})

const wordCount = computed(() => form.story.length)
const exceedLimit = computed(() => wordCount.value > 1000)

const detectEmotion = (text: string) => {
  if (/(迷茫|焦虑|犹豫|压力)/.test(text)) return '波动'
  if (/(兴奋|好奇|尝试|上头)/.test(text)) return '探索'
  if (/(清晰|稳定|坚定|笃定)/.test(text)) return '稳定'
  return '演变'
}

const generatedNodes = computed<GeneratedNode[]>(() => {
  if (generatedByModel.value.nodes.length > 0) {
    return generatedByModel.value.nodes
  }
  const raw = form.story
    .replace(/\n/g, '。')
    .split('。')
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, 4)

  if (raw.length === 0) {
    return [
      { id: 'gen-1', title: '内容触发期', description: '开始被某类内容反复吸引，注意力出现稳定偏移。', emotion: '观察' },
      { id: 'gen-2', title: '兴趣放大期', description: '从偶发浏览变成持续搜索，开始主动保存和比较信息。', emotion: '投入' },
      { id: 'gen-3', title: '行动转化期', description: '内容影响开始外化为行动，认知轨迹发生可感知变化。', emotion: '迁移' },
    ]
  }

  return raw.map((line, index) => ({
    id: `gen-${index + 1}`,
    title: `${index + 1}. ${line.slice(0, 14)}${line.length > 14 ? '…' : ''}`,
    description: line,
    emotion: detectEmotion(line),
  }))
})

const generatedSummary = computed(() => {
  if (generatedByModel.value.summary) return generatedByModel.value.summary
  const seed = form.story.trim() || '你正在把一段被内容影响的经历，整理为可回望的认知轨迹。'
  const short = seed.length > 110 ? `${seed.slice(0, 110)}…` : seed
  return `这段人生阶段的变化主线已形成：${short}`
})

const generatedKanshanState = computed(() => {
  if (generatedByModel.value.liu_kanshan_state) return generatedByModel.value.liu_kanshan_state
  const text = `${form.storyTitle} ${form.story}`
  if (/(迷茫|焦虑|犹豫)/.test(text)) return '看山状态：低声提醒你先稳住节奏，再决定方向。'
  if (/(尝试|学习|行动|开始)/.test(text)) return '看山状态：正在与你并肩推进，把想法转成行动。'
  return '看山状态：持续观察这段轨迹，等待下一次关键分叉。'
})

const generatedByModel = ref<{
  title: string
  tags: string[]
  nodes: GeneratedNode[]
  summary: string
  liu_kanshan_state: string
}>({
  title: '',
  tags: [],
  nodes: [],
  summary: '',
  liu_kanshan_state: '',
})

const runAnalysis = async () => {
  analysisState.value = 'loading'
  analysisError.value = ''
  stopProgress(analysisProgress, analysisProgressTimer, analysisStepTimer)
  const analysisTimers = startProgress(analysisProgress, analysisStepIndex)
  analysisProgressTimer = analysisTimers.progressTimer
  analysisStepTimer = analysisTimers.stepTimer
  if (!form.startDate || !form.endDate || form.startDate > form.endDate) {
    stopProgress(analysisProgress, analysisProgressTimer, analysisStepTimer)
    analysisState.value = 'empty'
    analysisReport.value = fallbackAnalysisSummary.value
    return
  }
  try {
    const resp = await fetch(`${API_BASE}/api/guest/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_date: form.startDate,
        end_date: form.endDate,
        mock_file: 'mock-data/test_data.md',
      }),
    })
    if (!resp.ok) throw new Error(await resp.text())
    const data = await resp.json()
    const obs = data.observation || {}
    analysisReport.value = {
      theme: obs.theme || '认知轨迹观察',
      overview: obs.overview || '',
      metrics: (obs.key_metrics || []).slice(0, 4),
      sections: [
        { label: '高频浏览', items: (obs.high_frequency_browsing || []).slice(0, 2) },
        { label: '深夜搜索', items: (obs.late_night_searches || []).slice(0, 2) },
        { label: '点赞倾向', items: (obs.likes_tendency || []).slice(0, 2) },
      ].filter((section) => section.items.length),
      shift: obs.interest_shift || '',
      question: obs.reflective_question || '',
    }
    suggestionTopics.value = (data.stardust_tag_suggestions || []).slice(0, 6)
    analysisSource.value = 'online'
    stopProgress(analysisProgress, analysisProgressTimer, analysisStepTimer)
    analysisState.value = 'ready'
  } catch (error) {
    analysisError.value = error instanceof Error ? error.message : String(error)
    analysisSource.value = 'fallback'
    stopProgress(analysisProgress, analysisProgressTimer, analysisStepTimer)
    analysisState.value = 'ready'
    analysisReport.value = fallbackAnalysisSummary.value
    suggestionTopics.value = []
  }
}

watch(() => [form.startDate, form.endDate], () => {
  analysisState.value = 'idle'
  analysisReport.value = { theme: '', overview: '', metrics: [], sections: [], shift: '', question: '' }
  analysisError.value = ''
  suggestionTopics.value = []
  analysisProgress.value = 0
})

const fillBySuggestion = (topic: string) => {
  form.storyTitle = topic
}

const fillGuestStory = () => {
  const ok = window.confirm('游客模式体验：是否同意使用示例经历并一键填充到输入框？')
  if (!ok) return
  if (!form.storyTitle) form.storyTitle = '被诺兰影评改变的那段时期'
  form.story = guestStory
}

const cancelBack = () => {
  router.push('/home')
}

const generateStardust = () => {
  if (!form.story.trim()) {
    window.alert('请简单描述一下，那段时期发生了什么。')
    return
  }
  if (exceedLimit.value) {
    window.alert('故事请控制在 1000 字以内。')
    return
  }

  isGenerating.value = true
  generationError.value = ''
  stopProgress(generationProgress, generationProgressTimer, generationStepTimer)
  const generationTimers = startProgress(generationProgress, generationStepIndex)
  generationProgressTimer = generationTimers.progressTimer
  generationStepTimer = generationTimers.stepTimer
  ;(async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/guest/generate-stardust`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: form.startDate,
          end_date: form.endDate,
          story_title: form.storyTitle,
          story_text: form.story,
          mock_file: 'mock-data/test_data.md',
        }),
      })
      if (!resp.ok) throw new Error(await resp.text())
      const data = await resp.json()
      generatedByModel.value = {
        title: data.title || '',
        tags: data.tags || [],
        nodes: data.nodes || [],
        summary: data.summary || '',
        liu_kanshan_state: data.liu_kanshan_state || '',
      }
      if (!form.storyTitle && data.title) form.storyTitle = data.title
      generationSource.value = 'online'
    } catch (error) {
      // fallback to local generation
      generationError.value = error instanceof Error ? error.message : String(error)
      generationSource.value = 'fallback'
    } finally {
      stopProgress(generationProgress, generationProgressTimer, generationStepTimer)
      isGenerating.value = false
      hasGeneratedStardust.value = true
      showPreviewModal.value = true
    }
  })()
}

const joinUniverse = () => {
  const id = `guest-stardust-${Date.now()}`
  const card: Card = {
    id,
    title: form.storyTitle || generatedByModel.value.title || '未命名星尘',
    time_range: `${form.startDate} ~ ${form.endDate}`,
    tags: generatedByModel.value.tags.length > 0 ? generatedByModel.value.tags : suggestionTopics.value.slice(0, 4),
    nodes: generatedNodes.value.map((node, index) => ({
      id: node.id || `${id}-node-${index + 1}`,
      title: node.title,
      description: node.description,
      emotion: node.emotion,
      reading_links: node.reading_links,
    })),
    summary: generatedSummary.value,
    liu_kanshan_state: generatedKanshanState.value,
  }
  saveGuestStardust(card)
  showPreviewModal.value = false
  router.push('/home')
}

onMounted(() => {
  if (document.getElementById('model-viewer-script')) return
  const script = document.createElement('script')
  script.id = 'model-viewer-script'
  script.type = 'module'
  script.src = 'https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js'
  document.head.appendChild(script)
})
</script>

<template>
  <main class="stardust-page relative min-h-screen overflow-hidden text-white">
    <div class="bg-fog fog-a" />
    <div class="bg-fog fog-b" />
    <div class="bg-fog fog-c" />

    <div class="bg-particles" aria-hidden="true">
      <span v-for="i in 20" :key="i" class="particle" />
    </div>

    <div class="mx-auto flex min-h-screen w-full max-w-[1400px] items-center px-6 py-10 lg:px-10">
      <section class="workbench w-full rounded-[34px] border border-white/12 bg-white/[0.04] p-6 shadow-[0_0_45px_rgba(96,165,250,0.12)] backdrop-blur-xl lg:p-8">
        <header class="mb-6">
          <RouterLink to="/home" class="text-sm text-blue-200/70 transition hover:text-blue-100">← 返回主宇宙</RouterLink>
          <p class="mt-5 text-xs uppercase tracking-[0.2em] text-blue-100/55">Create Stardust</p>
          <h1 class="mt-3 text-3xl font-semibold sm:text-4xl">创建人生星尘</h1>
          <p class="mt-4 text-sm leading-7 text-slate-200/72 sm:text-base">
            记录一次被内容改变的瞬间。<br />
            你的虚拟形象就是看山，并会随阶段持续变化。
          </p>
        </header>

        <div class="grid gap-6 lg:grid-cols-2">
          <section class="space-y-4">
            <article class="panel">
              <div class="mb-3 flex items-center justify-between gap-3">
                <h2 class="panel-title">选择一段时间轨迹</h2>
                <button type="button" class="confirm-btn" @click="runAnalysis">确定</button>
              </div>
              <div class="grid gap-3 sm:grid-cols-2">
                <label class="time-input-wrap">
                  <span>起点时间</span>
                  <input v-model="form.startDate" type="date" class="time-input" />
                </label>
                <label class="time-input-wrap">
                  <span>终点时间</span>
                  <input v-model="form.endDate" type="date" class="time-input" />
                </label>
              </div>
            </article>

            <article class="panel">
              <div v-if="analysisState === 'loading'" class="analysis-loading">
                <div class="loading-core" />
                <p>{{ analysisStepText }}</p>
                <div class="inline-progress">
                  <span :style="{ width: `${analysisProgress}%` }" />
                </div>
                <strong>{{ analysisProgress }}%</strong>
              </div>

              <div v-else-if="analysisState === 'idle'">
                <h3 class="panel-title">认知轨迹观察</h3>
                <p class="analysis-text">选择时间轨迹后，点击「确定」开始读取游客模式下的知乎行为轨迹。</p>
              </div>

              <div v-else>
                <div class="flex items-center justify-between gap-3">
                  <h3 class="panel-title">认知轨迹观察</h3>
                  <span class="text-[11px] text-slate-300/70">
                    {{ analysisSource === 'online' ? '系统在线推演' : '本地回退结果' }}
                  </span>
                </div>
                <div class="analysis-report">
                  <div class="analysis-theme">
                    <span>本阶段主题</span>
                    <strong>{{ analysisReport.theme || '认知轨迹观察' }}</strong>
                  </div>

                  <p v-if="analysisReport.overview" class="analysis-text">{{ analysisReport.overview }}</p>

                  <div v-if="analysisReport.metrics.length" class="metric-row">
                    <span v-for="metric in analysisReport.metrics" :key="metric">{{ metric }}</span>
                  </div>

                  <div v-if="analysisReport.sections.length" class="observation-list">
                    <section
                      v-for="section in analysisReport.sections"
                      :key="section.label"
                      class="observation-item"
                    >
                      <h4>{{ section.label }}</h4>
                      <ul>
                        <li v-for="item in section.items" :key="item">{{ item }}</li>
                      </ul>
                    </section>
                  </div>

                  <p v-if="analysisReport.shift" class="shift-line">{{ analysisReport.shift }}</p>
                  <p v-if="analysisReport.question" class="question-line">系统追问：{{ analysisReport.question }}</p>
                </div>
                <p v-if="analysisError" class="mt-3 rounded-xl border border-rose-400/20 bg-rose-500/10 p-3 text-xs leading-5 text-rose-100/80">
                  后端调用未成功：{{ analysisError }}
                </p>
              </div>
            </article>

            <article class="panel">
              <h3 class="panel-title">星尘标签建议</h3>
              <div v-if="suggestionTopics.length" class="mt-3 flex flex-wrap gap-2">
                <button
                  v-for="topic in suggestionTopics"
                  :key="topic"
                  type="button"
                  class="suggestion-pill"
                  @click="fillBySuggestion(topic)"
                >
                  {{ topic }}
                </button>
              </div>
              <p v-else class="mt-3 text-sm leading-7 text-slate-300/72">
                点击「确定」完成轨迹读取后，这里会显示系统推演出的星尘标签建议。
              </p>
            </article>

            <article class="panel">
              <h2 class="panel-title">讲述这段时期的你</h2>
              <input
                v-model="form.storyTitle"
                class="story-title-input"
                placeholder="先给这段记忆起一个标题"
              />
              <textarea
                v-model="form.story"
                class="story-editor mt-3"
                placeholder="从某段时间开始，你被哪些内容持续影响？它如何改变了你的兴趣、情绪和行动？"
              />
              <p class="mt-3 text-xs leading-6 text-slate-300/72">
                游客模式说明：你可以直接使用系统示例文字快速体验推演流程。点击下方按钮即视为你同意将示例内容一键填充到输入框。
              </p>
              <button class="use-story-btn mt-2" type="button" @click="fillGuestStory">同意并一键填充示例文字（游客模式）</button>

              <div class="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-300/70">
                <span class="ml-auto" :class="exceedLimit ? 'text-rose-300' : ''">{{ wordCount }}/1000</span>
              </div>
            </article>
          </section>

          <section class="space-y-4">
            <article class="panel preview-panel">
              <p class="text-xs uppercase tracking-[0.2em] text-blue-100/55">System Memory Card</p>
              <h3 class="mt-2 text-lg font-medium text-white">人生星尘推演预览</h3>
              <p class="mt-3 text-sm leading-7 text-slate-200/75">
                选择时间轨迹并推演人生星尘后，这里会显示系统推演出的星尘标签、阶段摘要和你的阶段看山形象。
              </p>
              <div v-if="hasGeneratedStardust && generatedByModel.tags.length" class="mt-4 flex flex-wrap gap-2">
                <span v-for="tag in generatedByModel.tags" :key="tag" class="tag">#{{ tag }}</span>
              </div>
              <p v-else class="mt-4 text-xs text-slate-300/60">
                推演后显示星尘标签
              </p>
              <p class="mt-6 text-xs uppercase tracking-[0.2em] text-blue-100/55">Stardust Preview · 阶段看山形象</p>
              <div v-if="hasGeneratedStardust" class="model-stage mt-4">
                <p class="mb-2 text-xs text-blue-100/60">你的阶段看山形象（3D）</p>
                <model-viewer
                  class="kanshan-model"
                  :src="modelSrc"
                  camera-controls
                  auto-rotate
                  rotation-per-second="8deg"
                  interaction-prompt="none"
                  shadow-intensity="0.8"
                  exposure="1"
                  disable-zoom
                />
              </div>
              <p v-else class="mt-3 text-sm leading-7 text-slate-300/72">
                点击「生成人生星尘」后，这里将显示系统推演出的阶段看山形象。
              </p>
            </article>

            <div class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <button type="button" class="primary-btn" @click="generateStardust">生成人生星尘</button>
              <button type="button" class="secondary-btn" @click="cancelBack">取消返回</button>
            </div>
          </section>
        </div>
      </section>
    </div>

    <div v-if="isGenerating" class="generating-layer">
      <div class="generating-orbit" />
      <div class="generating-orbit orbit-2" />
      <div class="generating-copy">
        <p>{{ generationStepText }}</p>
        <span>系统正在推演关键节点、整理阶段总结，并构建你的阶段看山形象。</span>
      </div>
      <div class="generation-progress" aria-hidden="true">
        <span :style="{ width: `${generationProgress}%` }" />
      </div>
      <strong class="generation-percent">{{ generationProgress }}%</strong>
    </div>

    <div v-if="showPreviewModal" class="modal-mask" @click.self="showPreviewModal = false">
      <section class="preview-modal">
        <div class="preview-modal-scroll">
          <p class="text-xs uppercase tracking-[0.2em] text-blue-100/55">人生星尘预览</p>
          <p class="mt-1 text-[11px] text-slate-300/70">
            {{ generationSource === 'online' ? '系统在线推演' : '本地回退推演' }}
          </p>
          <p v-if="generationError" class="mt-3 rounded-xl border border-rose-400/20 bg-rose-500/10 p-3 text-xs leading-5 text-rose-100/80">
            后端调用未成功：{{ generationError }}
          </p>
          <div class="mt-4 flex items-end justify-between gap-4">
            <div>
              <h3 class="text-2xl font-medium text-white">{{ form.storyTitle || '未命名星尘' }}</h3>
              <p class="mt-2 text-sm text-slate-200/74">{{ form.startDate }} ~ {{ form.endDate }}</p>
            </div>
            <model-viewer
              class="kanshan-model kanshan-model-modal"
              :src="modelSrc"
              camera-controls
              auto-rotate
              rotation-per-second="8deg"
              interaction-prompt="none"
              shadow-intensity="0.8"
              exposure="1"
              disable-zoom
            />
          </div>

          <section class="mt-5">
            <h4 class="text-sm font-semibold text-slate-100">Timeline 节点链</h4>
            <ol class="mt-4 space-y-6">
              <li
                v-for="(node, index) in generatedNodes"
                :key="node.id"
                class="relative pl-8"
              >
                <span class="timeline-dot absolute left-0 top-1.5 h-3 w-3 rounded-full" />
                <span
                  v-if="index !== generatedNodes.length - 1"
                  class="timeline-line absolute left-[5px] top-5 h-[calc(100%+12px)] w-px"
                />
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <h5 class="text-sm font-semibold text-slate-100">{{ node.title }}</h5>
                    <span class="rounded-full bg-slate-800/80 px-2 py-0.5 text-xs text-slate-300">{{ node.emotion }}</span>
                  </div>
                  <p class="mt-2 text-sm leading-6 text-slate-300">{{ node.description }}</p>
                  <div v-if="node.reading_links?.length" class="mt-2 flex flex-wrap gap-2">
                    <a
                      v-for="(link, linkIndex) in node.reading_links"
                      :key="`${node.id}-${linkIndex}`"
                      :href="link"
                      target="_blank"
                      rel="noreferrer"
                      class="text-xs text-blue-300 underline decoration-blue-400/60 underline-offset-2 hover:text-blue-200"
                    >
                      相关阅读 {{ linkIndex + 1 }}
                    </a>
                  </div>
                </div>
              </li>
            </ol>
          </section>

          <section class="mt-6 rounded-xl border border-slate-700/70 bg-slate-900/45 p-4">
            <h4 class="text-sm font-semibold text-slate-100">阶段总结</h4>
            <p class="mt-2 text-sm leading-7 text-slate-300">{{ generatedSummary }}</p>
            <p class="mt-3 text-sm text-slate-300">{{ generatedKanshanState }}</p>
          </section>
        </div>

        <div class="preview-modal-actions grid grid-cols-1 gap-3 sm:grid-cols-2">
          <button class="primary-btn" type="button" @click="joinUniverse">加入主宇宙</button>
          <button class="secondary-btn" type="button" @click="showPreviewModal = false">继续编辑</button>
        </div>
      </section>
    </div>
    <KanshanGuide
      :steps="[
        '先选一段时间轨迹，让系统读取这段时期的线索。',
        '再补充你的故事，越具体越容易形成星尘。',
        '最后生成预览，满意后加入主宇宙。'
      ]"
    />
  </main>
</template>

<style scoped>
.stardust-page {
  background:
    radial-gradient(circle at 18% 20%, rgba(59, 130, 246, 0.18), transparent 40%),
    radial-gradient(circle at 82% 18%, rgba(168, 85, 247, 0.15), transparent 42%),
    linear-gradient(160deg, #020617 0%, #081126 54%, #020915 100%);
}

.bg-fog {
  position: absolute;
  border-radius: 9999px;
  filter: blur(96px);
  opacity: 0.25;
  pointer-events: none;
  animation: fog-breathe 18s ease-in-out infinite alternate;
}

.fog-a { width: 560px; height: 560px; left: -9%; top: 14%; background: radial-gradient(circle, rgba(59,130,246,0.34), transparent 66%); }
.fog-b { width: 520px; height: 520px; right: -8%; top: 25%; background: radial-gradient(circle, rgba(168,85,247,0.28), transparent 66%); animation-duration: 22s; }
.fog-c { width: 470px; height: 470px; left: 42%; bottom: -14%; background: radial-gradient(circle, rgba(34,211,238,0.2), transparent 68%); animation-duration: 20s; }

.bg-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background: rgba(191, 219, 254, 0.22);
  box-shadow: 0 0 10px rgba(125, 211, 252, 0.16);
  animation: rise linear infinite;
}

.particle:nth-child(1) { left: 6%; animation-duration: 28s; animation-delay: -2s; }
.particle:nth-child(2) { left: 12%; animation-duration: 34s; animation-delay: -9s; }
.particle:nth-child(3) { left: 19%; animation-duration: 24s; animation-delay: -12s; }
.particle:nth-child(4) { left: 27%; animation-duration: 30s; animation-delay: -5s; }
.particle:nth-child(5) { left: 35%; animation-duration: 32s; animation-delay: -10s; }
.particle:nth-child(6) { left: 44%; animation-duration: 29s; animation-delay: -7s; }
.particle:nth-child(7) { left: 52%; animation-duration: 37s; animation-delay: -15s; }
.particle:nth-child(8) { left: 59%; animation-duration: 26s; animation-delay: -14s; }
.particle:nth-child(9) { left: 66%; animation-duration: 35s; animation-delay: -18s; }
.particle:nth-child(10) { left: 73%; animation-duration: 31s; animation-delay: -4s; }
.particle:nth-child(11) { left: 79%; animation-duration: 38s; animation-delay: -16s; }
.particle:nth-child(12) { left: 84%; animation-duration: 27s; animation-delay: -13s; }
.particle:nth-child(13) { left: 89%; animation-duration: 33s; animation-delay: -8s; }
.particle:nth-child(14) { left: 94%; animation-duration: 30s; animation-delay: -19s; }
.particle:nth-child(15) { left: 22%; animation-duration: 36s; animation-delay: -20s; }
.particle:nth-child(16) { left: 48%; animation-duration: 28s; animation-delay: -11s; }
.particle:nth-child(17) { left: 62%; animation-duration: 34s; animation-delay: -21s; }
.particle:nth-child(18) { left: 97%; animation-duration: 32s; animation-delay: -17s; }
.particle:nth-child(19) { left: 40%; animation-duration: 29s; animation-delay: -6s; }
.particle:nth-child(20) { left: 75%; animation-duration: 35s; animation-delay: -22s; }

.workbench {
  position: relative;
}

.panel {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.035);
  backdrop-filter: blur(14px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
  padding: 16px;
}

.panel-title {
  color: rgba(226, 232, 240, 0.9);
  font-size: 15px;
  line-height: 1.7;
  font-weight: 500;
}

.time-input-wrap span {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: rgba(191, 219, 254, 0.72);
}

.time-input,
.story-title-input,
.story-editor {
  width: 100%;
  border: 1px solid transparent;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.45);
  color: rgba(241, 245, 249, 0.9);
  padding: 11px 13px;
  outline: none;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
}

.time-input:focus,
.story-title-input:focus,
.story-editor:focus {
  border-color: rgba(125, 211, 252, 0.4);
  background: rgba(15, 23, 42, 0.56);
  box-shadow: 0 0 0 1px rgba(125, 211, 252, 0.2), 0 0 24px rgba(96, 165, 250, 0.16);
}

.story-editor {
  min-height: 170px;
  resize: vertical;
  line-height: 1.7;
}

.analysis-loading {
  min-height: 96px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.loading-core {
  width: 44px;
  height: 44px;
  border-radius: 9999px;
  background: radial-gradient(circle at 35% 30%, rgba(255,255,255,0.75), rgba(96,165,250,0.28) 38%, rgba(30,64,175,0.2) 62%, transparent 74%);
  box-shadow: 0 0 20px rgba(125, 211, 252, 0.2);
  animation: orbit 2.4s linear infinite;
}

.analysis-loading p {
  color: rgba(191, 219, 254, 0.82);
  font-size: 13px;
}

.analysis-loading strong,
.generation-percent {
  color: rgba(226, 232, 240, 0.82);
  font-size: 12px;
  font-weight: 500;
}

.inline-progress {
  width: min(260px, 100%);
  height: 4px;
  overflow: hidden;
  border-radius: 9999px;
  border: 1px solid rgba(147, 197, 253, 0.18);
  background: rgba(15, 23, 42, 0.75);
}

.inline-progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.35), rgba(191, 219, 254, 0.92), rgba(34, 211, 238, 0.4));
  box-shadow: 0 0 14px rgba(125, 211, 252, 0.28);
  transition: width 0.55s ease;
}

.analysis-text {
  margin-top: 8px;
  color: rgba(226, 232, 240, 0.76);
  font-size: 14px;
  line-height: 1.8;
}

.analysis-report {
  margin-top: 12px;
}

.analysis-theme {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
}

.analysis-theme span {
  color: rgba(147, 197, 253, 0.62);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.analysis-theme strong {
  color: rgba(248, 250, 252, 0.95);
  font-size: 18px;
  font-weight: 600;
}

.metric-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.metric-row span {
  border: 1px solid rgba(125, 211, 252, 0.22);
  border-radius: 9999px;
  background: rgba(14, 165, 233, 0.08);
  color: rgba(191, 219, 254, 0.86);
  font-size: 12px;
  padding: 5px 9px;
}

.observation-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.observation-item {
  border-left: 1px solid rgba(125, 211, 252, 0.24);
  padding-left: 11px;
}

.observation-item h4 {
  color: rgba(147, 197, 253, 0.86);
  font-size: 12px;
  font-weight: 600;
}

.observation-item ul {
  margin-top: 5px;
  display: grid;
  gap: 4px;
}

.observation-item li {
  color: rgba(226, 232, 240, 0.78);
  font-size: 13px;
  line-height: 1.65;
}

.shift-line,
.question-line {
  margin-top: 12px;
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.7;
}

.shift-line {
  background: rgba(15, 23, 42, 0.42);
  color: rgba(226, 232, 240, 0.78);
}

.question-line {
  border: 1px solid rgba(168, 85, 247, 0.18);
  background: rgba(168, 85, 247, 0.08);
  color: rgba(233, 213, 255, 0.88);
}

.suggestion-pill,
.keyword-mini,
.tag,
.emotion-pill,
.cloud-pill {
  border-radius: 9999px;
  border: 1px solid rgba(191, 219, 254, 0.25);
  background: rgba(96, 165, 250, 0.1);
  color: rgba(191, 219, 254, 0.85);
  font-size: 12px;
  padding: 6px 10px;
  transition: all 0.25s ease;
}

.suggestion-pill:hover,
.keyword-mini:hover,
.use-story-btn:hover {
  transform: translateY(-1px);
  border-color: rgba(191, 219, 254, 0.4);
}

.preview-panel {
  background: rgba(12, 20, 38, 0.5);
}

.use-story-btn {
  border: 1px solid rgba(191, 219, 254, 0.3);
  background: rgba(255, 255, 255, 0.07);
  color: rgba(226, 232, 240, 0.9);
  border-radius: 9999px;
  padding: 8px 14px;
  font-size: 13px;
  transition: all 0.25s ease;
}

.model-stage {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  background: rgba(10, 18, 34, 0.45);
  padding: 10px;
}

.kanshan-model {
  width: 100%;
  height: 220px;
  border-radius: 12px;
  background: radial-gradient(circle at 50% 45%, rgba(59, 130, 246, 0.16), rgba(2, 6, 23, 0.1) 58%, rgba(2, 6, 23, 0) 100%);
}

.kanshan-model-modal {
  width: 130px;
  height: 130px;
}

.primary-btn,
.secondary-btn {
  width: 100%;
  border-radius: 9999px;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(12px);
  transition: all 0.25s ease;
}

.confirm-btn {
  border-radius: 9999px;
  border: 1px solid rgba(191, 219, 254, 0.3);
  background: rgba(255, 255, 255, 0.08);
  color: rgba(226, 232, 240, 0.92);
  font-size: 12px;
  padding: 7px 14px;
  transition: all 0.25s ease;
}

.confirm-btn:hover {
  transform: translateY(-1px);
  border-color: rgba(191, 219, 254, 0.42);
  box-shadow: 0 0 18px rgba(96, 165, 250, 0.18);
}

.primary-btn {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 24px rgba(96, 165, 250, 0.18);
}

.secondary-btn {
  color: rgba(226, 232, 240, 0.9);
  background: rgba(255, 255, 255, 0.06);
}

.primary-btn:hover,
.secondary-btn:hover {
  transform: translateY(-2px);
  border-color: rgba(191, 219, 254, 0.34);
}

.generating-layer {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.78);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 60;
}

.generating-orbit {
  width: 110px;
  height: 110px;
  border-radius: 9999px;
  border: 1px solid rgba(125, 211, 252, 0.4);
  box-shadow: 0 0 34px rgba(125, 211, 252, 0.22);
  animation: orbit 4.2s linear infinite;
}

.orbit-2 {
  position: absolute;
  width: 180px;
  height: 180px;
  border-color: rgba(168, 85, 247, 0.24);
  animation-duration: 6.2s;
}

.generating-copy {
  max-width: 420px;
  text-align: center;
}

.generating-copy p {
  color: rgba(226, 232, 240, 0.9);
  font-size: 15px;
}

.generating-copy span {
  display: block;
  margin-top: 8px;
  color: rgba(203, 213, 225, 0.66);
  font-size: 13px;
  line-height: 1.8;
}

.generation-progress {
  width: min(360px, 70vw);
  height: 5px;
  overflow: hidden;
  border-radius: 9999px;
  border: 1px solid rgba(147, 197, 253, 0.18);
  background: rgba(15, 23, 42, 0.8);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 0 18px rgba(96, 165, 250, 0.1);
}

.generation-progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.25), rgba(191, 219, 254, 0.9), rgba(34, 211, 238, 0.38));
  box-shadow: 0 0 18px rgba(125, 211, 252, 0.34);
  transition: width 0.55s ease;
}

.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 70;
  background: rgba(2, 6, 23, 0.78);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  overflow: hidden;
}

.preview-modal {
  display: flex;
  max-height: min(88vh, 780px);
  width: min(760px, 100%);
  flex-direction: column;
  overflow: hidden;
  padding: 0;
  width: min(760px, 100%);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(15, 23, 42, 0.75);
  box-shadow: 0 0 36px rgba(96, 165, 250, 0.18);
  backdrop-filter: blur(14px);
}

.preview-modal-scroll {
  overflow-y: auto;
  padding: 22px 22px 18px;
  scrollbar-color: rgba(147, 197, 253, 0.45) rgba(15, 23, 42, 0.45);
}

.preview-modal-actions {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.86);
  padding: 16px 22px 18px;
  backdrop-filter: blur(14px);
}

.timeline-dot {
  background: #60a5fa;
  box-shadow: 0 0 12px rgba(96, 165, 250, 0.85);
}

.timeline-line {
  background: linear-gradient(180deg, rgba(148, 163, 184, 0.7), rgba(148, 163, 184, 0.2));
}

@keyframes rise {
  0% { bottom: -8%; opacity: 0; transform: translate3d(0, 0, 0) scale(0.85); }
  22% { opacity: 0.22; }
  82% { opacity: 0.12; }
  100% { bottom: 108%; opacity: 0; transform: translate3d(12px, 0, 0) scale(1); }
}

@keyframes fog-breathe {
  from { opacity: 0.17; transform: translate3d(0, 0, 0); }
  to { opacity: 0.3; transform: translate3d(16px, -10px, 0); }
}

@keyframes orbit {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes progress-drift {
  0% {
    transform: translateX(-105%);
  }

  55% {
    transform: translateX(86%);
  }

  100% {
    transform: translateX(240%);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 0.28; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.45; transform: translate(-50%, -50%) scale(1.06); }
}

@media (max-width: 1024px) {
  .workbench {
    padding: 18px;
  }
}
</style>
