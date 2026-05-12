<script setup>
import UserTable from '../components/UserTable.vue'
import ConfigCard from '../components/ConfigCard.vue'
</script>

<template>
  <v-container fluid class="pa-2 pa-sm-6">
    <v-row>
      <v-col cols="12" lg="8">
        <UserTable />
      </v-col>
      <v-col cols="12" lg="4">
        <ConfigCard />
      </v-col>
    </v-row>
  </v-container>
</template>
