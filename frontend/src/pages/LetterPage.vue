<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const hasAgreed = ref(true)
const showLoginModal = ref(false)
</script>

<template>
  <main class="letter-page relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10 text-white">
    <div class="letter-overlay" aria-hidden="true" />
    <div class="letter-trails" aria-hidden="true">
      <span class="trail trail-1" />
      <span class="trail trail-2" />
    </div>
    <div class="letter-particles" aria-hidden="true">
      <span v-for="index in 14" :key="index" class="particle" />
    </div>

    <section class="letter-card relative z-10 w-full max-w-[720px] rounded-3xl px-6 py-8 sm:px-10 sm:py-10">
      <p class="text-xs font-medium tracking-wide text-slate-300/55">What If · 看山宇宙</p>
      <h1 class="mt-4 text-3xl font-semibold tracking-normal text-white sm:text-4xl">给用户的一封信</h1>

      <div class="mt-8 space-y-5 text-sm leading-8 text-slate-200/78 sm:text-base">
        <p>你好，即将进入看山宇宙的人...</p>
        <p>你或许未曾留意——<br />在知乎的某一次深夜搜索、一次不经意的点亮、一篇读了又读的回答里，<br />有什么东西，已经悄悄起了涟漪。</p>
        <p>也许是一个念头，<br />也许是一段日子的回忆，<br />也许是——你对自己这一生的另一种想象。</p>
        <p>在这里，在看山宇宙，<br />我们把这些被你影响过的痕迹，<br />叫做“星尘”。<br />每一片，都是一段真实的演变。</p>
        <p>接下来，你可以重新回望他们，<br />甚至可以让时光倒流，<br />停在某一个人生节点，<br />轻声问一句：<br />What If？</p>
        <p>本产品当前为概念体验 Demo。</p>
        <p>游客模式下，<br />您将进入基于开发者团队贡献的个人数据构建的平行宇宙示例空间。</p>
      </div>

      <label class="mt-8 flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm leading-7 text-slate-200/72">
        <input
          v-model="hasAgreed"
          type="checkbox"
          class="mt-1 h-4 w-4 rounded border-white/20 bg-white/10 text-blue-300"
        />
        <span>
          我已阅读并同意：<br />
          为了生成属于你的认知宇宙，系统可能会基于知乎中的部分行为痕迹，包括：
          <ul class="mt-3 space-y-1 pl-5 text-slate-200/64">
            <li>浏览与停留过的问题</li>
            <li>搜索兴趣变化</li>
            <li>点赞与收藏倾向</li>
            <li>一段时间内关注的话题轨迹</li>
          </ul>
          <span class="mt-3 block">
            这些内容仅用于生成认知切片与平行宇宙体验，不会公开展示你的原始记录。
          </span>
        </span>
      </label>

      <div class="mt-8 flex flex-col gap-3 sm:flex-row">
        <RouterLink
          to="/home"
          :class="[
            'primary-entry inline-flex flex-1 items-center justify-center rounded-2xl px-5 py-3 text-sm font-medium text-white transition',
            hasAgreed ? '' : 'pointer-events-none opacity-45',
          ]"
        >
          游客进入
        </RouterLink>
        <button
          class="secondary-entry inline-flex flex-1 items-center justify-center rounded-2xl px-5 py-3 text-sm font-medium text-slate-200/78 transition"
          type="button"
          @click="showLoginModal = true"
        >
          知乎账号登录
        </button>
      </div>
    </section>

    <div v-if="showLoginModal" class="modal-layer fixed inset-0 z-50 flex items-center justify-center px-4">
      <button class="absolute inset-0 cursor-default bg-slate-950/62 backdrop-blur-sm" type="button" @click="showLoginModal = false" />
      <section class="modal-card relative w-full max-w-md rounded-3xl p-7 text-slate-100">
        <p class="text-xs font-medium tracking-wide text-slate-300/55">Zhihu Account</p>
        <h2 class="mt-3 text-xl font-semibold text-white">知乎账号登录暂未开放</h2>
        <p class="mt-5 text-sm leading-7 text-slate-200/72">
          当前版本仍处于概念体验 Demo 阶段。为了避免授权链路影响体验，请先通过游客模式进入看山宇宙。
        </p>
        <button class="primary-entry mt-7 w-full rounded-2xl px-5 py-3 text-sm font-medium text-white" type="button" @click="showLoginModal = false">
          我知道了
        </button>
      </section>
    </div>
  </main>
</template>

<style scoped>
.letter-page {
  background-image: url('/images/landing-bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', 'HarmonyOS Sans', sans-serif;
}

.letter-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 38%, rgba(59, 130, 246, 0.14), rgba(2, 6, 23, 0.52) 56%, rgba(2, 6, 23, 0.82) 100%),
    linear-gradient(135deg, rgba(37, 99, 235, 0.16), rgba(168, 85, 247, 0.1) 45%, rgba(34, 211, 238, 0.06)),
    rgba(2, 6, 23, 0.58);
}

.letter-card,
.modal-card {
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(15, 23, 42, 0.58);
  box-shadow: 0 0 34px rgba(96, 165, 250, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(18px);
  animation: card-in 0.7s ease both;
}

.primary-entry {
  border: 1px solid rgba(191, 219, 254, 0.2);
  background: rgba(255, 255, 255, 0.09);
  box-shadow: 0 0 22px rgba(147, 197, 253, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
}

.primary-entry:hover {
  transform: translateY(-2px);
  border-color: rgba(191, 219, 254, 0.3);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 28px rgba(147, 197, 253, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.secondary-entry {
  border: 1px solid rgba(255, 255, 255, 0.11);
  background: rgba(255, 255, 255, 0.045);
  backdrop-filter: blur(10px);
}

.secondary-entry:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.07);
}

.letter-trails {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  opacity: 0.56;
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
  top: 31%;
  width: 64%;
  transform: rotate(-13deg);
  background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.42), rgba(168, 85, 247, 0.22), transparent);
  animation-duration: 18s;
}

.trail-2 {
  left: 25%;
  top: 67%;
  width: 48%;
  transform: rotate(16deg);
  background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.26), rgba(147, 197, 253, 0.24), transparent);
  animation-duration: 22s;
}

.letter-particles {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
}

.particle {
  position: absolute;
  bottom: -8%;
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background: rgba(191, 219, 254, 0.28);
  box-shadow: 0 0 12px rgba(125, 211, 252, 0.22);
  animation: particle-rise linear infinite;
}

.particle:nth-child(1) { left: 8%; animation-duration: 18s; animation-delay: -3s; }
.particle:nth-child(2) { left: 16%; animation-duration: 22s; animation-delay: -10s; }
.particle:nth-child(3) { left: 25%; animation-duration: 20s; animation-delay: -7s; }
.particle:nth-child(4) { left: 34%; animation-duration: 24s; animation-delay: -12s; }
.particle:nth-child(5) { left: 43%; animation-duration: 17s; animation-delay: -5s; }
.particle:nth-child(6) { left: 51%; animation-duration: 21s; animation-delay: -13s; }
.particle:nth-child(7) { left: 59%; animation-duration: 19s; animation-delay: -8s; }
.particle:nth-child(8) { left: 66%; animation-duration: 23s; animation-delay: -4s; }
.particle:nth-child(9) { left: 73%; animation-duration: 18s; animation-delay: -14s; }
.particle:nth-child(10) { left: 80%; animation-duration: 22s; animation-delay: -9s; }
.particle:nth-child(11) { left: 87%; animation-duration: 20s; animation-delay: -6s; }
.particle:nth-child(12) { left: 92%; animation-duration: 25s; animation-delay: -15s; }
.particle:nth-child(13) { left: 12%; animation-duration: 21s; animation-delay: -11s; }
.particle:nth-child(14) { left: 96%; animation-duration: 19s; animation-delay: -2s; }

@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes trail-drift {
  from {
    opacity: 0.42;
    translate: 0 0;
  }

  to {
    opacity: 0.68;
    translate: 20px -12px;
  }
}

@keyframes particle-rise {
  0% {
    opacity: 0;
    transform: translate3d(0, 0, 0) scale(0.8);
  }

  18% {
    opacity: 0.22;
  }

  78% {
    opacity: 0.14;
  }

  100% {
    opacity: 0;
    transform: translate3d(14px, -112vh, 0) scale(1);
  }
}
</style>
