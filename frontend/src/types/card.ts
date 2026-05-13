export type Node = {
  id: string
  title: string
  description: string
  emotion: string
  reading_links?: string[]
}

export type Card = {
  id: string
  title: string
  time_range: string
  tags: string[]
  nodes: Node[]
  summary: string
  liu_kanshan_state: string
  source_type?: 'mock' | 'guest' | 'parallel' | 'shared'
  parent_id?: string
  source_label?: string
}
