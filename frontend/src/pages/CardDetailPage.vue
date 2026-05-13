<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { findUniverseCard, isSharedToSquare, saveSharedSquareStardust } from '../data/guestStardust'
import KanshanGuide from '../components/KanshanGuide.vue'

const route = useRoute()
const showShareModal = ref(false)
const shared = ref(false)

const card = computed(() => {
  const id = String(route.params.id)
  return findUniverseCard(id)
})

watch(
  card,
  (current) => {
    shared.value = current ? isSharedToSquare(current.id.replace(/^shared-square-/, '')) || current.source_type === 'shared' : false
  },
  { immediate: true },
)

const openShareModal = () => {
  if (!card.value) return
  showShareModal.value = true
}

const confirmShare = () => {
  if (!card.value) return
  const sourceCard = {
    ...card.value,
    id: card.value.id.replace(/^shared-square-/, ''),
  }
  saveSharedSquareStardust(sourceCard)
  shared.value = true
  showShareModal.value = false
}
</script>

<template>
  <main class="detail-bg min-h-screen text-slate-100">
    <div class="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <RouterLink to="/home" class="text-sm font-medium text-blue-300 hover:text-blue-200">← 返回首页</RouterLink>

      <section v-if="card" class="glass-card mt-5 rounded-2xl p-6 sm:p-7">
        <header class="border-b border-slate-700/70 pb-5">
          <h1 class="text-2xl font-bold text-white sm:text-3xl">{{ card.title }}</h1>
          <p class="mt-2 text-sm text-slate-300">{{ card.time_range }}</p>
          <div class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="tag in card.tags"
              :key="`${card.id}-${tag}`"
              class="glow-tag rounded-full px-2.5 py-1 text-xs"
            >
              #{{ tag }}
            </span>
          </div>
        </header>

        <section class="pt-6">
          <h2 class="text-base font-semibold text-white">Timeline 节点链</h2>
          <ol class="mt-4 space-y-6">
            <li
              v-for="(node, index) in card.nodes"
              :key="node.id"
              class="timeline-fade-in relative pl-8"
              :style="{ animationDelay: `${index * 0.08}s` }"
            >
              <span class="timeline-dot absolute left-0 top-1.5 h-3 w-3 rounded-full" />
              <span
                v-if="node.id !== card.nodes[card.nodes.length - 1].id"
                class="timeline-line absolute left-[5px] top-5 h-[calc(100%+12px)] w-px"
              />

              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <h3 class="text-sm font-semibold text-slate-100">{{ node.title }}</h3>
                  <span class="rounded-full bg-slate-800/80 px-2 py-0.5 text-xs text-slate-300">
                    {{ node.emotion }}
                  </span>
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

        <section class="mt-8 rounded-xl border border-slate-700/70 bg-slate-900/45 p-4">
          <h2 class="text-sm font-semibold text-slate-100">阶段总结</h2>
          <p class="mt-2 text-sm leading-7 text-slate-300">{{ card.summary }}</p>
          <p class="mt-3 text-sm text-slate-300">
            <span class="font-semibold text-blue-300">刘看山状态：</span>{{ card.liu_kanshan_state }}
          </p>
        </section>

        <footer class="mt-8 flex flex-wrap gap-3">
          <RouterLink
            :to="`/compare/${card.id}`"
            class="interactive-button inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            尝试 What If 改写
          </RouterLink>
          <button
            type="button"
            class="share-button inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-semibold"
            :class="shared ? 'is-shared' : ''"
            @click="openShareModal"
          >
            {{ shared ? '已暂存到宇宙广场' : '分享到宇宙广场' }}
          </button>
        </footer>
      </section>

      <section v-else class="mt-5 rounded-2xl border border-slate-700 bg-slate-900/60 p-6 text-slate-300 shadow-sm">
        未找到对应卡片。
      </section>
    </div>

    <div v-if="showShareModal && card" class="share-modal-mask" @click.self="showShareModal = false">
      <section class="share-modal">
        <p class="text-xs uppercase tracking-[0.22em] text-blue-100/55">Share To Square</p>
        <h2 class="mt-3 text-xl font-semibold text-white">将这颗星尘分享到看山宇宙广场？</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300/82">
          这次分享只会把当前星尘的标题、标签、节点链、阶段总结与刘看山状态暂存在你的浏览器里，用于在本机体验“宇宙广场”的展示效果。
        </p>
        <div class="mt-5 rounded-2xl border border-blue-200/12 bg-blue-400/[0.06] p-4">
          <p class="text-sm leading-7 text-slate-200/86">
            我已知晓：当前 Demo 不会上传你的原始浏览记录、搜索记录、点赞收藏等隐私数据；分享内容仅作为本地暂存的星尘卡片展示。
          </p>
        </div>
        <div class="mt-6 flex flex-wrap gap-3">
          <button type="button" class="share-confirm-btn" @click="confirmShare">我愿意分享</button>
          <button type="button" class="share-cancel-btn" @click="showShareModal = false">暂不分享</button>
        </div>
      </section>
    </div>
    <KanshanGuide
      :steps="[
        '这里记录了这颗星尘的节点链。',
        '向下看阶段总结，能看到内容留下的影响。',
        '想探索另一种走向，就试试 What If 改写。'
      ]"
    />
  </main>
</template>

<style scoped>
.detail-bg {
  background: radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.2), transparent 35%),
    radial-gradient(circle at 80% 30%, rgba(14, 116, 144, 0.16), transparent 40%),
    linear-gradient(160deg, #020617 0%, #0b1120 55%, #060b1a 100%);
}

.glass-card {
  border: 1px solid rgba(96, 165, 250, 0.3);
  background: rgba(15, 23, 42, 0.58);
  backdrop-filter: blur(8px);
  box-shadow: 0 0 0 1px rgba(191, 219, 254, 0.08) inset, 0 0 32px rgba(37, 99, 235, 0.14);
}

.glow-tag {
  border: 1px solid rgba(147, 197, 253, 0.35);
  background: rgba(59, 130, 246, 0.14);
  color: #bfdbfe;
  box-shadow: 0 0 10px rgba(96, 165, 250, 0.2);
}

.timeline-dot {
  background: #60a5fa;
  box-shadow: 0 0 12px rgba(96, 165, 250, 0.85);
}

.timeline-line {
  background: linear-gradient(180deg, rgba(148, 163, 184, 0.7), rgba(148, 163, 184, 0.2));
}

.share-button {
  border: 1px solid rgba(191, 219, 254, 0.18);
  background: rgba(255, 255, 255, 0.06);
  color: rgba(219, 234, 254, 0.92);
  box-shadow: 0 0 18px rgba(96, 165, 250, 0.1);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
}

.share-button:hover {
  transform: translateY(-2px);
  border-color: rgba(125, 211, 252, 0.38);
  background: rgba(14, 165, 233, 0.12);
  box-shadow: 0 0 26px rgba(96, 165, 250, 0.18);
}

.share-button.is-shared {
  border-color: rgba(52, 211, 153, 0.28);
  background: rgba(16, 185, 129, 0.1);
  color: rgba(209, 250, 229, 0.94);
}

.share-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(2, 6, 23, 0.72);
  backdrop-filter: blur(12px);
}

.share-modal {
  width: min(560px, 100%);
  border: 1px solid rgba(147, 197, 253, 0.26);
  border-radius: 28px;
  background:
    radial-gradient(circle at 20% 0%, rgba(59, 130, 246, 0.16), transparent 42%),
    rgba(8, 13, 30, 0.92);
  padding: 1.5rem;
  box-shadow: 0 24px 90px rgba(0, 0, 0, 0.56), 0 0 34px rgba(59, 130, 246, 0.16);
}

.share-confirm-btn,
.share-cancel-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  padding: 0.72rem 1.15rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, background 0.25s ease;
}

.share-confirm-btn {
  border: 1px solid rgba(125, 211, 252, 0.35);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.36), rgba(14, 165, 233, 0.2));
  color: white;
  box-shadow: 0 0 24px rgba(37, 99, 235, 0.18);
}

.share-cancel-btn {
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: rgba(226, 232, 240, 0.78);
}

.share-confirm-btn:hover,
.share-cancel-btn:hover {
  transform: translateY(-2px);
}
</style>
