<script setup>
import { ref, watch } from 'vue'
import { api } from '../api'

const props = defineProps({
  modelValue: Boolean,
  username: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'error'])

const devices    = ref([])
const loading    = ref(false)
const removingId = ref('')

async function loadDevices() {
  if (!props.username) return
  loading.value = true
  try {
    devices.value = await api.getUserDevices(props.username)
  } catch (e) {
    emit('error', e.message)
  } finally {
    loading.value = false
  }
}

watch(() => props.modelValue, (open) => {
  if (open) loadDevices()
})

async function removeDevice(device) {
  if (!confirm(`Remove device "${device.device_id}" for user ${props.username}?`)) return
  removingId.value = device.device_id
  try {
    await api.removeDevice(props.username, device.device_id)
    devices.value = devices.value.filter(d => d.device_id !== device.device_id)
  } catch (e) {
    emit('error', e.message)
  } finally {
    removingId.value = ''
  }
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    max-width="500"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon start>mdi-cellphone-link</v-icon>
        Devices for {{ username }}
      </v-card-title>
      <v-card-text>
        <div v-if="loading" class="d-flex justify-center pa-4">
          <v-progress-circular indeterminate color="primary" />
        </div>
        <v-list v-else-if="devices.length">
          <v-list-item v-for="device in devices" :key="device.device_id">
            <v-list-item-title>{{ device.device_id }}</v-list-item-title>
            <template #append>
              <v-chip v-if="device.fcm_registered" size="small" color="primary" class="me-1">FCM</v-chip>
              <v-chip v-if="device.web_push_registered" size="small" color="info" class="me-2">Web Push</v-chip>
              <v-btn
                icon="mdi-delete"
                variant="text"
                size="small"
                color="error"
                :loading="removingId === device.device_id"
                @click="removeDevice(device)"
              />
            </template>
          </v-list-item>
        </v-list>
        <p v-else class="text-medium-emphasis pa-2">No devices registered.</p>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="emit('update:modelValue', false)">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
