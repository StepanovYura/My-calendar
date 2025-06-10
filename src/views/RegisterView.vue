<template>
  <div class="auth-page">
    <img src="" id="image-logo" alt="logo">
    <h2>Регистрация</h2>
    <div class="main-field">
      <form id="main" @submit.prevent="handleRegister">
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
            v-model="form.username" 
            type="text" 
            placeholder="USERNAME"
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

        <div class="form-group">
          <input 
            v-model="form.confirmPassword" 
            type="showConfirmPassword ? 'text' : 'password'" 
            placeholder="CONFIRM PASSWORD"
            class="password-input"
            required
          >
          <span class="toggle-icon" @click="showConfirmPassword = !showConfirmPassword">
            <i :class="showConfirmPassword ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
          </span>
        </div>

        <button type="submit" id="auth-btn">Зарегистрироваться</button>
      </form>
    </div>
    <span>Уже зарегистрированы? <a href="/login">Войти</a></span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = ref({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

async function handleRegister() {
  if (form.value.password !== form.value.confirmPassword) {
    alert('Пароли не совпадают!')
    return
  }
  
  const success = await authStore.register({
    email: form.value.email,
    name: form.value.username,
    password: form.value.password
  })
  
  if (success) {
    router.push('/login')
  } else {
    alert(authStore.error || 'Ошибка регистрации')
  }
}
</script>

<style scoped>
/* Стили такие же как в AuthPage.vue */
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