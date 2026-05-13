import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../pages/LandingPage.vue'
import LetterPage from '../pages/LetterPage.vue'
import HomePage from '../pages/HomePage.vue'
import CreateSlicePage from '../pages/CreateSlicePage.vue'
import ExplorePage from '../pages/ExplorePage.vue'
import CardDetailPage from '../pages/CardDetailPage.vue'
import ComparePage from '../pages/ComparePage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/landing' },
    { path: '/landing', name: 'landing', component: LandingPage },
    { path: '/letter', name: 'letter', component: LetterPage },
    { path: '/home', name: 'home', component: HomePage },
    { path: '/create-slice', name: 'create-slice', component: CreateSlicePage },
    { path: '/explore', name: 'explore', component: ExplorePage },
    { path: '/card/:id', name: 'card-detail', component: CardDetailPage },
    { path: '/compare/:id', name: 'compare', component: ComparePage },
  ],
})

export default router
