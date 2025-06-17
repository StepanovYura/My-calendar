<template>
  <div class="create-event-page">
    <h2>Создание события</h2>
    <form @submit.prevent="submitEvent">
      <label>Название:</label>
      <input v-model="form.title" type="text" required />

      <label>Описание:</label>
      <textarea v-model="form.description" rows="4" />

      <!-- <label>Дата и время:</label>
      <input v-model="form.date_time" type="datetime-local" required /> -->

      <label>Дата:</label>
      <input v-model="form.date" type="date" :disabled="initialDate != null" :required="initialDate == null" />

      <label>Время:</label>
      <input v-model="form.time" type="time" required />

      <label>Длительность (мин):</label>
      <input v-model.number="form.duration_minutes" type="number" min="1" required />
        
      <label>Никнейм друга (необязательно):</label>
      <input v-model="form.friend_username" type="text" placeholder="username" />

      <div class="buttons">
        <button type="submit">Создать</button>
        <button type="button" @click="router.back()">Назад</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventsStore } from '../stores/eventsStore'

const router = useRouter()
const route = useRoute()
const eventsStore = useEventsStore()
const initialDate = route.query.date ? new Date(route.query.date) : null

const form = ref({
  title: '',
  description: '',
  date: initialDate ? initialDate.toISOString().split('T')[0] : '', // yyyy-mm-dd
  time: initialDate ? initialDate.toTimeString().slice(0, 5) : '',    // hh:mm
  duration_minutes: 60,
  friend_username: ''
})

async function submitEvent() {
  try {
    const datetimeString = `${form.value.date}T${form.value.time}`
    const eventData = {
      ...form.value,
      date_time: datetimeString
    }
    delete eventData.date
    delete eventData.time
    await eventsStore.createEvent(eventData)
    router.back() // После создания — назад
  } catch (err) {
    alert(err.message || 'Ошибка создания события')
  }
}
</script>

<style scoped>
.create-event-page {
  max-width: 500px;
  margin: 40px auto;
  padding: 20px;
  background: white;
  box-shadow: 0 0 4px rgba(0,0,0,0.1);
  border-radius: 8px;
}
form {
  display: flex;
  flex-direction: column;
}
label {
  margin-top: 1rem;
  margin-bottom: 0.3rem;
}
input, textarea {
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}
button {
  margin-top: 1.5rem;
  padding: 0.7rem;
  background-color: #2a7ae2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.buttons {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
</style>
