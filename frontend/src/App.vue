<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <v-app>
    <v-app-bar color="primary" elevation="2">
      <v-app-bar-title>
        <v-icon start>mdi-phone-voip</v-icon>
        SIPConnect
      </v-app-bar-title>
      <v-btn variant="text" to="/" :active="route.path === '/'">Dashboard</v-btn>
      <v-btn variant="text" to="/logs" :active="route.path === '/logs'">Logs</v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-4">
      <router-view />
    </v-main>
  </v-app>
</template>
