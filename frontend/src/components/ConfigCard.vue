<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const config     = ref({ sa_configured: false, project_id: '' })
const saFile     = ref(null)
const uploading  = ref(false)
const snackbar   = ref({ show: false, message: '', color: 'success' })

onMounted(async () => {
  try {
    config.value = await api.getConfig()
  } catch (e) {
    showSnackbar(e.message, 'error')
  }
})

async function uploadSA() {
  if (!saFile.value) return
  uploading.value = true
  try {
    const form = new FormData()
    form.append('config_file', saFile.value)
    const res = await api.uploadSA(form)
    showSnackbar(res.message)
    saFile.value = null
    config.value = await api.getConfig()
  } catch (e) {
    showSnackbar(e.message, 'error')
  } finally {
    uploading.value = false
  }
}

function showSnackbar(message, color = 'success') {
  snackbar.value = { show: true, message, color }
}
</script>

<template>
  <v-card class="mb-4">
    <v-card-title>
      <v-icon start>mdi-firebase</v-icon>
      Firebase Config
    </v-card-title>
    <v-card-text>
      <v-chip
        :color="config.sa_configured ? 'success' : 'warning'"
        prepend-icon="config.sa_configured ? 'mdi-check-circle' : 'mdi-alert-circle'"
        class="mb-3"
      >
        {{ config.sa_configured ? 'Service Account Configured' : 'No Service Account' }}
      </v-chip>

      <div v-if="config.project_id" class="text-body-2 text-medium-emphasis mb-4">
        Project ID: <strong>{{ config.project_id }}</strong>
      </div>

      <v-file-input
        v-model="saFile"
        label="Service Account JSON"
        accept=".json"
        prepend-icon="mdi-upload"
        variant="outlined"
        density="compact"
        hide-details
      />
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn
        color="primary"
        variant="flat"
        :loading="uploading"
        :disabled="!saFile"
        @click="uploadSA"
      >Upload</v-btn>
    </v-card-actions>
  </v-card>

  <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
    {{ snackbar.message }}
  </v-snackbar>
</template>
