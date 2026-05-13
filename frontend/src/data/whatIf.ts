import type { Card } from '../types/card'
import type { WhatIfScenario } from '../types/whatif'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export const generateWhatIf = async (card: Card, rewrittenOpening: string): Promise<WhatIfScenario> => {
  const response = await fetch(`${API_BASE}/api/guest/what-if`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      card_title: card.title,
      time_range: card.time_range,
      tags: card.tags,
      summary: card.summary,
      liu_kanshan_state: card.liu_kanshan_state,
      original_nodes: card.nodes,
      rewritten_opening: rewrittenOpening,
    }),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message)
  }

  return response.json()
}
