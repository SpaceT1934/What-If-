<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

const showText = ref(false)
const showButton = ref(false)

const leftFragments = [
  '长期阅读知乎高赞文章会改变认知吗？',
  '如何走出人生的迷茫期？',
  '为什么有些选择会影响很多年？',
  '你是如何做出那个决定的？',
]

const rightFragments = [
  '如果当时看到的是另一种答案？',
  '平行宇宙中的你现在怎么样？',
  '那些未被选择的可能性...',
  '如果重新经历一次会怎样？',
]

onMounted(() => {
  window.setTimeout(() => {
    showText.value = true
  }, 300)

  window.setTimeout(() => {
    showButton.value = true
  }, 900)
})
</script>

<template>
  <main class="landing-page relative flex min-h-screen items-center justify-center overflow-hidden text-white">
    <div class="landing-overlay" aria-hidden="true" />
    <div class="cosmic-trails" aria-hidden="true">
      <span class="trail trail-1" />
      <span class="trail trail-2" />
      <span class="trail trail-3" />
    </div>
    <div class="landing-particles" aria-hidden="true">
      <span v-for="index in 14" :key="index" class="landing-particle" />
    </div>

    <div class="thought-fragments left-fragments" aria-hidden="true">
      <span v-for="(item, index) in leftFragments" :key="item" :class="`fragment fragment-left-${index + 1}`">
        {{ item }}
      </span>
    </div>

    <div class="thought-fragments right-fragments" aria-hidden="true">
      <span v-for="(item, index) in rightFragments" :key="item" :class="`fragment fragment-right-${index + 1}`">
        {{ item }}
      </span>
    </div>

    <section class="relative z-10 mx-auto max-w-5xl px-6 text-center">
      <h1
        :class="[
          'poster-title mx-auto text-[3.5rem] font-semibold leading-none text-white transition-all duration-700 sm:text-[5rem] lg:text-[7rem]',
          showText ? 'translate-y-0 opacity-100' : 'translate-y-3 opacity-0',
        ]"
      >
        What If?
      </h1>

      <p
        :class="[
          'mt-14 text-xl font-medium text-slate-100 transition-all delay-150 duration-700 sm:text-2xl',
          showText ? 'translate-y-0 opacity-100' : 'translate-y-3 opacity-0',
        ]"
      >
        每一次选择，都有另一种可能
      </p>

      <p
        :class="[
          'mx-auto mt-7 max-w-2xl whitespace-pre-line text-sm leading-7 text-slate-200/62 transition-all delay-300 duration-700 sm:text-base',
          showText ? 'translate-y-0 opacity-100' : 'translate-y-3 opacity-0',
        ]"
      >
        记录内容如何影响一段星尘，
        探索平行人生的无限可能
      </p>

      <RouterLink
        to="/letter"
        :class="[
          'glass-btn mt-16 inline-flex items-center justify-center px-8 py-3.5 text-sm font-medium text-white transition-all duration-500',
          showButton ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0',
        ]"
      >
        进入看山宇宙
      </RouterLink>
    </section>
  </main>
</template>

<style scoped>
.landing-page {
  background-image: url('/images/landing-bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.landing-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 42%, rgba(59, 130, 246, 0.12), rgba(2, 6, 23, 0.36) 52%, rgba(2, 6, 23, 0.7) 100%),
    linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(168, 85, 247, 0.12) 45%, rgba(34, 211, 238, 0.08)),
    rgba(2, 6, 23, 0.65);
}

.poster-title {
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', 'HarmonyOS Sans', sans-serif;
  letter-spacing: 0;
  text-shadow: 0 0 12px rgba(226, 232, 240, 0.14), 0 0 32px rgba(96, 165, 250, 0.14);
}

.cosmic-trails {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
  opacity: 0.72;
}

.trail {
  position: absolute;
  height: 1px;
  border-radius: 9999px;
  filter: blur(0.5px);
  animation: trail-drift ease-in-out infinite alternate;
}

.trail-1 {
  left: 18%;
  top: 38%;
  width: 64%;
  transform: rotate(-16deg);
  background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.55), rgba(168, 85, 247, 0.34), transparent);
  box-shadow: 0 0 18px rgba(96, 165, 250, 0.24);
  animation-duration: 18s;
}

.trail-2 {
  left: 24%;
  top: 56%;
  width: 52%;
  transform: rotate(13deg);
  background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.38), rgba(168, 85, 247, 0.32), transparent);
  box-shadow: 0 0 18px rgba(168, 85, 247, 0.18);
  animation-duration: 20s;
}

.trail-3 {
  left: 34%;
  top: 28%;
  width: 38%;
  transform: rotate(22deg);
  background: linear-gradient(90deg, transparent, rgba(147, 197, 253, 0.42), transparent);
  box-shadow: 0 0 14px rgba(147, 197, 253, 0.18);
  animation-duration: 16s;
}

.glass-btn {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 18px rgba(147, 197, 253, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  letter-spacing: 0;
}

.glass-btn:hover {
  transform: translateY(-2px) scale(1.015);
  border-color: rgba(255, 255, 255, 0.26);
  background: rgba(255, 255, 255, 0.11);
  box-shadow: 0 0 24px rgba(147, 197, 253, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.thought-fragments {
  position: absolute;
  inset: 0;
  z-index: 5;
  pointer-events: none;
}

.landing-particles {
  position: absolute;
  inset: 0;
  z-index: 4;
  pointer-events: none;
}

.landing-particle {
  position: absolute;
  bottom: -8%;
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: rgba(191, 219, 254, 0.42);
  box-shadow: 0 0 16px rgba(125, 211, 252, 0.34);
  animation: particle-rise linear infinite;
}

.landing-particle:nth-child(1) { left: 9%; animation-duration: 18s; animation-delay: -3s; }
.landing-particle:nth-child(2) { left: 18%; animation-duration: 22s; animation-delay: -10s; }
.landing-particle:nth-child(3) { left: 27%; animation-duration: 20s; animation-delay: -7s; }
.landing-particle:nth-child(4) { left: 35%; animation-duration: 24s; animation-delay: -12s; }
.landing-particle:nth-child(5) { left: 42%; animation-duration: 17s; animation-delay: -5s; }
.landing-particle:nth-child(6) { left: 49%; animation-duration: 21s; animation-delay: -13s; }
.landing-particle:nth-child(7) { left: 56%; animation-duration: 19s; animation-delay: -8s; }
.landing-particle:nth-child(8) { left: 63%; animation-duration: 23s; animation-delay: -4s; }
.landing-particle:nth-child(9) { left: 70%; animation-duration: 18s; animation-delay: -14s; }
.landing-particle:nth-child(10) { left: 77%; animation-duration: 22s; animation-delay: -9s; }
.landing-particle:nth-child(11) { left: 83%; animation-duration: 20s; animation-delay: -6s; }
.landing-particle:nth-child(12) { left: 88%; animation-duration: 25s; animation-delay: -15s; }
.landing-particle:nth-child(13) { left: 14%; animation-duration: 21s; animation-delay: -11s; }
.landing-particle:nth-child(14) { left: 92%; animation-duration: 19s; animation-delay: -2s; }

.fragment {
  position: absolute;
  max-width: 17rem;
  color: rgba(226, 232, 240, 0.3);
  font-family: 'Source Han Sans SC', 'Noto Sans CJK SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 0.875rem;
  line-height: 1.7;
  letter-spacing: 0;
  text-align: left;
  animation: fragment-float ease-in-out infinite alternate;
  text-shadow: 0 0 14px rgba(148, 197, 253, 0.1);
}

.fragment-left-1 { left: 7%; top: 18%; animation-duration: 20s; animation-delay: -2s; opacity: 0.28; }
.fragment-left-2 { left: 12%; top: 40%; animation-duration: 24s; animation-delay: -9s; opacity: 0.32; }
.fragment-left-3 { left: 6%; top: 62%; animation-duration: 22s; animation-delay: -5s; opacity: 0.24; }
.fragment-left-4 { left: 13%; top: 80%; animation-duration: 26s; animation-delay: -13s; opacity: 0.3; }
.fragment-right-1 { right: 8%; top: 19%; animation-duration: 23s; animation-delay: -6s; opacity: 0.3; }
.fragment-right-2 { right: 12%; top: 42%; animation-duration: 21s; animation-delay: -3s; opacity: 0.26; }
.fragment-right-3 { right: 6%; top: 63%; animation-duration: 25s; animation-delay: -11s; opacity: 0.32; }
.fragment-right-4 { right: 13%; top: 81%; animation-duration: 22s; animation-delay: -8s; opacity: 0.24; }

@keyframes fragment-float {
  from {
    transform: translate3d(0, 0, 0);
  }

  to {
    transform: translate3d(10px, -8px, 0);
  }
}

@keyframes trail-drift {
  from {
    opacity: 0.46;
    translate: 0 0;
  }

  to {
    opacity: 0.76;
    translate: 24px -14px;
  }
}

@keyframes particle-rise {
  0% {
    opacity: 0;
    transform: translate3d(0, 0, 0) scale(0.8);
  }

  18% {
    opacity: 0.28;
  }

  78% {
    opacity: 0.18;
  }

  100% {
    opacity: 0;
    transform: translate3d(16px, -112vh, 0) scale(1);
  }
}

@media (max-width: 900px) {
  .fragment {
    opacity: 0.45;
    transform: scale(0.9);
  }

  .fragment-left-1,
  .fragment-left-2,
  .fragment-left-3 {
    left: 6%;
  }

  .fragment-right-1,
  .fragment-right-2,
  .fragment-right-3 {
    right: 6%;
  }
}
</style>
