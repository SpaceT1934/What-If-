import mockCards from './mockCards'
import exploreCards from './exploreCards'
import type { Card } from '../types/card'

const STORAGE_KEY = 'what-if-universe:guest-stardust'
const SHARED_SQUARE_KEY = 'what-if-universe:shared-square-stardust'

const isBrowser = () => typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
const withDefaultKanshanImage = (card: Card): Card => ({
  ...card,
  liu_kanshan_image: card.liu_kanshan_image || '/images/liukanshan/confusion.png',
})

export const getGuestStardust = (): Card[] => {
  if (!isBrowser()) return []
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.map(withDefaultKanshanImage) : []
  } catch {
    return []
  }
}

export const saveGuestStardust = (card: Card) => {
  if (!isBrowser()) return
  const existing = getGuestStardust().filter((item) => item.id !== card.id)
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify([card, ...existing]))
  window.dispatchEvent(new CustomEvent('guest-stardust-updated'))
}

export const getSharedSquareStardust = (): Card[] => {
  if (!isBrowser()) return []
  try {
    const raw = window.localStorage.getItem(SHARED_SQUARE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.map(withDefaultKanshanImage) : []
  } catch {
    return []
  }
}

export const saveSharedSquareStardust = (card: Card) => {
  if (!isBrowser()) return
  const sharedCard: Card = {
    ...card,
    id: `shared-square-${card.id}`,
    source_type: 'shared',
    source_label: '已暂存到看山宇宙广场',
  }
  const existing = getSharedSquareStardust().filter((item) => item.id !== sharedCard.id)
  window.localStorage.setItem(SHARED_SQUARE_KEY, JSON.stringify([sharedCard, ...existing]))
  window.dispatchEvent(new CustomEvent('shared-square-stardust-updated'))
}

export const isSharedToSquare = (cardId: string): boolean => {
  return getSharedSquareStardust().some((item) => item.id === `shared-square-${cardId}`)
}

export const getUniverseCards = (): Card[] => {
  return [...getGuestStardust(), ...mockCards]
}

export const getMainUniverseCards = (): Card[] => {
  return getUniverseCards().filter((item) => item.source_type !== 'parallel')
}

export const getParallelStardustByParent = (parentId: string): Card[] => {
  return getGuestStardust().filter((item) => item.source_type === 'parallel' && item.parent_id === parentId)
}

export const findUniverseCard = (id: string): Card | undefined => {
  return [...getUniverseCards(), ...getSharedSquareStardust(), ...exploreCards].find((item) => item.id === id)
}
