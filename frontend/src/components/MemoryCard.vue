<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Card } from '../types/card'

const props = defineProps<{
  card: Card
}>()

const router = useRouter()

const goToDetail = () => {
  router.push(`/card/${props.card.id}`)
}
</script>

<template>
  <article
    class="interactive-card cursor-pointer rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    @click="goToDetail"
  >
    <div class="mb-3 flex items-center justify-between gap-3">
      <h2 class="text-lg font-semibold text-slate-900">{{ card.title }}</h2>
      <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
        {{ card.time_range }}
      </span>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <span
        v-for="tag in card.tags"
        :key="`${card.id}-${tag}`"
        class="rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 text-xs text-blue-700"
      >
        #{{ tag }}
      </span>
    </div>

    <p class="mb-4 text-sm leading-6 text-slate-600">{{ card.summary }}</p>

    <div class="rounded-xl bg-slate-50 p-3 text-sm leading-6 text-slate-700">
      <span class="mr-1 font-semibold text-blue-700">刘看山状态：</span>{{ card.liu_kanshan_state }}
    </div>
  </article>
</template>
