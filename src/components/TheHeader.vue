<template>
  <header>
    <nav class="navbar">
      <div class="logo">
        <a href="/">
          <img src="" alt="logo" />
        </a>
      </div>
      <div class="nowData"><p>{{ currentDate }}</p></div>
      <div class="search">
        <form>
          <input type="search" name="text" class="serach" placeholder="Найти дату">
          <input type="submit" name="submit" class="submit" value="Найти">
        </form>
      </div>
      <div class="nav-buttons">
        <RouterLink to="/" class="icons active" id="schedule">
          <img src="../assets/shedule-light-48.png" alt="sched">
        </RouterLink>
        <RouterLink to="/social" class="icons" id="communication">
          <img src="../assets/community-light-50.png" alt="comm">
        </RouterLink>
        <RouterLink to="/match" class="icons" id="matched">
          <img src="../assets/match-light-50.png" alt="match">
        </RouterLink>
        <RouterLink to="/messages" class="icons" id="message">
          <img src="../assets/message-light-48.png" alt="mes">
        </RouterLink>
        <RouterLink to="/profile" class="icons" id="profile">
          <img src="../assets/profile-light-48.png" alt="prof">
        </RouterLink>
      </div>
      <button class="theme" @click="toggleTheme">
        <span>Тема</span>
      </button>
    </nav>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentDate = ref('')

onMounted(() => {
  const date = new Date()
  currentDate.value = date.toLocaleDateString('ru-RU')
})

function toggleTheme() {
  // Заглушка
  alert('Смена темы пока не реализована')
}
</script>

<style scoped>
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

#add-event-button > img {
    transition: all 0.3s ease; /* Плавное изменение размера */
}

.theme {
    background-color: rgb(173, 173, 173);
    border: none;
    cursor: pointer;
}
</style>
