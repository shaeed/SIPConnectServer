<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import UserFormDialog from './UserFormDialog.vue'

const users          = ref([])
const loading        = ref(true)
const formDialog     = ref(false)
const deleteDialog   = ref(false)
const editingUser    = ref(null)
const deletingUser   = ref('')
const snackbar       = ref({ show: false, message: '', color: 'success' })

const headers = [
  { title: 'Username',        key: 'username' },
  { title: 'Audio Interface', key: 'audio_interface' },
  { title: 'Data Interface',  key: 'data_interface' },
  { title: 'Voicemail',       key: 'voicemail_number' },
  { title: 'Actions',         key: 'actions', sortable: false, align: 'end' },
]

async function loadUsers() {
  loading.value = true
  try {
    users.value = await api.getUsers()
  } catch (e) {
    showSnackbar(e.message, 'error')
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editingUser.value = null
  formDialog.value = true
}

function openEdit(user) {
  editingUser.value = { ...user }
  formDialog.value = true
}

function confirmDelete(username) {
  deletingUser.value = username
  deleteDialog.value = true
}

async function deleteUser() {
  try {
    await api.deleteUser(deletingUser.value)
    showSnackbar(`User "${deletingUser.value}" deleted.`)
    await loadUsers()
  } catch (e) {
    showSnackbar(e.message, 'error')
  } finally {
    deleteDialog.value = false
  }
}

function onSaved(message) {
  formDialog.value = false
  showSnackbar(message)
  loadUsers()
}

function showSnackbar(message, color = 'success') {
  snackbar.value = { show: true, message, color }
}

onMounted(loadUsers)
</script>

<template>
  <v-card>
    <v-card-title class="d-flex align-center pa-4">
      <v-icon start>mdi-account-group</v-icon>
      SIP Users
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">Add User</v-btn>
    </v-card-title>

    <v-data-table
      :headers="headers"
      :items="users"
      :loading="loading"
      :items-per-page="10"
    >
      <template #item.actions="{ item }">
        <v-btn icon="mdi-pencil" variant="text" size="small" @click="openEdit(item)" />
        <v-btn icon="mdi-delete" variant="text" size="small" color="error" @click="confirmDelete(item.username)" />
      </template>
    </v-data-table>
  </v-card>

  <UserFormDialog
    v-model="formDialog"
    :user="editingUser"
    @saved="onSaved"
    @error="showSnackbar($event, 'error')"
  />

  <v-dialog v-model="deleteDialog" max-width="420">
    <v-card>
      <v-card-title>Delete User</v-card-title>
      <v-card-text>
        Delete user <strong>{{ deletingUser }}</strong>? This will also remove their Asterisk config.
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
        <v-btn color="error" variant="flat" @click="deleteUser">Delete</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
    {{ snackbar.message }}
  </v-snackbar>
</template>
