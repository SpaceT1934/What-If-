<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { getMainUniverseCards, getParallelStardustByParent } from '../data/guestStardust'
import KanshanGuide from '../components/KanshanGuide.vue'

const router = useRouter()
const route = useRoute()
const cards = ref(getMainUniverseCards())
const hoveredCardId = ref(String(route.query.focus || ''))
let hoverClearTimer: number | undefined

const refreshCards = () => {
  cards.value = getMainUniverseCards()
}

onMounted(() => {
  refreshCards()
  window.addEventListener('storage', refreshCards)
  window.addEventListener('guest-stardust-updated', refreshCards)
})

onUnmounted(() => {
  window.removeEventListener('storage', refreshCards)
  window.removeEventListener('guest-stardust-updated', refreshCards)
})

const sceneClasses = ['scene-ai', 'scene-startup', 'scene-sci-fi']
const hoveredCard = computed(() => cards.value.find((item) => item.id === hoveredCardId.value) ?? null)
const hoveredParallelStardust = computed(() => hoveredCardId.value ? getParallelStardustByParent(hoveredCardId.value) : [])

const deterministicOffset = (index: number, range: number) => {
  const value = Math.sin((index + 1) * 12.9898) * 43758.5453
  return (value - Math.floor(value) - 0.5) * range
}

const bubbles = computed(() => {
  const universeCards = cards.value
  const basePositions = [
    { region: 'left', x: 22, y: 24, size: 174 },
    { region: 'left', x: 30, y: 52, size: 212 },
    { region: 'left', x: 19, y: 74, size: 150 },
    { region: 'center', x: 50, y: 38, size: 276 },
    { region: 'center', x: 58, y: 66, size: 232 },
    { region: 'right', x: 78, y: 26, size: 204 },
    { region: 'right', x: 86, y: 54, size: 166 },
    { region: 'right', x: 76, y: 76, size: 192 },
  ]
  const seed = universeCards.map((_, index) => {
    const base = basePositions[index % basePositions.length]
    const loop = Math.floor(index / basePositions.length)
    return {
      ...base,
      x: Math.min(90, Math.max(14, base.x + loop * 3)),
      y: Math.min(84, Math.max(16, base.y + (loop % 2 === 0 ? 5 : -5))),
      size: Math.max(142, base.size - loop * 12),
    }
  }).map((item, index) => ({
    ...item,
    x: item.x + deterministicOffset(index, 4),
    y: item.y + deterministicOffset(index + 7, 6),
    size: Math.round(item.size + deterministicOffset(index + 13, 16)),
  }))

  return seed.map((pos, index) => {
    const card = universeCards[index]
    const duration = `${(16 + Math.abs(deterministicOffset(index + 21, 8))).toFixed(2)}s`
    const delay = `${Math.abs(deterministicOffset(index + 31, 6)).toFixed(2)}s`
    const amplitude = `${(7 + Math.abs(deterministicOffset(index + 41, 8))).toFixed(1)}px`
    const driftX = `${deterministicOffset(index + 51, 10).toFixed(1)}px`
    const isForeground = pos.region === 'center' || pos.size >= 205
    const hovered = card.id === hoveredCardId.value

    return {
      ...pos,
      card,
      tags: card.tags.slice(0, 2),
      scene: sceneClasses[index % sceneClasses.length],
      hovered,
      hasParallel: getParallelStardustByParent(card.id).length > 0,
      duration,
      delay,
      amplitude,
      driftX,
      displayX: `${pos.x.toFixed(1)}%`,
      displayY: `${pos.y.toFixed(1)}%`,
      displayXValue: pos.x,
      displayYValue: pos.y,
      displaySize: Math.round(pos.size),
      opacity: isForeground ? 1 : 0.6,
      zIndex: isForeground ? 30 + index : 10 + index,
    }
  })
})

const hoveredBubble = computed(() => bubbles.value.find((bubble) => bubble.card.id === hoveredCardId.value) ?? null)
const branchSide = computed(() => {
  const x = hoveredBubble.value?.displayXValue ?? 50
  return x > 64 ? 'left' : 'right'
})
const branchStageStyle = computed(() => {
  const bubble = hoveredBubble.value
  if (!bubble) return {}

  const offset = Math.round(bubble.displaySize / 2 + 26)
  if (branchSide.value === 'left') {
    return {
      left: `calc(${bubble.displayX} - ${offset + 330}px)`,
      top: bubble.displayY,
    }
  }

  return {
    left: `calc(${bubble.displayX} + ${offset}px)`,
    top: bubble.displayY,
  }
})

const keepParallelPreview = (id: string) => {
  if (getParallelStardustByParent(id).length === 0) return
  if (hoverClearTimer) window.clearTimeout(hoverClearTimer)
  hoveredCardId.value = id
}

const scheduleClearParallelPreview = () => {
  if (hoverClearTimer) window.clearTimeout(hoverClearTimer)
  hoverClearTimer = window.setTimeout(() => {
    hoveredCardId.value = ''
  }, 120)
}

const goDetail = (id: string) => {
  router.push(`/card/${id}`)
}
</script>

<template>
  <main class="memory-space relative min-h-screen overflow-hidden text-white">
    <div class="space-glow layer-1" />
    <div class="space-glow layer-2" />
    <div class="space-glow layer-3" />
    <div class="particle-field" aria-hidden="true">
      <span v-for="index in 20" :key="index" class="particle" />
    </div>
    <div class="rising-particle-field" aria-hidden="true">
      <span v-for="index in 16" :key="index" class="rising-particle" />
    </div>

    <aside class="universe-guide absolute bottom-8 left-6 top-8 z-40 w-[30vw] min-w-[320px] max-w-[440px] px-6 py-7 sm:left-8 lg:left-10">
      <div class="guide-copy pt-24 text-center">
        <h1 class="guide-title text-6xl font-semibold leading-none text-white lg:text-7xl">
          What If?
        </h1>
        <p class="mt-4 text-xl font-medium text-slate-100/82">看山主宇宙</p>
        <p class="guide-whisper mx-auto mt-10 max-w-sm text-sm leading-7 text-slate-200/52">
          那些看过和写过的内容，终将改变我们。
        </p>

        <div class="guide-actions mt-14 space-y-4">
          <RouterLink
            to="/create-slice"
            class="create-slice-btn inline-flex w-full items-center justify-center rounded-full px-6 py-3 text-sm font-medium text-white"
          >
            新增星尘
          </RouterLink>
          <RouterLink
            to="/explore"
            class="explore-universe-btn inline-flex w-full items-center justify-center rounded-full px-6 py-3 text-sm font-medium text-slate-200/72"
          >
            进入看山宇宙广场
          </RouterLink>
        </div>
      </div>

      <div class="guide-assistant absolute bottom-9 left-10 right-8 min-h-[150px]" aria-hidden="true">
        <div class="assistant-whisper">
          <p>
            这些漂浮的星尘，记录了内容如何悄悄塑造你。
          </p>
          <p class="mt-3 whitespace-nowrap">你可以重新回望过去的轨迹，继续创造新的人生经历切片，</p>
          <p class="mt-3">
            也可以进入半山宇宙，观察他人的另一种人生可能。
          </p>
        </div>
      </div>
    </aside>

    <section class="bubble-field absolute bottom-0 left-[35%] right-0 top-0 z-10 overflow-hidden">
      <div class="orbit-trails" aria-hidden="true">
        <span class="orbit-trail trail-a" />
        <span class="orbit-trail trail-b" />
        <span class="orbit-trail trail-c" />
      </div>

      <div
        v-for="(bubble, index) in bubbles"
        :key="`${bubble.card.id}-${index}`"
        class="bubble absolute"
        :class="{ 'bubble-hovered': bubble.hovered }"
        :style="{
          left: bubble.displayX,
          top: bubble.displayY,
          width: `${bubble.displaySize}px`,
          height: `${bubble.displaySize}px`,
          zIndex: bubble.hovered ? 80 : bubble.zIndex,
          opacity: bubble.opacity,
          '--float-duration': bubble.duration,
          '--float-delay': bubble.delay,
          '--float-amplitude': bubble.amplitude,
          '--float-drift-x': bubble.driftX,
        }"
      >
        <div
          class="memory-body group h-full w-full"
          :class="bubble.scene"
          role="button"
          tabindex="0"
          @mouseenter="keepParallelPreview(bubble.card.id)"
          @mouseleave="scheduleClearParallelPreview"
          @click="goDetail(bubble.card.id)"
          @keydown.enter="goDetail(bubble.card.id)"
          @keydown.space.prevent="goDetail(bubble.card.id)"
        >
          <div class="memory-scene" />
          <img class="memory-kanshan" :src="bubble.card.liu_kanshan_image || '/images/liukanshan-main.png'" alt="" />
          <div class="memory-noise" />

          <div class="memory-label">
            <span v-if="bubble.card.id.startsWith('guest-stardust-')" class="new-stardust-mark">
              新生成
            </span>
            <span v-if="bubble.hasParallel" class="parallel-count-mark">
              {{ getParallelStardustByParent(bubble.card.id).length }} 条平行分支
            </span>
            <h2 class="truncate text-sm font-medium text-white">{{ bubble.card.title }}</h2>
            <p class="mt-1 text-[11px] leading-4 text-slate-200/58">{{ bubble.card.time_range }}</p>
            <p class="mt-1 truncate text-[11px] leading-4 text-blue-100/70">
              {{ bubble.tags.map((tag) => `#${tag}`).join(' ') }}
            </p>
          </div>

          <div class="memory-extra">
            <p class="line-clamp text-xs leading-5 text-slate-100/76">{{ bubble.card.summary }}</p>
            <p class="mt-2 text-[11px] leading-4 text-blue-100/74">刘看山：{{ bubble.card.liu_kanshan_state }}</p>
            <button
              type="button"
              class="mt-3 rounded-full border border-white/12 bg-white/8 px-3 py-1 text-[11px] text-slate-100/80"
              @click.stop="goDetail(bubble.card.id)"
            >
              进入星尘详情
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="hoveredCard && hoveredParallelStardust.length"
        class="parallel-branch-stage absolute z-[90]"
        :class="branchSide === 'left' ? 'branch-left' : 'branch-right'"
        :style="branchStageStyle"
        @mouseenter="keepParallelPreview(hoveredCard.id)"
        @mouseleave="scheduleClearParallelPreview"
      >
        <div class="branch-line" aria-hidden="true" />
        <div
          v-for="(parallelCard, index) in hoveredParallelStardust"
          :key="parallelCard.id"
          class="parallel-stardust"
          :style="{ '--branch-index': index }"
          role="button"
          tabindex="0"
          @click="goDetail(parallelCard.id)"
          @keydown.enter="goDetail(parallelCard.id)"
          @keydown.space.prevent="goDetail(parallelCard.id)"
        >
          <span class="parallel-mark">平行宇宙推演 · Parallel {{ String(index + 1).padStart(2, '0') }}</span>
          <h3>{{ parallelCard.title }}</h3>
          <p>{{ parallelCard.summary }}</p>
          <span class="parallel-enter">点击进入这条分支</span>
        </div>
      </div>
    </section>
    <KanshanGuide
      :steps="[
        '这里是你的主宇宙。点击一颗星尘，回看人生轨迹。',
        '悬停星尘，可以看到它旁边的平行分支。',
        '想记录新阶段，就点左侧的新增星尘。',
        '想看看别人的星尘，可以进入看山宇宙广场。'
      ]"
    />
  </main>
</template>

<style scoped>
.memory-space {
  background-image: url('/images/main_bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.memory-space::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(circle at 48% 42%, rgba(59, 130, 246, 0.08), rgba(2, 6, 23, 0.24) 52%, rgba(2, 6, 23, 0.68) 100%),
    linear-gradient(135deg, rgba(37, 99, 235, 0.14), rgba(168, 85, 247, 0.08) 46%, rgba(34, 211, 238, 0.05)),
    rgba(2, 6, 23, 0.52);
  pointer-events: none;
}

.space-glow {
  position: absolute;
  border-radius: 9999px;
  filter: blur(90px);
  opacity: 0.28;
  pointer-events: none;
  transform: translate3d(0, 0, 0);
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  animation-direction: alternate;
}

.layer-1 {
  width: 620px;
  height: 620px;
  left: -8%;
  top: 18%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.38), transparent 62%);
  animation-name: glow-drift-blue;
  animation-duration: 18s;
}

.layer-2 {
  width: 560px;
  height: 560px;
  right: -6%;
  top: 6%;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.32), transparent 64%);
  animation-name: glow-drift-purple;
  animation-duration: 20s;
}

.layer-3 {
  width: 520px;
  height: 520px;
  left: 36%;
  bottom: -18%;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.3), transparent 66%);
  animation-name: glow-drift-cyan;
  animation-duration: 16s;
}

.universe-guide {
  background: transparent;
}

.guide-copy {
  animation: info-drift 12s ease-in-out infinite alternate;
}

.guide-title {
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', 'HarmonyOS Sans', sans-serif;
  letter-spacing: 0;
  text-shadow: 0 0 18px rgba(147, 197, 253, 0.12), 0 0 52px rgba(96, 165, 250, 0.1);
}

.guide-whisper {
  text-shadow: 0 0 22px rgba(147, 197, 253, 0.08);
}

.create-slice-btn,
.explore-universe-btn {
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(12px);
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease, border-color 0.25s ease;
}

.create-slice-btn {
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.075);
  box-shadow: 0 0 20px rgba(147, 197, 253, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.create-slice-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(191, 219, 254, 0.13) 42%, transparent 68%);
  transform: translateX(-120%);
  transition: transform 0.85s ease;
}

.create-slice-btn:hover {
  transform: translateY(-2px);
  border-color: rgba(191, 219, 254, 0.24);
  background: rgba(255, 255, 255, 0.105);
  box-shadow: 0 0 26px rgba(147, 197, 253, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.create-slice-btn:hover::after {
  transform: translateX(120%);
}

.explore-universe-btn {
  background: rgba(255, 255, 255, 0.035);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.explore-universe-btn:hover {
  transform: translateY(-1px);
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.07);
}

.guide-assistant {
  animation: assistant-float 10s ease-in-out infinite alternate;
}

.assistant-whisper {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 28px;
  z-index: 2;
  max-width: 330px;
  color: rgba(226, 232, 240, 0.48);
  font-size: 13px;
  line-height: 1.9;
  text-shadow: 0 0 18px rgba(147, 197, 253, 0.1);
}

.assistant-whisper::before {
  content: '';
  position: absolute;
  left: -18px;
  top: 4px;
  width: 1px;
  height: 76%;
  background: linear-gradient(180deg, transparent, rgba(147, 197, 253, 0.34), transparent);
  box-shadow: 0 0 12px rgba(147, 197, 253, 0.14);
}

.particle-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.particle {
  position: absolute;
  width: 2px;
  height: 2px;
  border-radius: 9999px;
  background: rgba(191, 219, 254, 0.18);
  box-shadow: 0 0 8px rgba(125, 211, 252, 0.12);
  animation: particle-drift 24s ease-in-out infinite alternate;
}

.particle:nth-child(1) { left: 8%; top: 18%; animation-duration: 28s; animation-delay: -2s; }
.particle:nth-child(2) { left: 16%; top: 74%; animation-duration: 34s; animation-delay: -8s; }
.particle:nth-child(3) { left: 24%; top: 42%; animation-duration: 26s; animation-delay: -5s; }
.particle:nth-child(4) { left: 31%; top: 22%; animation-duration: 36s; animation-delay: -11s; }
.particle:nth-child(5) { left: 39%; top: 82%; animation-duration: 31s; animation-delay: -4s; }
.particle:nth-child(6) { left: 47%; top: 56%; animation-duration: 33s; animation-delay: -13s; }
.particle:nth-child(7) { left: 53%; top: 30%; animation-duration: 29s; animation-delay: -7s; }
.particle:nth-child(8) { left: 61%; top: 76%; animation-duration: 38s; animation-delay: -10s; }
.particle:nth-child(9) { left: 68%; top: 16%; animation-duration: 27s; animation-delay: -3s; }
.particle:nth-child(10) { left: 73%; top: 48%; animation-duration: 35s; animation-delay: -12s; }
.particle:nth-child(11) { left: 79%; top: 68%; animation-duration: 30s; animation-delay: -6s; }
.particle:nth-child(12) { left: 86%; top: 28%; animation-duration: 37s; animation-delay: -9s; }
.particle:nth-child(13) { left: 92%; top: 82%; animation-duration: 32s; animation-delay: -14s; }
.particle:nth-child(14) { left: 12%; top: 52%; animation-duration: 40s; animation-delay: -15s; }
.particle:nth-child(15) { left: 44%; top: 12%; animation-duration: 33s; animation-delay: -1s; }
.particle:nth-child(16) { left: 57%; top: 88%; animation-duration: 30s; animation-delay: -16s; }
.particle:nth-child(17) { left: 21%; top: 12%; animation-duration: 39s; animation-delay: -18s; }
.particle:nth-child(18) { left: 66%; top: 91%; animation-duration: 34s; animation-delay: -20s; }
.particle:nth-child(19) { left: 84%; top: 8%; animation-duration: 41s; animation-delay: -17s; }
.particle:nth-child(20) { left: 36%; top: 64%; animation-duration: 36s; animation-delay: -22s; }

.rising-particle-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  overflow: hidden;
}

.rising-particle {
  position: absolute;
  bottom: -8%;
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  background: rgba(191, 219, 254, 0.22);
  box-shadow: 0 0 14px rgba(125, 211, 252, 0.2);
  animation: particle-rise linear infinite;
}

.rising-particle:nth-child(1) { left: 7%; animation-duration: 22s; animation-delay: -2s; }
.rising-particle:nth-child(2) { left: 14%; animation-duration: 28s; animation-delay: -11s; }
.rising-particle:nth-child(3) { left: 21%; animation-duration: 24s; animation-delay: -6s; }
.rising-particle:nth-child(4) { left: 31%; animation-duration: 30s; animation-delay: -16s; }
.rising-particle:nth-child(5) { left: 39%; animation-duration: 25s; animation-delay: -9s; }
.rising-particle:nth-child(6) { left: 46%; animation-duration: 32s; animation-delay: -20s; }
.rising-particle:nth-child(7) { left: 54%; animation-duration: 23s; animation-delay: -5s; }
.rising-particle:nth-child(8) { left: 61%; animation-duration: 29s; animation-delay: -14s; }
.rising-particle:nth-child(9) { left: 68%; animation-duration: 26s; animation-delay: -18s; }
.rising-particle:nth-child(10) { left: 73%; animation-duration: 31s; animation-delay: -8s; }
.rising-particle:nth-child(11) { left: 79%; animation-duration: 24s; animation-delay: -12s; }
.rising-particle:nth-child(12) { left: 85%; animation-duration: 33s; animation-delay: -22s; }
.rising-particle:nth-child(13) { left: 91%; animation-duration: 27s; animation-delay: -4s; }
.rising-particle:nth-child(14) { left: 18%; animation-duration: 34s; animation-delay: -24s; }
.rising-particle:nth-child(15) { left: 57%; animation-duration: 30s; animation-delay: -17s; }
.rising-particle:nth-child(16) { left: 96%; animation-duration: 26s; animation-delay: -10s; }

.bubble {
  transform: translate(-50%, -50%);
  animation: bubble-float var(--float-duration) ease-in-out var(--float-delay) infinite;
  border-radius: 9999px;
  transition: opacity 0.32s ease;
  will-change: transform;
}

.bubble-hovered {
  animation-play-state: paused;
}

.orbit-trails {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.58;
}

.orbit-trail {
  position: absolute;
  height: 1px;
  border-radius: 9999px;
  background: linear-gradient(90deg, transparent 0%, rgba(147, 197, 253, 0.22) 32%, rgba(226, 232, 240, 0.48) 50%, rgba(168, 85, 247, 0.14) 68%, transparent 100%);
  background-size: 240% 100%;
  box-shadow: 0 0 16px rgba(96, 165, 250, 0.16);
  filter: blur(0.2px);
  animation: orbit-flow 18s ease-in-out infinite alternate;
  overflow: hidden;
}

.orbit-trail::after {
  content: '';
  position: absolute;
  inset: -1px auto -1px 0;
  width: 24%;
  border-radius: inherit;
  background: linear-gradient(90deg, transparent, rgba(226, 232, 240, 0.62), transparent);
  box-shadow: 0 0 18px rgba(147, 197, 253, 0.22);
  opacity: 0;
  animation: orbit-spark 9s ease-in-out infinite;
}

.trail-a {
  left: 18%;
  top: 35%;
  width: 52%;
  transform: rotate(14deg);
  animation-duration: 22s;
}

.trail-a::after {
  animation-duration: 10s;
  animation-delay: -2s;
}

.trail-b {
  left: 22%;
  top: 61%;
  width: 48%;
  transform: rotate(-18deg);
  animation-duration: 26s;
}

.trail-b::after {
  animation-duration: 12s;
  animation-delay: -6s;
}

.trail-c {
  left: 42%;
  top: 47%;
  width: 38%;
  transform: rotate(28deg);
  animation-duration: 20s;
}

.trail-c::after {
  animation-duration: 11s;
  animation-delay: -4s;
}

.memory-body {
  position: relative;
  overflow: hidden;
  isolation: isolate;
  border: 1px solid transparent;
  border-radius: 46% 54% 50% 50% / 48% 45% 55% 52%;
  clip-path: ellipse(50% 50% at 50% 50%);
  background:
    linear-gradient(rgba(15, 23, 42, 0.26), rgba(15, 23, 42, 0.42)) padding-box,
    linear-gradient(135deg, rgba(147, 197, 253, 0.52), rgba(168, 85, 247, 0.38), rgba(34, 211, 238, 0.28)) border-box;
  backdrop-filter: blur(12px);
  box-shadow: 0 0 22px rgba(100, 150, 255, 0.22), inset 0 0 24px rgba(255, 255, 255, 0.045);
  animation: memory-breathe 16s ease-in-out infinite alternate;
  transform-origin: center;
  transition: transform 0.32s ease, box-shadow 0.32s ease, background-color 0.32s ease, opacity 0.32s ease, border-color 0.32s ease;
  will-change: transform;
  padding: 0;
  cursor: pointer;
  outline: none;
}

.memory-body::before {
  content: '';
  position: absolute;
  inset: -12%;
  border-radius: inherit;
  background: conic-gradient(from 160deg, rgba(96, 165, 250, 0.16), rgba(168, 85, 247, 0.1), rgba(34, 211, 238, 0.14), rgba(96, 165, 250, 0.16));
  filter: blur(18px);
  opacity: 0.58;
  animation: membrane-flow 18s ease-in-out infinite alternate;
}

.memory-body::after {
  content: '';
  position: absolute;
  inset: 8%;
  border-radius: 44% 56% 52% 48% / 55% 45% 55% 45%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  pointer-events: none;
}

.memory-scene,
.memory-noise,
.memory-kanshan,
.memory-label,
.memory-extra {
  position: absolute;
}

.memory-scene {
  inset: 0;
  border-radius: inherit;
  opacity: 0.48;
  filter: blur(10px);
  transform: scale(1.08);
  transition: opacity 0.35s ease, filter 0.35s ease, transform 0.35s ease;
}

.scene-ai .memory-scene {
  background:
    linear-gradient(115deg, rgba(2, 6, 23, 0.2), rgba(37, 99, 235, 0.5), transparent 62%),
    radial-gradient(circle at 68% 35%, rgba(125, 211, 252, 0.46), transparent 24%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.84), rgba(30, 64, 175, 0.42));
}

.scene-sci-fi .memory-scene {
  background:
    radial-gradient(circle at 68% 32%, rgba(216, 180, 254, 0.6), transparent 26%),
    radial-gradient(circle at 28% 66%, rgba(56, 189, 248, 0.34), transparent 24%),
    linear-gradient(140deg, rgba(30, 27, 75, 0.9), rgba(76, 29, 149, 0.4));
}

.scene-startup .memory-scene {
  background:
    linear-gradient(90deg, rgba(15, 23, 42, 0.86), rgba(30, 64, 175, 0.32)),
    repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.12) 0 1px, transparent 1px 18px),
    radial-gradient(circle at 72% 78%, rgba(251, 191, 36, 0.24), transparent 28%);
}

.bubble:hover .memory-scene {
  opacity: 0.74;
  filter: blur(7px);
  transform: scale(1.12);
}

.bubble-hovered .memory-body {
  transform: scale(1.06);
  border-color: rgba(216, 180, 254, 0.36);
  box-shadow: 0 0 34px rgba(168, 85, 247, 0.22), 0 0 58px rgba(59, 130, 246, 0.13), inset 0 0 26px rgba(255, 255, 255, 0.07);
}

.bubble-hovered .memory-scene {
  opacity: 0.82;
  filter: blur(6px);
  transform: scale(1.13);
}

.memory-noise {
  inset: 0;
  border-radius: inherit;
  background:
    radial-gradient(circle at 24% 28%, rgba(255, 255, 255, 0.11), transparent 3%),
    radial-gradient(circle at 70% 62%, rgba(255, 255, 255, 0.08), transparent 3%),
    linear-gradient(180deg, transparent, rgba(2, 6, 23, 0.52));
  opacity: 0.58;
}

.memory-kanshan {
  right: 8%;
  top: 8%;
  z-index: 6;
  width: 30%;
  opacity: 0.96;
  filter: saturate(1.02) brightness(1.05) drop-shadow(0 0 12px rgba(96, 165, 250, 0.24));
  transition: opacity 0.35s ease, transform 0.35s ease;
  transform: translateY(0);
  pointer-events: none;
}

.memory-label {
  left: 14%;
  right: 14%;
  bottom: 14%;
  z-index: 2;
  text-align: left;
  text-shadow: 0 0 14px rgba(15, 23, 42, 0.8);
}

.new-stardust-mark {
  display: inline-flex;
  margin-bottom: 6px;
  border: 1px solid rgba(125, 211, 252, 0.36);
  border-radius: 9999px;
  background: rgba(14, 165, 233, 0.12);
  padding: 2px 8px;
  color: rgba(191, 219, 254, 0.9);
  font-size: 10px;
  line-height: 1.4;
  box-shadow: 0 0 14px rgba(96, 165, 250, 0.14);
}

.parallel-count-mark {
  display: inline-flex;
  margin-bottom: 6px;
  margin-left: 4px;
  border: 1px solid rgba(216, 180, 254, 0.32);
  border-radius: 9999px;
  background: rgba(168, 85, 247, 0.13);
  padding: 2px 8px;
  color: rgba(243, 232, 255, 0.88);
  font-size: 10px;
  line-height: 1.4;
  box-shadow: 0 0 14px rgba(168, 85, 247, 0.14);
}

.memory-extra {
  left: 14%;
  right: 14%;
  top: 16%;
  z-index: 2;
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 0.35s ease, opacity 0.35s ease;
  text-align: left;
}

.parallel-branch-stage {
  width: min(330px, 32vw);
  transform: translateY(-50%);
  pointer-events: auto;
  animation: branch-stage-in 0.26s ease both;
}

.branch-line {
  position: absolute;
  top: 50%;
  width: 64px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(216, 180, 254, 0.48), rgba(125, 211, 252, 0.34));
  box-shadow: 0 0 18px rgba(168, 85, 247, 0.22);
  animation: orbit-flow 12s ease-in-out infinite alternate;
}

.branch-right .branch-line {
  left: -64px;
}

.branch-left .branch-line {
  right: -64px;
  transform: rotate(180deg);
}

.parallel-stardust {
  position: relative;
  pointer-events: auto;
  margin: 14px 0;
  border: 1px solid rgba(216, 180, 254, 0.22);
  border-radius: 28px;
  background:
    radial-gradient(circle at 18% 18%, rgba(216, 180, 254, 0.16), transparent 34%),
    linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(30, 27, 75, 0.84));
  padding: 18px;
  color: rgba(248, 250, 252, 0.9);
  box-shadow: 0 18px 54px rgba(0, 0, 0, 0.32), 0 0 26px rgba(168, 85, 247, 0.12);
  cursor: pointer;
  animation: parallel-float 10s ease-in-out calc(var(--branch-index) * -1.6s) infinite alternate;
  transition: transform 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease;
}

.parallel-stardust:hover {
  transform: translateY(-3px) scale(1.02);
  border-color: rgba(216, 180, 254, 0.36);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.4), 0 0 34px rgba(168, 85, 247, 0.18);
}

.parallel-mark {
  display: inline-flex;
  border: 1px solid rgba(216, 180, 254, 0.28);
  border-radius: 9999px;
  background: rgba(168, 85, 247, 0.14);
  padding: 3px 9px;
  color: rgba(243, 232, 255, 0.86);
  font-size: 10px;
  letter-spacing: 0.06em;
}

.parallel-stardust h3 {
  margin-top: 12px;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.5;
}

.parallel-stardust p {
  display: -webkit-box;
  margin-top: 8px;
  overflow: hidden;
  color: rgba(203, 213, 225, 0.68);
  font-size: 12px;
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.parallel-enter {
  display: inline-flex;
  margin-top: 12px;
  color: rgba(125, 211, 252, 0.82);
  font-size: 11px;
}

.line-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@keyframes bubble-float {
  0% {
    transform: translate(-50%, -50%) translateY(0);
  }

  34% {
    transform: translate(-50%, -50%) translate3d(var(--float-drift-x, 0px), calc(var(--float-amplitude, 10px) * -1), 0);
  }

  68% {
    transform: translate(-50%, -50%) translate3d(calc(var(--float-drift-x, 0px) * -0.75), calc(var(--float-amplitude, 10px) * 0.55), 0);
  }

  100% {
    transform: translate(-50%, -50%) translateY(0);
  }
}

@keyframes membrane-flow {
  from {
    transform: rotate(0deg) scale(1);
    opacity: 0.42;
  }

  to {
    transform: rotate(18deg) scale(1.04);
    opacity: 0.68;
  }
}

@keyframes memory-breathe {
  from {
    box-shadow: 0 0 18px rgba(100, 150, 255, 0.18), inset 0 0 22px rgba(255, 255, 255, 0.04);
  }

  to {
    box-shadow: 0 0 30px rgba(100, 150, 255, 0.28), inset 0 0 28px rgba(255, 255, 255, 0.06);
  }
}

@keyframes parallel-float {
  from {
    transform: translate3d(0, 0, 0);
  }

  to {
    transform: translate3d(10px, -10px, 0);
  }
}

@keyframes branch-stage-in {
  from {
    opacity: 0;
    transform: translate3d(10px, -50%, 0) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translate3d(0, -50%, 0) scale(1);
  }
}

@keyframes glow-drift-blue {
  from {
    transform: translate3d(0, 0, 0);
    opacity: 0.22;
  }

  to {
    transform: translate3d(50px, -30px, 0);
    opacity: 0.36;
  }
}

@keyframes glow-drift-purple {
  from {
    transform: translate3d(0, 0, 0);
    opacity: 0.2;
  }

  to {
    transform: translate3d(-45px, 35px, 0);
    opacity: 0.34;
  }
}

@keyframes glow-drift-cyan {
  from {
    transform: translate3d(0, 0, 0);
    opacity: 0.18;
  }

  to {
    transform: translate3d(36px, -24px, 0);
    opacity: 0.3;
  }
}

@keyframes particle-drift {
  from {
    transform: translate3d(0, 0, 0);
    opacity: 0.06;
  }

  to {
    transform: translate3d(24px, -18px, 0);
    opacity: 0.18;
  }
}

@keyframes particle-rise {
  0% {
    opacity: 0;
    transform: translate3d(0, 0, 0) scale(0.75);
  }

  18% {
    opacity: 0.22;
  }

  76% {
    opacity: 0.14;
  }

  100% {
    opacity: 0;
    transform: translate3d(18px, -112vh, 0) scale(1);
  }
}

@keyframes orbit-flow {
  from {
    background-position: 0% 50%;
    opacity: 0.32;
  }

  to {
    background-position: 100% 50%;
    opacity: 0.62;
  }
}

@keyframes orbit-spark {
  0% {
    opacity: 0;
    transform: translateX(-120%);
  }

  20% {
    opacity: 0.12;
  }

  50% {
    opacity: 0.42;
  }

  82% {
    opacity: 0.1;
  }

  100% {
    opacity: 0;
    transform: translateX(520%);
  }
}

@keyframes assistant-float {
  from {
    transform: translate3d(0, 0, 0);
  }

  to {
    transform: translate3d(0, -8px, 0);
  }
}

@keyframes info-drift {
  from {
    transform: translate3d(0, 0, 0);
  }

  to {
    transform: translate3d(0, -6px, 0);
  }
}

@media (max-width: 900px) {
  .universe-guide {
    bottom: auto;
    left: 1rem;
    right: 1rem;
    top: 1rem;
    width: auto;
    min-width: 0;
    max-width: none;
  }

  .bubble {
    transform: translate(-50%, -50%) scale(0.85);
  }
}
</style>
