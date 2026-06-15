import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Logs from '../views/Logs.vue'
import Notifications from '../views/Notifications.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/logs', component: Logs },
  { path: '/notifications', component: Notifications },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
