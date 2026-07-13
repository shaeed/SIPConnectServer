<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const callLogs = ref([])
const loading  = ref(true)
const error    = ref('')

const callHeaders = [
  { title: 'ID',        key: 'id',        width: '80px' },
  { title: 'User',      key: 'user' },
  { title: 'Number',    key: 'number' },
  { title: 'Timestamp', key: 'timestamp' },
]

onMounted(async () => {
  try {
    callLogs.value = (await api.getCallLogs()).data
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <v-container fluid class="pa-2 pa-sm-6">
    <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>

    <v-card>
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
        :mobile-breakpoint="600"
      />
    </v-card>
  </v-container>
</template>
