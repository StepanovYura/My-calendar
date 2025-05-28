<template>
  <div class="auth-page">
    <img src="" id="image-logo" alt="logo">
    <h2>Авторизация</h2>
    <div class="main-field">
      <form id="main" @submit.prevent="handleLogin">
        <div class="form-group">
        <input 
          v-model="form.email" 
          type="text" 
          placeholder="EMAIL ADDRESS"
          class="email-input"
          required
        >
      </div>

      <div class="form-group">
        <input 
          v-model="form.password" 
          type="showPassword ? 'text' : 'password'" 
          placeholder="PASSWORD"
          class="password-input"
          required
        >
        <span class="toggle-icon" @click="showPassword = !showPassword">
          <i :class="showPassword ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
        </span>
      </div>

      <button type="submit" id="auth-btn">Войти</button>
      </form>
    </div>
    <RouterLink to="/changePswd">Забыли пароль?</RouterLink><!--ДОБАВИТЬ СТРАНИЦУ С ИЗМЕНЕНИЕМ ПАРОЛЯ ПОЛЬЗОВАТЕЛЯ-->
    <span>Ещё не регистрировались? <RouterLink to="/register">Зарегистрироваться</RouterLink></span><!--ДОБАВИТЬ СТРАНИЦУ С РЕГИСТРАЦИЕЙ ПОЛЬЗОВАТЕЛЯ(сделать копию этой, но чуть изменить)-->
  </div>
</template>


<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const auth = useAuthStore()
const showPassword = ref(false)

const form = ref({
  email: '',
  password: ''
})

function handleLogin() {
  auth.login({ 
    email: form.value.email, 
    password: form.value.password 
  })
  router.push('/')
}
</script>

<style scoped>
.auth-page {
  font-family: "Arial", sans-serif;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;

  background-color: white;
  color: #333;
  margin-top: 90px;
}

.main-field {
  width: 40%;
}

#main {
  display: grid;
  gap: 1rem;
}

.password-input-wrapper {
  position: relative;
  width: 100%;
}

.email-input {
  padding: 8px 35px 8px 10px;
  width: -webkit-fill-available;
}

.password-input {
  padding: 8px 35px 8px 10px;
  width: -webkit-fill-available;
}

.toggle-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666;
}

#auth-btn {
  align-items: center;
  background-color: #333;
  width: 100%;
  margin-bottom: 20px;
}
</style>