<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const callLogs = ref([])
const smsLogs  = ref([])
const loading  = ref(true)
const error    = ref('')

const callHeaders = [
  { title: 'ID',        key: 'id',        width: '80px' },
  { title: 'User',      key: 'user' },
  { title: 'Number',    key: 'number' },
  { title: 'Timestamp', key: 'timestamp' },
]

const smsHeaders = [
  { title: 'ID',        key: 'id',        width: '80px' },
  { title: 'User',      key: 'user' },
  { title: 'Number',    key: 'number' },
  { title: 'Message',   key: 'message' },
  { title: 'Type',      key: 'sms_type' },
  { title: 'Timestamp', key: 'timestamp' },
]

onMounted(async () => {
  try {
    const [callData, smsData] = await Promise.all([api.getCallLogs(), api.getSmsLogs()])
    callLogs.value = callData.data
    smsLogs.value  = smsData.data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <v-container fluid class="pa-6">
    <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>

    <v-card class="mb-6">
      <v-card-title>
        <v-icon start>mdi-phone</v-icon>
        Call Logs
      </v-card-title>
      <v-data-table
        :headers="callHeaders"
        :items="callLogs"
        :loading="loading"
        :items-per-page="20"
        :sort-by="[{ key: 'timestamp', order: 'desc' }]"
      />
    </v-card>

    <v-card>
      <v-card-title>
        <v-icon start>mdi-message-text</v-icon>
        SMS Logs
      </v-card-title>
      <v-data-table
        :headers="smsHeaders"
        :items="smsLogs"
        :loading="loading"
        :items-per-page="20"
        :sort-by="[{ key: 'timestamp', order: 'desc' }]"
      />
    </v-card>
  </v-container>
</template>
