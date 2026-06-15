<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const username    = ref(localStorage.getItem('notif_username') || '')
const supported   = ref('serviceWorker' in navigator && 'PushManager' in window)
const subscribed  = ref(false)
const loading     = ref(false)
const snackbar    = ref({ show: false, message: '', color: 'success' })

function showSnackbar(message, color = 'success') {
  snackbar.value = { show: true, message, color }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)))
}

function getDeviceId() {
  let deviceId = localStorage.getItem('notif_device_id')
  if (!deviceId) {
    deviceId = crypto.randomUUID()
    localStorage.setItem('notif_device_id', deviceId)
  }
  return deviceId
}

onMounted(async () => {
  if (!supported.value) return
  const registration = await navigator.serviceWorker.register('/sw.js')
  const subscription = await registration.pushManager.getSubscription()
  subscribed.value = !!subscription
})

async function enableNotifications() {
  if (!username.value) {
    showSnackbar('Please enter a username.', 'error')
    return
  }
  localStorage.setItem('notif_username', username.value)
  loading.value = true
  try {
    const permission = await Notification.requestPermission()
    if (permission !== 'granted') {
      showSnackbar('Notification permission denied.', 'error')
      return
    }

    const registration = await navigator.serviceWorker.register('/sw.js')
    let subscription = await registration.pushManager.getSubscription()
    if (!subscription) {
      const { public_key } = await api.getVapidPublicKey()
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(public_key),
      })
    }

    await api.registerWebPush({
      username: username.value,
      device_id: getDeviceId(),
      subscription: subscription.toJSON(),
    })

    subscribed.value = true
    showSnackbar('Browser notifications enabled.')
  } catch (e) {
    showSnackbar(e.message, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container fluid class="pa-2 pa-sm-6">
    <v-card class="mb-4">
      <v-card-title>
        <v-icon start>mdi-bell-ring</v-icon>
        Browser Notifications
      </v-card-title>
      <v-card-text>
        <v-alert v-if="!supported" type="warning" class="mb-4">
          This browser does not support push notifications.
        </v-alert>

        <v-chip v-if="supported" :color="subscribed ? 'success' : 'warning'" class="mb-3">
          {{ subscribed ? 'Notifications Enabled' : 'Notifications Not Enabled' }}
        </v-chip>

        <p class="text-body-2 text-medium-emphasis mb-4">
          Enter your SIP username to receive call and SMS alerts as browser notifications
          on this device.
        </p>

        <v-text-field
          v-model="username"
          label="SIP Username"
          variant="outlined"
          density="compact"
          :disabled="!supported"
          hide-details
          class="mb-4"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="primary"
          variant="flat"
          :loading="loading"
          :disabled="!supported"
          @click="enableNotifications"
        >Enable Browser Notifications</v-btn>
      </v-card-actions>
    </v-card>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>
