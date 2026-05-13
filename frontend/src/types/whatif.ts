import type { Node } from './card'

export type ZhihuSearchResult = {
  title: string
  url: string
  content_type: string
  content_text: string
  author_name: string
  vote_up_count: number
}

export type NodeZhihuSearchResult = {
  node_id: string
  query: string
  results: ZhihuSearchResult[]
}

export type WhatIfScenario = {
  rewritten_title: string
  rewritten_opening: string
  divergence_note: string
  rewritten_nodes: Node[]
  rewritten_tags: string[]
  rewritten_summary: string
  rewritten_state: string
  rewritten_liu_kanshan_state: string
  zhihu_search_queries: string[]
  zhihu_search_results: ZhihuSearchResult[]
  node_search_results: NodeZhihuSearchResult[]
}
