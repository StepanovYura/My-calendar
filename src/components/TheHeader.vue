<template>
  <header>
    <nav class="navbar">
      <div class="logo">
        <a href="/" v-if="!isAdmin">
          <img src="" alt="logo" />
        </a>
      </div>
      <div class="nowData"><p>{{ currentDate }}</p></div>
      <div class="search" v-if="!isAdmin">
        <form @submit.prevent="searchByDate">
          <input 
            v-model="searchDate"
            type="date"
            name="text"
            class="search"
            :class="{active: $route.path !== '/'}"
            placeholder="Найти дату"
          >
          <input 
            type="submit"
            name="submit"
            class="submit"
            :class="{active: $route.path !== '/'}"
            value="Найти"
          >
        </form>
      </div>
      <div class="nav-buttons" v-if="!isAdmin">
        <RouterLink to="/" class="icons":class="{active: $route.path === '/'}" id="schedule">
          <img src="../assets/shedule-light-48.png" alt="sched">
        </RouterLink>
        <RouterLink to="/social" class="icons":class="{active: $route.path === '/social'}" id="communication">
          <img src="../assets/community-light-50.png" alt="comm">
        </RouterLink>
        <RouterLink to="/match" class="icons":class="{active: $route.path === '/match'}" id="matched">
          <img src="../assets/match-light-50.png" alt="match">
        </RouterLink>
        <RouterLink to="/messages" class="icons":class="{active: $route.path === '/messages'}" id="message">
          <img src="../assets/message-light-48.png" alt="mes">
        </RouterLink>
        <RouterLink to="/profile" class="icons":class="{active: $route.path === '/profile'}" id="profile">
          <img src="../assets/profile-light-48.png" alt="prof">
        </RouterLink>
      </div>
      <button class="auth-btn" @click="handleAuthClick">
        <span>{{ isAuthenticated ? 'Выйти' : 'Войти' }}</span>
      </button>
    </nav>
  </header>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const currentDate = ref('')
const router = useRouter()
const searchDate = ref('')
const authStore = useAuthStore()
const isAuthenticated = computed(() => !!authStore.token)
const isAdmin = computed(() => authStore.user?.role === 'admin')
onMounted(() => {
  const date = new Date()
  currentDate.value = date.toLocaleDateString('ru-RU')
})

function searchByDate() {
  if (!searchDate.value) return
  router.push({ path: '/', query: { date: searchDate.value } })
}

async function handleAuthClick() {
  if (isAuthenticated.value) {
    await authStore.logout()
    router.push('/login')  // После выхода отправляем на страницу входа
  } else {
    router.push('/login')  // Просто переходим на страницу входа
  }
}

</script>

<style scoped>

.auth-btn {
  background-color: rgb(173, 173, 173);
  border: none;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.navbar {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;

    padding: 0 2rem 0 2rem;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-buttons {
    display: flex;
    gap: 1rem;
}

.nav-buttons img {
    max-block-size: 30px;
    transition: all 0.3s ease; /* Плавное изменение размера */
}

#add-event-button > img:hover,
.icons > img:hover,
.icons.active > img {
    transform: scale(1.2);
    border-radius: 50%;
}

.search.active,
.submit.active {
  visibility: hidden
}

#add-event-button > img {
    transition: all 0.3s ease; /* Плавное изменение размера */
}

.theme {
    background-color: rgb(173, 173, 173);
    border: none;
    cursor: pointer;
}
</style>
