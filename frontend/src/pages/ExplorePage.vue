<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import exploreCards from '../data/exploreCards'
import { getSharedSquareStardust } from '../data/guestStardust'
import type { Card } from '../types/card'
import KanshanGuide from '../components/KanshanGuide.vue'

type StarTone = 'blue' | 'purple' | 'gold' | 'cyan'

type StarPoint = {
  card: Card
  id: string
  x: string
  y: string
  size: number
  depth: number
  blur: number
  zIndex: number
  dimension: string
  tone: StarTone
  duration: string
  delay: string
  driftX: string
  driftY: string
  trace: string[]
  tags: string[]
}

const router = useRouter()
const cards = ref<Card[]>([...getSharedSquareStardust(), ...exploreCards])
const activeStarId = ref('')
const pulseTick = ref(0)
let ambientTimer: number | undefined

const centerLine = '这里漂浮着一些，被内容悄悄改变的人生。'
const recommendationLine = '系统会根据你的性格底色与认知轨迹，为你点亮更可能产生共鸣的星云。'

const positionSeeds = [
  { x: 15, y: 18, size: 172, depth: 0.92, z: 8, blur: 0 },
  { x: 33, y: 24, size: 224, depth: 0.96, z: 16, blur: 0 },
  { x: 57, y: 38, size: 286, depth: 1, z: 26, blur: 0 },
  { x: 77, y: 27, size: 204, depth: 0.95, z: 13, blur: 0 },
  { x: 90, y: 35, size: 174, depth: 0.92, z: 7, blur: 0 },
  { x: 22, y: 58, size: 232, depth: 0.98, z: 21, blur: 0 },
  { x: 62, y: 61, size: 198, depth: 0.95, z: 14, blur: 0 },
  { x: 80, y: 66, size: 246, depth: 0.99, z: 22, blur: 0 },
  { x: 14, y: 79, size: 156, depth: 0.9, z: 6, blur: 0 },
  { x: 39, y: 80, size: 208, depth: 0.96, z: 16, blur: 0 },
  { x: 57, y: 84, size: 184, depth: 0.93, z: 11, blur: 0 },
  { x: 76, y: 82, size: 170, depth: 0.92, z: 9, blur: 0 },
]

const refreshCards = () => {
  cards.value = [...getSharedSquareStardust(), ...exploreCards]
}

const inferDimension = (card: Card) => {
  const text = `${card.title} ${card.tags.join(' ')} ${card.summary} ${card.nodes.map((node) => node.description).join(' ')}`
  if (/(AI|大模型|提示词|工具|学习方法)/.test(text)) return 'AI'
  if (/(科幻|宇宙|电影|叙事)/.test(text)) return '科幻'
  if (/(创业|项目|转型|内容创作)/.test(text)) return '创业'
  if (/(迷茫|孤独|焦虑|后悔)/.test(text)) return '孤独'
  if (/(深夜|凌晨|夜|凌晨一点)/.test(text)) return '深夜宇宙'
  if (/(重启|辞掉|改变|另一种活法)/.test(text)) return '重启人生'
  return 'AI'
}

const inferTone = (card: Card): StarTone => {
  const text = `${card.tags.join(' ')} ${card.summary} ${card.nodes.map((node) => node.emotion).join(' ')}`
  if (/(AI|学习|方法|稳定)/.test(text)) return 'cyan'
  if (/(孤独|迷茫|后悔|科幻|宇宙)/.test(text)) return 'purple'
  if (/(重启|改变|长期主义|理性)/.test(text)) return 'gold'
  return 'blue'
}

const inferTrace = (card: Card) => {
  const timeHint = card.title.includes('科幻')
    ? '凌晨 1:42'
    : card.title.includes('AI')
      ? '夜里 12:18'
      : card.title.includes('数码')
        ? '晚上 11:07'
        : '深夜 1:13'

  const searchHint = card.nodes[1]?.title
    ? `连续搜索：${card.nodes[1].title}`
    : `连续搜索：${card.tags.slice(0, 2).join(' / ')}`

  const emotionHint = `情绪标签：${card.nodes[0]?.emotion || '波动'}`
  return [timeHint, searchHint, emotionHint]
}

const toneStyleMap: Record<StarTone, { glow: string; shell: string; ring: string; haze: string }> = {
  blue: {
    glow: 'rgba(96, 165, 250, 0.24)',
    shell: 'rgba(59, 130, 246, 0.12)',
    ring: 'rgba(191, 219, 254, 0.34)',
    haze: 'radial-gradient(circle at 36% 30%, rgba(147, 197, 253, 0.12), rgba(37, 99, 235, 0.08) 34%, rgba(8, 15, 30, 0.1) 64%, rgba(2, 6, 23, 0.5) 100%)',
  },
  purple: {
    glow: 'rgba(167, 139, 250, 0.22)',
    shell: 'rgba(139, 92, 246, 0.1)',
    ring: 'rgba(221, 214, 254, 0.32)',
    haze: 'radial-gradient(circle at 36% 30%, rgba(196, 181, 253, 0.11), rgba(139, 92, 246, 0.08) 34%, rgba(10, 14, 28, 0.1) 64%, rgba(2, 6, 23, 0.52) 100%)',
  },
  gold: {
    glow: 'rgba(245, 158, 11, 0.2)',
    shell: 'rgba(245, 158, 11, 0.1)',
    ring: 'rgba(253, 230, 138, 0.32)',
    haze: 'radial-gradient(circle at 36% 30%, rgba(253, 224, 71, 0.11), rgba(217, 119, 6, 0.08) 34%, rgba(12, 14, 24, 0.12) 64%, rgba(2, 6, 23, 0.54) 100%)',
  },
  cyan: {
    glow: 'rgba(34, 211, 238, 0.22)',
    shell: 'rgba(6, 182, 212, 0.1)',
    ring: 'rgba(165, 243, 252, 0.32)',
    haze: 'radial-gradient(circle at 36% 30%, rgba(103, 232, 249, 0.11), rgba(8, 145, 178, 0.08) 34%, rgba(8, 16, 28, 0.1) 64%, rgba(2, 6, 23, 0.52) 100%)',
  },
}

const starField = computed<StarPoint[]>(() => {
  return cards.value.map((card, index) => {
    const seed = positionSeeds[index % positionSeeds.length]
    const loop = Math.floor(index / positionSeeds.length)
    const dimension = inferDimension(card)
    const tone = inferTone(card)
  const xNudge = ((index % 3) - 1) * 2.8 + loop * 1.6
  const yNudge = ((index % 4) - 1.5) * 2.6 + (loop % 2 === 0 ? loop * 1.4 : loop * -1.2)
    return {
      card,
      id: card.id,
      x: `${Math.min(88, Math.max(12, seed.x + xNudge))}%`,
      y: `${seed.y + yNudge}%`,
      size: Math.max(156, seed.size - loop * 8),
      depth: Math.max(0.82, seed.depth - loop * 0.02),
      blur: 0,
      zIndex: Math.max(4, seed.z - loop),
      dimension,
      tone,
      duration: `${15 + (index % 6) * 2.6}s`,
      delay: `${(index % 7) * 0.7}s`,
      driftX: `${((index % 5) - 2) * 7}px`,
      driftY: `${8 + (index % 4) * 3}px`,
      trace: inferTrace(card),
      tags: card.tags.slice(0, 2),
    }
  })
})

const starConnections = computed(() => {
  const nodes = starField.value
  if (nodes.length < 2) return []
  const pairs = [
    ['科幻', 'AI'],
    ['AI', '创业'],
    ['孤独', '重启人生'],
    ['深夜宇宙', '科幻'],
  ]

  return pairs.map((pair, index) => {
    const from = nodes.find((node) => node.dimension === pair[0])
    const to = nodes.find((node) => node.dimension === pair[1] && node.id !== from?.id)
    if (!from || !to) return null
    const x1 = Number.parseFloat(from.x)
    const y1 = Number.parseFloat(from.y)
    const x2 = Number.parseFloat(to.x)
    const y2 = Number.parseFloat(to.y)
    const dx = x2 - x1
    const dy = y2 - y1
    const length = Math.sqrt(dx * dx + dy * dy)
    const angle = Math.atan2(dy, dx) * (180 / Math.PI)
    return {
      id: `connection-${index}`,
      left: `${x1}%`,
      top: `${y1}%`,
      width: `${length}%`,
      angle,
      delay: `${index * 1.3}s`,
    }
  }).filter(Boolean)
})

const activeSystemLine = computed(() => {
  if (!activeStarId.value) return centerLine
  const active = starField.value.find((item) => item.id === activeStarId.value)
  return active ? `正在观察：${active.card.title}` : centerLine
})

const openDetail = (id: string) => {
  router.push(`/card/${id}`)
}

onMounted(() => {
  window.addEventListener('storage', refreshCards)
  window.addEventListener('guest-stardust-updated', refreshCards)
  window.addEventListener('shared-square-stardust-updated', refreshCards)
  ambientTimer = window.setInterval(() => {
    pulseTick.value += 1
  }, 3000)
})

onUnmounted(() => {
  window.removeEventListener('storage', refreshCards)
  window.removeEventListener('guest-stardust-updated', refreshCards)
  window.removeEventListener('shared-square-stardust-updated', refreshCards)
  if (ambientTimer) window.clearInterval(ambientTimer)
})
</script>

<template>
  <main class="cosmos-page relative min-h-screen overflow-hidden text-slate-100">
    <div class="nebula nebula-a" aria-hidden="true" />
    <div class="nebula nebula-b" aria-hidden="true" />
    <div class="nebula nebula-c" aria-hidden="true" />

    <div class="dust-field" aria-hidden="true">
      <span v-for="index in 20" :key="index" class="dust" />
    </div>

    <div class="rising-particle-field" aria-hidden="true">
      <span v-for="index in 16" :key="index" class="rising-particle" />
    </div>

    <div class="meteor-field" aria-hidden="true">
      <span class="meteor meteor-a" />
      <span class="meteor meteor-b" />
    </div>

    <div class="floating-nav relative z-20 mx-auto w-[calc(100%-2rem)] max-w-[1480px] px-1 py-6 sm:w-[calc(100%-3rem)]">
      <RouterLink to="/home" class="nav-link text-sm text-slate-300/76 hover:text-white">← 返回主宇宙</RouterLink>

      <div class="nav-center text-left">
        <p class="text-[11px] uppercase tracking-[0.36em] text-slate-500">Cognitive Observatory</p>
        <h1 class="mt-2 text-xl font-semibold text-white sm:text-2xl">What If · 看山宇宙广场</h1>
        <p class="mt-2 text-sm text-slate-300/68">{{ activeSystemLine }}</p>
        <p class="mt-2 text-xs leading-6 text-slate-400/58">{{ recommendationLine }}</p>
      </div>

    </div>

    <div class="connection-layer absolute inset-x-0 bottom-[20px] top-[205px] z-10 overflow-hidden md:top-[205px] lg:top-[205px]">
      <div
        v-for="connection in starConnections"
        :key="connection!.id"
        class="star-connection"
        :style="{
          left: connection!.left,
          top: connection!.top,
          width: connection!.width,
          transform: `rotate(${connection!.angle}deg)`,
          animationDelay: connection!.delay,
        }"
      />
    </div>

    <section class="star-ocean absolute inset-0 z-10">
      <div
        v-for="star in starField"
        :key="star.id"
        class="star-wrapper absolute"
        :style="{
          left: star.x,
          top: star.y,
          width: `${star.size}px`,
          height: `${star.size}px`,
          zIndex: String(star.zIndex),
          opacity: activeStarId && activeStarId !== star.id ? '0.72' : String(star.depth),
          filter: star.blur ? `blur(${star.blur}px)` : 'none',
          animationDuration: star.duration,
          animationDelay: star.delay,
          '--drift-x': star.driftX,
          '--drift-y': star.driftY,
        }"
        @mouseenter="activeStarId = star.id"
        @mouseleave="activeStarId = ''"
      >
        <button
          type="button"
          class="star-shell group h-full w-full rounded-full"
          :style="{
            background: toneStyleMap[star.tone].haze,
            borderColor: toneStyleMap[star.tone].ring,
            boxShadow: `0 0 34px ${toneStyleMap[star.tone].glow}, inset 0 0 20px rgba(255,255,255,0.05)`,
          }"
          @click="openDetail(star.id)"
        >
          <span
            class="star-core"
            :style="{
              background: `radial-gradient(circle at 34% 30%, rgba(255,255,255,0.3), ${toneStyleMap[star.tone].shell} 44%, rgba(2,6,23,0.04) 76%)`,
            }"
          />
          <span class="star-ring" :style="{ borderColor: toneStyleMap[star.tone].ring }" />
          <span class="star-halo" :style="{ boxShadow: `0 0 42px ${toneStyleMap[star.tone].glow}` }" />
          <span class="star-noise" />
          <img class="star-kanshan" :src="star.card.liu_kanshan_image || '/images/liukanshan-main.png'" alt="" />

          <div class="star-title-wrap">
            <p class="community-mark">{{ star.card.source_type === 'shared' ? '我分享的星尘' : '看山星尘' }}</p>
            <p class="star-title">{{ star.card.title }}</p>
            <p class="star-time">{{ star.card.time_range }}</p>
            <p class="star-tags">{{ star.tags.map((tag) => `#${tag}`).join(' ') }}</p>
          </div>

          <div class="star-extra">
            <p class="line-clamp text-xs leading-5 text-slate-100/82">{{ star.card.summary }}</p>
            <p class="mt-2 text-[11px] leading-4 text-blue-100/76">刘看山：{{ star.card.liu_kanshan_state }}</p>
          </div>
        </button>
      </div>
    </section>
    <KanshanGuide
      :steps="[
        '这里是看山宇宙广场，漂浮着他人的看山星尘。',
        '悬停星尘，可以先看关键词和阶段状态。',
        '点击星尘，就能进入那段人生轨迹。'
      ]"
    />
  </main>
</template>

<style scoped>
.cosmos-page {
  background-image: url('/images/square_bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.cosmos-page::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 42%, rgba(59, 130, 246, 0.1), rgba(2, 6, 23, 0.32) 52%, rgba(2, 6, 23, 0.72) 100%),
    linear-gradient(135deg, rgba(37, 99, 235, 0.16), rgba(168, 85, 247, 0.1) 45%, rgba(34, 211, 238, 0.06)),
    rgba(2, 6, 23, 0.58);
  pointer-events: none;
}

.floating-nav {
  pointer-events: none;
  height: 185px;
}

.nav-link {
  pointer-events: auto;
}

.nav-link {
  position: absolute;
  left: 0;
  top: 4.75rem;
}

.nav-center {
  position: absolute;
  left: 50%;
  top: 2.55rem;
  max-width: 560px;
  width: min(560px, 48vw);
  transform: translateX(-50%);
  text-align: center;
}

.nav-center h1 {
  font-size: clamp(1.55rem, 2.2vw, 2.25rem);
  line-height: 1.15;
}

.nav-center p:last-child {
  line-height: 1.7;
}

.nebula {
  position: absolute;
  border-radius: 9999px;
  filter: blur(110px);
  opacity: 0.18;
  animation: nebula-drift 18s ease-in-out infinite alternate;
}

.nebula-a {
  left: -8%;
  top: 10%;
  width: 540px;
  height: 540px;
  background: rgba(37, 99, 235, 0.28);
}

.nebula-b {
  right: 6%;
  top: 16%;
  width: 460px;
  height: 460px;
  background: rgba(6, 182, 212, 0.18);
  animation-duration: 23s;
}

.nebula-c {
  left: 34%;
  bottom: -8%;
  width: 620px;
  height: 620px;
  background: rgba(139, 92, 246, 0.16);
  animation-duration: 27s;
}

.dust-field,
.rising-particle-field,
.meteor-field,
.star-ocean {
  pointer-events: none;
}

.star-ocean {
  top: 205px;
  bottom: 20px;
  left: 0;
  right: 0;
}

.dust {
  position: absolute;
  bottom: -10%;
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background: rgba(191, 219, 254, 0.2);
  box-shadow: 0 0 10px rgba(125, 211, 252, 0.16);
  animation: dust-rise linear infinite;
}

.dust:nth-child(1) { left: 7%; animation-duration: 18s; animation-delay: -3s; }
.dust:nth-child(2) { left: 13%; animation-duration: 24s; animation-delay: -10s; }
.dust:nth-child(3) { left: 19%; animation-duration: 20s; animation-delay: -5s; }
.dust:nth-child(4) { left: 29%; animation-duration: 26s; animation-delay: -14s; }
.dust:nth-child(5) { left: 36%; animation-duration: 19s; animation-delay: -7s; }
.dust:nth-child(6) { left: 44%; animation-duration: 22s; animation-delay: -11s; }
.dust:nth-child(7) { left: 52%; animation-duration: 28s; animation-delay: -16s; }
.dust:nth-child(8) { left: 59%; animation-duration: 21s; animation-delay: -6s; }
.dust:nth-child(9) { left: 68%; animation-duration: 25s; animation-delay: -13s; }
.dust:nth-child(10) { left: 76%; animation-duration: 18s; animation-delay: -4s; }
.dust:nth-child(11) { left: 82%; animation-duration: 23s; animation-delay: -9s; }
.dust:nth-child(12) { left: 90%; animation-duration: 27s; animation-delay: -15s; }
.dust:nth-child(13) { left: 11%; animation-duration: 30s; animation-delay: -18s; }
.dust:nth-child(14) { left: 34%; animation-duration: 20s; animation-delay: -2s; }
.dust:nth-child(15) { left: 47%; animation-duration: 24s; animation-delay: -12s; }
.dust:nth-child(16) { left: 61%; animation-duration: 29s; animation-delay: -17s; }
.dust:nth-child(17) { left: 73%; animation-duration: 22s; animation-delay: -8s; }
.dust:nth-child(18) { left: 86%; animation-duration: 26s; animation-delay: -14s; }
.dust:nth-child(19) { left: 94%; animation-duration: 19s; animation-delay: -5s; }
.dust:nth-child(20) { left: 57%; animation-duration: 31s; animation-delay: -20s; }

.rising-particle-field {
  position: absolute;
  inset: 0;
  z-index: 12;
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

.meteor {
  position: absolute;
  width: 140px;
  height: 1px;
  background: linear-gradient(90deg, rgba(191, 219, 254, 0), rgba(191, 219, 254, 0.28), rgba(191, 219, 254, 0));
  opacity: 0;
  filter: blur(0.2px);
}

.meteor-a {
  left: 18%;
  top: 24%;
  transform: rotate(-18deg);
  animation: meteor-pass 24s linear infinite;
}

.meteor-b {
  right: 14%;
  top: 62%;
  transform: rotate(-24deg);
  animation: meteor-pass 31s linear infinite 8s;
}

.star-connection {
  position: absolute;
  height: 1px;
  transform-origin: left center;
  background: linear-gradient(90deg, rgba(96, 165, 250, 0.02), rgba(165, 243, 252, 0.18), rgba(167, 139, 250, 0.02));
  box-shadow: 0 0 10px rgba(125, 211, 252, 0.08);
  animation: line-breath 7s ease-in-out infinite;
}

.star-wrapper {
  pointer-events: auto;
  transform: translate(-50%, -50%);
  animation-name: star-drift;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}

.star-shell {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background:
    linear-gradient(rgba(15, 23, 42, 0.24), rgba(15, 23, 42, 0.5)) padding-box,
    linear-gradient(135deg, rgba(147, 197, 253, 0.34), rgba(168, 85, 247, 0.2), rgba(34, 211, 238, 0.16)) border-box;
  backdrop-filter: blur(12px);
  transition: transform 0.4s ease, box-shadow 0.35s ease, border-color 0.35s ease, opacity 0.35s ease;
}

.star-shell:hover {
  transform: scale(1.06);
}

.star-core,
.star-ring,
.star-halo,
.star-noise,
.star-kanshan,
.star-title-wrap,
.star-extra {
  position: absolute;
  inset: 0;
}

.star-core {
  opacity: 0.62;
  filter: blur(2px);
  transform: scale(1.03);
  transition: opacity 0.35s ease, filter 0.35s ease, transform 0.35s ease;
}

.star-shell:hover .star-core {
  opacity: 0.78;
  filter: blur(1px);
  transform: scale(1.07);
}

.star-ring {
  inset: 10%;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 9999px;
  animation: ring-breath 8s ease-in-out infinite;
}

.star-halo {
  inset: 18%;
  border-radius: 9999px;
  opacity: 0.22;
}

.star-noise {
  border-radius: inherit;
  background:
    radial-gradient(circle at 24% 28%, rgba(255, 255, 255, 0.1), transparent 3%),
    radial-gradient(circle at 70% 62%, rgba(255, 255, 255, 0.07), transparent 3%),
    linear-gradient(180deg, transparent, rgba(2, 6, 23, 0.46));
  opacity: 0.5;
  pointer-events: none;
}

.star-kanshan {
  right: 8%;
  top: 8%;
  z-index: 6;
  width: 30%;
  opacity: 0.96;
  filter: saturate(1.02) brightness(1.05) drop-shadow(0 0 12px rgba(96, 165, 250, 0.24));
  pointer-events: none;
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.star-shell:hover .star-kanshan {
  opacity: 0.95;
  transform: translateY(-2px) scale(1.04);
}

.star-title-wrap {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  z-index: 2;
  padding: 0 13% 13%;
  align-items: flex-start;
  text-align: left;
  text-shadow: 0 0 14px rgba(15, 23, 42, 0.8);
}

.community-mark {
  display: inline-flex;
  margin-bottom: 5px;
  border: 1px solid rgba(125, 211, 252, 0.32);
  border-radius: 9999px;
  background: rgba(14, 165, 233, 0.11);
  padding: 2px 7px;
  color: rgba(191, 219, 254, 0.86);
  font-size: 9px;
  line-height: 1.4;
  box-shadow: 0 0 14px rgba(96, 165, 250, 0.12);
}

.star-title {
  display: -webkit-box;
  overflow: hidden;
  font-size: clamp(0.78rem, 0.88vw, 0.9rem);
  font-weight: 600;
  line-height: 1.34;
  color: rgba(255, 255, 255, 0.92);
  max-width: 100%;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.star-time {
  margin-top: 0.28rem;
  color: rgba(226, 232, 240, 0.58);
  font-size: clamp(0.62rem, 0.72vw, 0.68rem);
  line-height: 1.25;
}

.star-tags {
  margin-top: 0.28rem;
  max-width: 100%;
  overflow: hidden;
  color: rgba(191, 219, 254, 0.7);
  font-size: clamp(0.62rem, 0.72vw, 0.68rem);
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-pill {
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(15, 23, 42, 0.54);
  color: rgba(226, 232, 240, 0.82);
  padding: 0.26rem 0.54rem;
  font-size: 0.7rem;
}

.star-extra {
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

.line-clamp {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.star-shell:hover .star-extra {
  max-height: 128px;
  opacity: 1;
}

@keyframes nebula-drift {
  from {
    transform: translate3d(0, 0, 0) scale(1);
  }

  to {
    transform: translate3d(44px, -28px, 0) scale(1.08);
  }
}

@keyframes dust-rise {
  0% {
    opacity: 0;
    transform: translate3d(0, 0, 0) scale(0.8);
  }

  18% {
    opacity: 0.42;
  }

  76% {
    opacity: 0.22;
  }

  100% {
    opacity: 0;
    transform: translate3d(8px, -112vh, 0) scale(1);
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

@keyframes meteor-pass {
  0%, 86% {
    opacity: 0;
    transform: translate3d(0, 0, 0) rotate(-18deg);
  }

  90% {
    opacity: 0.22;
  }

  100% {
    opacity: 0;
    transform: translate3d(180px, 40px, 0) rotate(-18deg);
  }
}

@keyframes line-breath {
  0%, 100% {
    opacity: 0.16;
  }

  50% {
    opacity: 0.38;
  }
}

@keyframes star-drift {
  0%, 100% {
    transform: translate(-50%, -50%) translate3d(0, 0, 0);
  }

  50% {
    transform: translate(-50%, -50%) translate3d(var(--drift-x), var(--drift-y), 0);
  }
}

@keyframes ring-breath {
  0%, 100% {
    opacity: 0.38;
    transform: scale(0.98);
  }

  50% {
    opacity: 0.72;
    transform: scale(1.03);
  }
}

@media (max-width: 1024px) {
  .floating-nav {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    height: auto;
    min-height: 250px;
    gap: 1rem;
  }

  .nav-center {
    position: static;
    width: min(560px, 100%);
    transform: none;
    text-align: center;
  }

  .nav-link {
    position: static;
  }

  .star-ocean {
    top: 275px;
  }

  .connection-layer {
    top: 275px;
  }
}

@media (max-width: 768px) {
  .star-wrapper {
    transform: translate(-50%, -50%) scale(0.88);
  }

  .star-ocean {
    top: 330px;
  }

  .connection-layer {
    top: 330px;
  }

  .star-title {
    font-size: 0.84rem;
    max-width: 84%;
  }

  .trace-line {
    font-size: 0.72rem;
  }
}
</style>
