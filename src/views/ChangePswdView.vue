<template>
  <div class="auth-page">
    <img src="" id="image-logo" alt="logo">
    <h2>Изменение пароля</h2>
    <div class="main-field">
      <form id="main" @submit.prevent="handlePasswordChange">
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
            v-model="form.oldPassword" 
            type="showOldPassword ? 'text' : 'password'" 
            placeholder="OLD PASSWORD"
            class="password-input"
            required
          >
          <span class="toggle-icon" @click="showOldPassword = !showOldPassword">
            <i :class="showOldPassword ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
          </span>
        </div>

        <div class="form-group">
          <input 
            v-model="form.newPassword" 
            type="showNewPassword ? 'text' : 'password'" 
            placeholder="NEW PASSWORD"
            class="password-input"
            required
          >
          <span class="toggle-icon" @click="showNewPassword = !showNewPassword">
            <i :class="showNewPassword ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
          </span>
        </div>

        <div class="form-group">
          <input 
            v-model="form.confirmPassword" 
            type="showConfirmPassword ? 'text' : 'password'" 
            placeholder="CONFIRM NEW PASSWORD"
            class="password-input"
            required
          >
          <span class="toggle-icon" @click="showConfirmPassword = !showConfirmPassword">
            <i :class="showConfirmPassword ? 'fa fa-eye-slash' : 'fa fa-eye'"></i>
          </span>
        </div>

        <button type="submit" id="auth-btn">Изменить пароль</button>
      </form>
    </div>
    <span>Вернуться к <a href="/login">авторизации</a></span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const form = ref({
  email: '',
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

async function handlePasswordChange() {
  if (form.value.newPassword !== form.value.confirmPassword) {
    alert('Новые пароли не совпадают!')
    return
  }
  
  const success = await authStore.changePassword({
    email: form.value.email,
    oldPassword: form.value.oldPassword,
    newPassword: form.value.newPassword
  })
  
  if (success) {
    alert('Пароль успешно изменён')
    router.push('/login')
  } else {
    alert(authStore.error || 'Ошибка смены пароля')
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