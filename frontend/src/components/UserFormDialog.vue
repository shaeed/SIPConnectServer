<script setup>
import { ref, watch, computed } from 'vue'
import { api } from '../api'

const props = defineProps({
  modelValue: Boolean,
  user: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'saved', 'error'])

const form   = ref(null)
const saving = ref(false)
const isEdit = computed(() => !!props.user)

const fields = ref({
  username: '', password: '', audio_interface: '', data_interface: '', voicemail_number: '',
})

watch(() => props.user, (u) => {
  fields.value = u
    ? { ...u, password: '' }
    : { username: '', password: '', audio_interface: '', data_interface: '', voicemail_number: '' }
}, { immediate: true })

const rules = {
  required: v => !!v || 'Required',
  minLen:   n => v => (v && v.length >= n) || `Min ${n} characters`,
  maxLen:   n => v => (!v || v.length <= n) || `Max ${n} characters`,
}

async function save() {
  const { valid } = await form.value.validate()
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await api.updateUser(props.user.username, fields.value)
      emit('saved', `User "${props.user.username}" updated.`)
    } else {
      await api.createUser(fields.value)
      emit('saved', `User "${fields.value.username}" created.`)
    }
  } catch (e) {
    emit('error', e.message)
  } finally {
    saving.value = false
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
      <v-card-title>{{ isEdit ? 'Edit User' : 'Add User' }}</v-card-title>
      <v-card-text>
        <v-form ref="form">
          <v-text-field
            v-model="fields.username"
            label="Username"
            :rules="[rules.required, rules.minLen(3), rules.maxLen(10)]"
            :disabled="isEdit"
            variant="outlined"
            class="mb-2"
          />
          <v-text-field
            v-model="fields.password"
            label="Password"
            type="password"
            :rules="[rules.required, rules.minLen(8), rules.maxLen(30)]"
            variant="outlined"
            class="mb-2"
          />
          <v-text-field
            v-model="fields.audio_interface"
            label="Audio Interface"
            placeholder="/dev/ttyUSB1"
            :rules="[rules.required]"
            variant="outlined"
            class="mb-2"
          />
          <v-text-field
            v-model="fields.data_interface"
            label="Data Interface"
            placeholder="/dev/ttyUSB2"
            :rules="[rules.required]"
            variant="outlined"
            class="mb-2"
          />
          <v-text-field
            v-model="fields.voicemail_number"
            label="Voicemail Number (optional)"
            variant="outlined"
          />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="emit('update:modelValue', false)">Cancel</v-btn>
        <v-btn color="primary" variant="flat" :loading="saving" @click="save">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
