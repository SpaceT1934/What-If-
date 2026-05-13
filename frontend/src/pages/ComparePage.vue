<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { findUniverseCard, saveGuestStardust } from '../data/guestStardust'
import { generateWhatIf } from '../data/whatIf'
import type { Card, Node } from '../types/card'
import type { WhatIfScenario, ZhihuSearchResult } from '../types/whatif'

const route = useRoute()
const router = useRouter()
const cardId = computed(() => String(route.params.id))
const card = computed(() => findUniverseCard(cardId.value))

const rewriteInput = ref('')
const scenario = ref<WhatIfScenario | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const scenarioSource = ref<'online' | 'fallback' | null>(null)
const savedParallelId = ref('')
const progress = ref(0)
const stepIndex = ref(0)

const progressSteps = [
  '正在锁定这次分叉发生的最早节点。',
  '正在提炼原故事里的性格与行动方式。',
  '正在约束改写幅度，保持原有人生主题。',
  '正在基于新的起点讲述新的平行故事。',
  '正在整理标签变化与新的看山状态。',
]

let progressTimer: number | undefined
let stepTimer: number | undefined

const startProgress = () => {
  progress.value = 10
  stepIndex.value = 0
  progressTimer = window.setInterval(() => {
    if (progress.value < 90) {
      progress.value = Math.min(90, progress.value + Math.ceil(Math.random() * 6))
    }
  }, 680)
  stepTimer = window.setInterval(() => {
    stepIndex.value += 1
  }, 2200)
}

const stopProgress = () => {
  if (progressTimer) window.clearInterval(progressTimer)
  if (stepTimer) window.clearInterval(stepTimer)
  progress.value = 100
}

watch(
  card,
  (value) => {
    if (value?.nodes[0]) {
      rewriteInput.value = value.nodes[0].description
      scenario.value = null
      errorMessage.value = ''
      scenarioSource.value = null
      savedParallelId.value = ''
    }
  },
  { immediate: true },
)

const firstNode = computed(() => card.value?.nodes[0] ?? null)
const rewriteLength = computed(() => rewriteInput.value.trim().length)
const currentStep = computed(() => progressSteps[stepIndex.value % progressSteps.length])
const canGenerate = computed(() => {
  if (!card.value || !firstNode.value) return false
  return rewriteLength.value >= 8 && rewriteLength.value <= 90 && rewriteInput.value.trim() !== firstNode.value.description.trim()
})

const originalOnlyTags = computed(() => {
  if (!card.value || !scenario.value) return []
  return card.value.tags.filter((tag) => !scenario.value!.rewritten_tags.includes(tag))
})

const rewrittenOnlyTags = computed(() => {
  if (!card.value || !scenario.value) return []
  return scenario.value.rewritten_tags.filter((tag) => !card.value!.tags.includes(tag))
})

const nodeSearchMap = computed(() => {
  const pairs = new Map<string, { query: string; result: ZhihuSearchResult }>()
  for (const item of scenario.value?.node_search_results ?? []) {
    const firstResult = item.results?.[0]
    if (firstResult) {
      pairs.set(item.node_id, { query: item.query, result: firstResult })
    }
  }
  return pairs
})

const truncateText = (text: string | undefined, maxLength: number) => {
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

const buildFallbackScenario = (currentCard: Card, rewrittenOpening: string): WhatIfScenario => {
  const originalNodes = currentCard.nodes
  const first = originalNodes[0]
  const rest = originalNodes.slice(1, 4)

  const rewrittenNodes: Node[] = [
    {
      ...first,
      description: rewrittenOpening,
    },
    ...rest.map((node, index) => ({
      ...node,
      id: `fallback-${node.id}`,
      description:
        index === 0
          ? `因为起点出现了轻微偏移，这一阶段不再完全沿着原节奏推进，而是更早开始出现“${node.title}”的自觉。${node.description}`
          : `在这条 What If 分支里，${node.description}`,
    })),
  ]

  const extraTags = rewrittenOpening.includes('更早') || rewrittenOpening.includes('主动')
    ? ['主动偏移']
    : rewrittenOpening.includes('克制') || rewrittenOpening.includes('暂缓')
      ? ['延迟选择']
      : ['轻微分叉']

  return {
    rewritten_title: '另一种开始',
    rewritten_opening: rewrittenOpening,
    divergence_note: '这次改写没有推翻原来的人，只是换了更早的一步，于是同一个人走出了另一种节奏。',
    rewritten_nodes: rewrittenNodes,
    rewritten_tags: [...currentCard.tags.slice(0, 4), ...extraTags].slice(0, 5),
    rewritten_summary: `新的平行路径保留了这段阶段的核心兴趣和气质，只是把最开始的反应方式轻轻改了一下。于是同样的人、同样的主题，长成了另一种推进节奏，最后形成一条更贴近“${extraTags[0]}”的平行故事。`,
    rewritten_state: '性格底色仍然没变，但做决定的节奏和后续展开出现了新的层次。',
    rewritten_liu_kanshan_state: '看山低声说：你还是你，只是这一次，故事从另一个句子开始。',
    zhihu_search_queries: [rewrittenOpening.slice(0, 18), currentCard.tags[0] ?? currentCard.title].filter(Boolean),
    zhihu_search_results: [],
    node_search_results: [],
  }
}

const handleGenerate = async () => {
  if (!card.value || !firstNode.value) return
  if (!canGenerate.value) {
    errorMessage.value = '请只微调第一节点的一小段描述，长度保持在 8 到 90 字之间。'
    return
  }

  loading.value = true
  errorMessage.value = ''
  startProgress()

  try {
    const result = await generateWhatIf(card.value, rewriteInput.value.trim())
    scenario.value = result
    scenarioSource.value = 'online'
  } catch (error) {
    scenario.value = buildFallbackScenario(card.value, rewriteInput.value.trim())
    scenarioSource.value = 'fallback'
    errorMessage.value = '系统推演暂时没有成功返回，当前先展示一版本地分叉结果用于继续体验。'
    console.error(error)
  } finally {
    loading.value = false
    stopProgress()
  }
}

const saveParallelStardust = () => {
  if (!card.value || !scenario.value) return

  const id = `parallel-stardust-${card.value.id}-${Date.now()}`
  const parallelCard: Card = {
    id,
    title: scenario.value.rewritten_title || `${card.value.title}的另一种可能`,
    time_range: card.value.time_range,
    tags: ['平行宇宙', ...scenario.value.rewritten_tags].slice(0, 5),
    nodes: scenario.value.rewritten_nodes,
    summary: scenario.value.rewritten_summary,
    liu_kanshan_state: scenario.value.rewritten_liu_kanshan_state,
    source_type: 'parallel',
    parent_id: card.value.id,
    source_label: '由 What If 平行宇宙推演',
  }

  saveGuestStardust(parallelCard)
  savedParallelId.value = id
  router.push({ path: '/home', query: { focus: card.value.id, branch: id } })
}
</script>

<template>
  <main class="min-h-screen bg-slate-950 text-slate-100">
    <div class="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <RouterLink to="/home" class="text-sm font-medium text-blue-300 hover:text-blue-200">← 返回首页</RouterLink>

      <section
        v-if="card"
        class="mt-5 rounded-2xl border border-slate-800 bg-slate-900/70 shadow-[0_0_40px_rgba(15,23,42,0.55)]"
      >
        <header class="border-b border-slate-800 px-6 py-6">
          <p class="text-xs font-semibold uppercase tracking-wide text-blue-300">What If Compare</p>
          <h1 class="mt-2 text-2xl font-bold text-white sm:text-3xl">{{ card.title }}</h1>
          <p class="mt-2 text-sm text-slate-300">换一个更轻微的开头，让同一个人走出另一段平行故事</p>
        </header>

        <div class="relative grid grid-cols-1 lg:grid-cols-2">
          <div class="pointer-events-none absolute left-1/2 top-0 hidden h-full w-px -translate-x-1/2 bg-slate-700 lg:block" />

          <section class="path-left border-b border-slate-800 p-6 lg:border-b-0">
            <h2 class="text-base font-semibold text-blue-300">原路径</h2>
            <p class="mt-1 text-sm text-slate-300">{{ card.time_range }}</p>

            <ol class="mt-5 space-y-5">
              <li
                v-for="(node, index) in card.nodes"
                :key="node.id"
                class="timeline-fade-in relative pl-8"
                :style="{ animationDelay: `${index * 0.08}s` }"
              >
                <span class="node-dot node-blue absolute left-0 top-1.5" />
                <span
                  v-if="node.id !== card.nodes[card.nodes.length - 1].id"
                  class="node-line node-blue absolute left-[7px] top-5 h-[calc(100%+12px)] w-px"
                />
                <h3 class="text-sm font-semibold text-white">{{ node.title }}</h3>
                <p class="mt-1 text-sm leading-6 text-slate-300">{{ node.description }}</p>
              </li>
            </ol>

            <div class="mt-6">
              <h3 class="text-sm font-semibold text-slate-100">原标签</h3>
              <div class="mt-2 flex flex-wrap gap-2">
                <span
                  v-for="tag in card.tags"
                  :key="`origin-${tag}`"
                  class="rounded-full border border-blue-300/30 bg-blue-500/10 px-2.5 py-1 text-xs text-blue-200"
                >
                  #{{ tag }}
                </span>
              </div>
            </div>

            <div class="mt-6 rounded-xl border border-blue-400/20 bg-blue-500/10 p-4">
              <p class="text-sm text-slate-200"><span class="font-semibold text-blue-300">阶段总结：</span>{{ card.summary }}</p>
              <p class="mt-2 text-sm text-slate-200">
                <span class="font-semibold text-blue-300">刘看山状态：</span>{{ card.liu_kanshan_state }}
              </p>
            </div>
          </section>

          <section class="path-right p-6">
            <div class="mb-4 flex items-center justify-center lg:justify-start">
              <div class="fork-badge">节点分叉点</div>
            </div>

            <h2 class="text-base font-semibold text-fuchsia-300">平行起点微调</h2>
            <p class="mt-1 text-sm text-slate-300">
              只改写第一个节点的一小段描述，系统会沿着原来的性格与气质，从这个新开头继续推演下去。
            </p>

            <div v-if="firstNode" class="mt-5 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-xs uppercase tracking-[0.18em] text-slate-400">Opening Node</p>
                  <h3 class="mt-1 text-sm font-semibold text-white">{{ firstNode.title }}</h3>
                </div>
                <span class="rounded-full border border-white/10 bg-slate-900/70 px-2.5 py-1 text-xs text-slate-300">
                  {{ rewriteLength }}/90
                </span>
              </div>

              <textarea
                v-model="rewriteInput"
                rows="5"
                maxlength="90"
                class="whatif-input mt-4 w-full resize-none rounded-2xl px-4 py-3 text-sm leading-6 text-slate-100 outline-none"
                placeholder="例如：如果当时没有立刻沉迷于设定，而是先把注意力放在人物情感上……"
              />

              <p class="mt-3 text-xs leading-6 text-slate-400">
                这里只允许轻微调整起点，不建议改掉整段阶段的主题、身份、兴趣方向或人生底色。
              </p>

              <div class="mt-4 flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  class="generate-btn inline-flex items-center justify-center rounded-full px-5 py-2.5 text-sm font-medium text-white disabled:pointer-events-none disabled:opacity-50"
                  :disabled="loading"
                  @click="handleGenerate"
                >
                  {{ loading ? '正在推演平行轨迹...' : '系统推演 What If 续写' }}
                </button>
                <p class="text-xs text-slate-400">建议只改一句话，让系统用同一个人的性格去推演另一种后续。</p>
              </div>
            </div>

            <div v-if="loading" class="mt-6 rounded-2xl border border-fuchsia-300/15 bg-fuchsia-500/8 p-4">
              <div class="flex items-center justify-between text-xs text-slate-300">
                <span>{{ currentStep }}</span>
                <span>{{ progress }}%</span>
              </div>
              <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
                <div class="h-full rounded-full bg-gradient-to-r from-blue-400 via-cyan-300 to-fuchsia-400 transition-all duration-500" :style="{ width: `${progress}%` }" />
              </div>
            </div>

            <p v-if="errorMessage" class="mt-4 rounded-2xl border border-amber-300/15 bg-amber-500/10 px-4 py-3 text-sm leading-6 text-amber-100/82">
              {{ errorMessage }}
            </p>

            <section v-if="scenario" class="mt-6">
              <div class="flex flex-wrap items-center gap-3">
                <h2 class="text-base font-semibold text-fuchsia-300">改写路径</h2>
                <span
                  class="rounded-full border px-2.5 py-1 text-[11px]"
                  :class="scenarioSource === 'online'
                    ? 'border-emerald-300/20 bg-emerald-500/10 text-emerald-200'
                    : 'border-amber-300/20 bg-amber-500/10 text-amber-100'"
                >
                  {{ scenarioSource === 'online' ? '系统在线推演' : '本地兜底推演' }}
                </span>
              </div>

              <p class="mt-2 text-sm leading-6 text-slate-300">{{ scenario.divergence_note }}</p>

              <ol class="mt-5 space-y-5">
                <li
                  v-for="(node, index) in scenario.rewritten_nodes"
                  :key="node.id"
                  class="whatif-node timeline-fade-in relative pl-8"
                  :style="{ animationDelay: `${index * 0.08}s` }"
                >
                  <span class="node-dot node-purple absolute left-0 top-1.5" />
                  <span
                    v-if="node.id !== scenario.rewritten_nodes[scenario.rewritten_nodes.length - 1].id"
                    class="node-line node-purple absolute left-[7px] top-5 h-[calc(100%+12px)] w-px"
                  />
                  <div class="relative z-30 flex flex-wrap items-start justify-between gap-3">
                    <h3 class="text-sm font-semibold text-white">{{ node.title }}</h3>
                    <a
                      v-if="nodeSearchMap.get(node.id)"
                      :href="nodeSearchMap.get(node.id).result.url"
                      target="_blank"
                      rel="noreferrer"
                      class="node-link group relative z-50 w-[138px] rounded-full border border-cyan-200/20 bg-cyan-300/10 px-3 py-1 text-[11px] text-cyan-100 sm:w-[168px]"
                    >
                      <span class="block truncate">{{ truncateText(nodeSearchMap.get(node.id).result.title, 15) }}</span>
                      <span class="node-link-card pointer-events-none absolute right-0 top-9 z-[9999] w-64 rounded-2xl border border-cyan-200/24 bg-[#020617] p-4 text-left opacity-0 shadow-[0_22px_70px_rgba(0,0,0,0.7),0_0_24px_rgba(34,211,238,0.12)] transition duration-200 group-hover:translate-y-1 group-hover:opacity-100 sm:w-72">
                        <span class="block text-[10px] uppercase tracking-[0.16em] text-cyan-200/70">Zhihu Search</span>
                        <span class="mt-2 block text-sm font-semibold leading-6 text-slate-100">{{ truncateText(nodeSearchMap.get(node.id).result.title, 34) }}</span>
                        <span v-if="nodeSearchMap.get(node.id).result.content_text" class="mt-2 block text-xs leading-5 text-slate-400">
                          {{ truncateText(nodeSearchMap.get(node.id).result.content_text, 96) }}
                        </span>
                        <span class="mt-3 flex flex-wrap gap-2 text-[11px] text-slate-500">
                          <span v-if="nodeSearchMap.get(node.id).result.author_name">{{ truncateText(nodeSearchMap.get(node.id).result.author_name, 8) }}</span>
                          <span v-if="nodeSearchMap.get(node.id).result.vote_up_count">赞同 {{ nodeSearchMap.get(node.id).result.vote_up_count }}</span>
                          <span>搜索：{{ truncateText(nodeSearchMap.get(node.id).query, 16) }}</span>
                        </span>
                      </span>
                    </a>
                  </div>
                  <p class="mt-1 text-sm leading-6 text-slate-300">{{ node.description }}</p>
                </li>
              </ol>

              <div v-if="scenario.zhihu_search_queries?.length && nodeSearchMap.size === 0" class="mt-6 rounded-2xl border border-cyan-300/15 bg-cyan-400/[0.06] p-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 class="text-sm font-semibold text-cyan-100">知乎搜索关键词</h3>
                    <p class="mt-1 text-xs leading-5 text-slate-400">已推演节点搜索词。确认知乎 Access Secret 可用后，节点旁会显示真实结果链接。</p>
                  </div>
                </div>

                <div class="mt-3 flex flex-wrap gap-2">
                  <span
                    v-for="query in scenario.zhihu_search_queries"
                    :key="`query-${query}`"
                    class="rounded-full border border-cyan-200/20 bg-cyan-300/10 px-2.5 py-1 text-[11px] text-cyan-100"
                  >
                    {{ query }}
                  </span>
                </div>
              </div>

              <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <h3 class="text-sm font-semibold text-slate-100">新增标签</h3>
                  <div class="mt-2 flex flex-wrap gap-2">
                    <span
                      v-for="tag in rewrittenOnlyTags"
                      :key="`new-${tag}`"
                      class="rounded-full border border-fuchsia-300/30 bg-fuchsia-500/10 px-2.5 py-1 text-xs text-fuchsia-200"
                    >
                      + #{{ tag }}
                    </span>
                    <span v-if="rewrittenOnlyTags.length === 0" class="text-xs text-slate-500">这条分支没有明显新增标签。</span>
                  </div>
                </div>

                <div>
                  <h3 class="text-sm font-semibold text-slate-100">减少标签</h3>
                  <div class="mt-2 flex flex-wrap gap-2">
                    <span
                      v-for="tag in originalOnlyTags"
                      :key="`old-${tag}`"
                      class="rounded-full border border-slate-600 bg-slate-800 px-2.5 py-1 text-xs text-slate-400 line-through"
                    >
                      #{{ tag }}
                    </span>
                    <span v-if="originalOnlyTags.length === 0" class="text-xs text-slate-500">原标签基本被保留下来了。</span>
                  </div>
                </div>
              </div>

              <div class="mt-6 rounded-xl border border-fuchsia-300/20 bg-fuchsia-500/10 p-4">
                <p class="text-sm text-slate-200">
                  <span class="font-semibold text-fuchsia-300">平行总结：</span>{{ scenario.rewritten_summary }}
                </p>
                <p class="mt-2 text-sm text-slate-200">
                  <span class="font-semibold text-fuchsia-300">状态变化：</span>{{ scenario.rewritten_state }}
                </p>
                <p class="mt-2 text-sm text-slate-200">
                  <span class="font-semibold text-fuchsia-300">刘看山状态变化：</span>{{ scenario.rewritten_liu_kanshan_state }}
                </p>
              </div>

              <div class="mt-5 flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  class="save-parallel-btn inline-flex items-center justify-center rounded-full px-5 py-2.5 text-sm font-medium text-white"
                  @click="saveParallelStardust"
                >
                  保存为平行宇宙星尘
                </button>
                <p class="text-xs leading-5 text-slate-400">
                  保存后会回到主宇宙，并在原星尘旁显示这条平行分支。
                </p>
              </div>
            </section>

            <div v-else-if="!loading" class="mt-6 rounded-2xl border border-dashed border-white/10 bg-white/[0.03] px-5 py-6">
              <p class="text-sm leading-7 text-slate-300">
                先微调第一节点的一句话，再让系统从这个新的开头继续推演。
                这不是推翻原来的人生，而是看看同一个人，用另一种起笔，会不会写出另一段平行故事。
              </p>
            </div>
          </section>

          <div class="pointer-events-none absolute left-1/2 top-24 hidden h-16 w-24 -translate-x-1/2 split-branch lg:block" />
        </div>
      </section>

      <section v-else class="mt-5 rounded-2xl border border-slate-700 bg-slate-900 p-6 text-slate-300 shadow-sm">
        未找到对应对比数据。
      </section>
    </div>
  </main>
</template>

<style scoped>
.path-left {
  background: linear-gradient(180deg, rgba(37, 99, 235, 0.08), rgba(15, 23, 42, 0));
}

.path-right {
  background: linear-gradient(180deg, rgba(168, 85, 247, 0.08), rgba(15, 23, 42, 0));
}

.node-dot {
  width: 14px;
  height: 14px;
  border-radius: 9999px;
}

.node-line {
  opacity: 0.9;
}

.node-blue {
  background: #60a5fa;
  box-shadow: 0 0 14px rgba(96, 165, 250, 0.8);
}

.node-purple {
  background: #c084fc;
  box-shadow: 0 0 14px rgba(192, 132, 252, 0.8);
}

.node-line.node-blue {
  background: linear-gradient(180deg, rgba(96, 165, 250, 0.85), rgba(96, 165, 250, 0.2));
}

.node-line.node-purple {
  background: linear-gradient(180deg, rgba(192, 132, 252, 0.85), rgba(192, 132, 252, 0.2));
}

.fork-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.8rem;
  border-radius: 9999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.7);
  color: #cbd5e1;
  font-size: 0.75rem;
  letter-spacing: 0.02em;
}

.whatif-input {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(2, 6, 23, 0.6);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.whatif-input:focus {
  border-color: rgba(192, 132, 252, 0.35);
  box-shadow: 0 0 0 1px rgba(192, 132, 252, 0.18), 0 0 24px rgba(192, 132, 252, 0.12);
}

.generate-btn {
  border: 1px solid rgba(216, 180, 254, 0.24);
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.32), rgba(59, 130, 246, 0.18));
  box-shadow: 0 0 20px rgba(192, 132, 252, 0.16);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  border-color: rgba(216, 180, 254, 0.36);
  box-shadow: 0 0 26px rgba(192, 132, 252, 0.22);
}

.save-parallel-btn {
  border: 1px solid rgba(216, 180, 254, 0.28);
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.34), rgba(34, 211, 238, 0.14));
  box-shadow: 0 0 22px rgba(168, 85, 247, 0.18);
  transition: transform 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease;
}

.save-parallel-btn:hover {
  transform: translateY(-2px);
  border-color: rgba(216, 180, 254, 0.44);
  box-shadow: 0 0 30px rgba(168, 85, 247, 0.26);
}

.node-link {
  transition: transform 0.25s ease, border-color 0.25s ease, background 0.25s ease, box-shadow 0.25s ease;
}

.node-link:hover {
  transform: translateY(-2px);
  z-index: 10000;
  border-color: rgba(125, 211, 252, 0.26);
  background: rgba(8, 47, 73, 0.22);
  box-shadow: 0 0 24px rgba(34, 211, 238, 0.1);
}

.whatif-node:hover {
  z-index: 10000;
}

.node-link-card {
  transform: translateY(-4px);
  max-height: 13.5rem;
  overflow: hidden;
}

.split-branch {
  opacity: 0;
  animation: split-branch-in 0.6s ease forwards;
}

.split-branch::before,
.split-branch::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 52%;
  height: 1px;
}

.split-branch::before {
  left: 0;
  transform: rotate(-25deg);
  transform-origin: right center;
  background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.95));
  box-shadow: 0 0 8px rgba(96, 165, 250, 0.6);
}

.split-branch::after {
  right: 0;
  transform: rotate(25deg);
  transform-origin: left center;
  background: linear-gradient(90deg, rgba(192, 132, 252, 0.95), transparent);
  box-shadow: 0 0 8px rgba(192, 132, 252, 0.6);
}

@keyframes split-branch-in {
  from {
    opacity: 0;
    transform: translateX(-50%) scaleX(0.7);
  }

  to {
    opacity: 1;
    transform: translateX(-50%) scaleX(1);
  }
}
</style>
