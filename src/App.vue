<template>
    <TheHeader />
    <!-- <header class="header">
      <h1>🗓 Умный календарь</h1>
      <nav class="nav">
        <router-link to="/">🏠 Главная</router-link>
        <router-link to="/social">👥 Друзья и группы</router-link>
        <router-link to="/match">🧩 Совпадения</router-link>
        <router-link to="/profile">🙍‍♂️ Профиль</router-link>
        <router-link v-if="auth.isAdmin" to="/admin">🔧 Админка</router-link>
        <router-link to="/login">🔐 Вход</router-link>
        <button v-if="auth.isAuthenticated" @click="logout">🚪 Выйти</button>
      </nav>
      <p v-if="auth.isAuthenticated">Вы вошли как <strong>{{ auth.user.name }}</strong> ({{ auth.user.role }})</p>
    </header> -->
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
