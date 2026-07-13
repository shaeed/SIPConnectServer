import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import CallLogs from '../views/CallLogs.vue'
import SmsLogs from '../views/SmsLogs.vue'
import Notifications from '../views/Notifications.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/logs/calls', component: CallLogs },
  { path: '/logs/sms', component: SmsLogs },
  { path: '/notifications', component: Notifications },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
