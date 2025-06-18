<template>
    <TheHeader />
    <router-view />
</template>


<script setup>
import { useAuthStore } from './stores/authStore'
import TheHeader from './components/TheHeader.vue'

const auth = useAuthStore()

function logout() {
  auth.logout()
}
</script>

<style>
body {
  margin: 0;
  font-family: sans-serif;
  background: #f7f7f7;
}

.header {
  background: #2c3e50;
  color: white;
  padding: 1rem;
}

.nav {
  margin-top: 0.5rem;
}

.nav a {
  margin-right: 10px;
  color: #ecf0f1;
  text-decoration: none;
}

.nav a.router-link-active {
  font-weight: bold;
}

button {
  background: #e74c3c;
  border: none;
  color: white;
  padding: 5px 10px;
  cursor: pointer;
}

main {
  margin-top: 2rem;
}
</style>
