<template>
  <div>
    <h2>Авторизация</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Имя" />
      <select v-model="role">
        <option value="user">Пользователь</option>
        <option value="admin">Админ</option>
      </select>
      <button type="submit">Войти</button>
    </form>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { ref } from 'vue'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const role = ref('user')

function handleLogin() {
  auth.login({ name: username.value, role: role.value })
  router.push('/')
}
</script>
