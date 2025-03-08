import { createRouter, createWebHistory } from 'vue-router'
import IndexView from '@/views/IndexView.vue'
import AdminView from '@/views/MusicManageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: AdminView,
    },
    {
      path: '/add',
      name: 'add',
      component: () => import('../views/VideoManageView.vue'),
    },
  ],
})

export default router
