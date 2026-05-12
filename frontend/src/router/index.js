import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Logs from '../views/Logs.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/logs', component: Logs },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
