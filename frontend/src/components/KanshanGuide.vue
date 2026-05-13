<script setup lang="ts">
import { computed, ref } from 'vue'

const props = withDefaults(defineProps<{
  steps: string[]
  position?: 'right' | 'left'
}>(), {
  position: 'right',
})

const currentIndex = ref(0)
const isOpen = ref(true)

const currentText = computed(() => props.steps[currentIndex.value] || '')
const hasNext = computed(() => currentIndex.value < props.steps.length - 1)
const hasPrev = computed(() => currentIndex.value > 0)

const prevStep = () => {
  if (hasPrev.value) {
    currentIndex.value -= 1
  }
}

const nextStep = () => {
  if (hasNext.value) {
    currentIndex.value += 1
  } else {
    isOpen.value = false
  }
}
</script>

<template>
  <aside
    class="kanshan-guide"
    :class="[`is-${position}`, { 'is-collapsed': !isOpen }]"
    aria-label="看山页面引导"
  >
    <button
      type="button"
      class="kanshan-avatar"
      aria-label="打开看山提示"
      @click="isOpen = !isOpen"
    >
      <img src="/images/liukanshan-main.png" alt="刘看山助手" />
    </button>

    <transition name="guide-fade">
      <div v-if="isOpen" class="guide-bubble">
        <p>{{ currentText }}</p>
        <div class="guide-actions">
          <button v-if="hasPrev" type="button" class="guide-action" @click="prevStep">上一步</button>
          <button type="button" class="guide-action is-primary" @click="nextStep">
            {{ hasNext ? '下一步' : '知道了' }}
          </button>
        </div>
      </div>
    </transition>
  </aside>
</template>

<style scoped>
.kanshan-guide {
  position: fixed;
  z-index: 70;
  right: clamp(1rem, 2.2vw, 2rem);
  bottom: clamp(1rem, 2.2vw, 2rem);
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  pointer-events: none;
}

.kanshan-guide.is-left {
  right: auto;
  left: clamp(1rem, 2.2vw, 2rem);
  flex-direction: row-reverse;
}

.kanshan-avatar,
.guide-bubble {
  pointer-events: auto;
}

.kanshan-avatar {
  width: 54px;
  height: 54px;
  overflow: hidden;
  border: 1px solid rgba(191, 219, 254, 0.28);
  border-radius: 9999px;
  background: rgba(15, 23, 42, 0.56);
  box-shadow: 0 0 22px rgba(96, 165, 250, 0.18);
  backdrop-filter: blur(12px);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.kanshan-avatar:hover {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 0 30px rgba(96, 165, 250, 0.24);
}

.kanshan-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.guide-bubble {
  width: min(230px, calc(100vw - 6.5rem));
  border: 1px solid rgba(191, 219, 254, 0.18);
  border-radius: 18px 18px 4px 18px;
  background: rgba(8, 13, 30, 0.78);
  box-shadow: 0 16px 50px rgba(0, 0, 0, 0.34), 0 0 22px rgba(59, 130, 246, 0.12);
  padding: 0.85rem;
  backdrop-filter: blur(14px);
}

.is-left .guide-bubble {
  border-radius: 18px 18px 18px 4px;
}

.guide-bubble p {
  margin: 0;
  color: rgba(226, 232, 240, 0.9);
  font-size: 0.78rem;
  line-height: 1.65;
}

.guide-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.7rem;
  margin-top: 0.6rem;
}

.guide-action {
  color: rgba(147, 197, 253, 0.95);
  font-size: 0.72rem;
  font-weight: 600;
  transition: color 0.2s ease, transform 0.2s ease;
}

.guide-action:not(.is-primary) {
  color: rgba(203, 213, 225, 0.58);
}

.guide-action:hover {
  color: white;
  transform: translateX(2px);
}

.guide-fade-enter-active,
.guide-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.guide-fade-enter-from,
.guide-fade-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.98);
}

@media (max-width: 640px) {
  .kanshan-guide {
    right: 0.8rem;
    bottom: 0.8rem;
    gap: 0.55rem;
  }

  .kanshan-avatar {
    width: 46px;
    height: 46px;
  }

  .guide-bubble {
    width: min(205px, calc(100vw - 5.2rem));
    padding: 0.72rem;
  }
}
</style>
