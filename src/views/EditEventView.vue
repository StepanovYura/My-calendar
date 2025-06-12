<template>
  <div class="edit-event-page">
    <h2>Редактирование события</h2>
    <form @submit.prevent="submitEvent">
      <label>Название:</label>
      <input v-model="form.title" type="text" required />

      <label>Описание:</label>
      <textarea v-model="form.description" rows="4" />

      <label>Дата:</label>
      <input v-model="form.date" type="date" required />

      <label>Время:</label>
      <input v-model="form.time" type="time" required />

      <label>Длительность (мин):</label>
      <input v-model.number="form.duration_minutes" type="number" min="1" required />
      
      <!-- Блок участника события -->
      <div class="participant-section" v-if="eventParticipant">
        <label>Участник:</label>
        <div class="participant-info">
          <span>{{ eventParticipant.name }}</span>
        </div>
      </div>
      
      <!-- Поле для добавления друга, если его ещё нет -->
      <div v-if="!eventParticipant">
        <label>Добавить друга (никнейм):</label>
        <div class="add-friend">
          <input 
            v-model="newFriendUsername" 
            type="text" 
            placeholder="Введите никнейм друга"
          />
          <button 
            type="button" 
            class="add-btn"
            @click="addParticipant"
            :disabled="!newFriendUsername"
          >
            Добавить
          </button>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="save-btn">Сохранить</button>
        <button type="button" class="cancel-btn" @click="cancelEdit">Отмена</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventsStore } from '../stores/eventsStore'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const route = useRoute()
const eventsStore = useEventsStore()
const authStore = useAuthStore()
const eventId = route.params.id

const form = ref({
  title: '',
  description: '',
  date: '',
  time: '',
  duration_minutes: 60,
  friend_username: ''
})

const newFriendUsername = ref('')
const currentEvent = ref(null)

// Участник события (друг, если он есть)
const eventParticipant = computed(() => {
  const participants = eventsStore.getParticipantsByEvent(eventId)
  if (!Array.isArray(participants)) return null
  if (participants.length <= 1) return null

  const currentUserId = authStore.user?.id
  return participants.find(p => p.id !== currentUserId) || null
})

// Загрузка данных события
onMounted(async () => {
  try {
    await eventsStore.fetchEvents()
    const event = eventsStore.events.find(e => e.id == eventId)
    if (!event) throw new Error('Событие не найдено')
    currentEvent.value = event

    await eventsStore.fetchEventParticipants(eventId)

    const eventDate = new Date(event.date_time)
    const dateStr = eventDate.toISOString().split('T')[0]
    const timeStr = eventDate.toTimeString().slice(0, 5)

    form.value = {
      title: event.title,
      description: event.description,
      date: dateStr,
      time: timeStr,
      duration_minutes: event.duration_minutes,
      friend_username: '' // не используется для отображения, только ввода
    }
  } catch (err) {
    alert(err.message)
    router.back()
  }
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

    await eventsStore.updateEvent(eventId, eventData)
    router.back()
  } catch (err) {
    alert(err.message || 'Ошибка сохранения события')
  }
}

async function addParticipant() {
  if (!newFriendUsername.value) return
  try {
    await eventsStore.addParticipantToEvent(eventId, newFriendUsername.value)
    await eventsStore.fetchEventParticipants(eventId)
    await eventsStore.fetchEvents()
    const updatedEvent = eventsStore.events.find(e => e.id == eventId)
    currentEvent.value = updatedEvent
    newFriendUsername.value = ''
  } catch (err) {
    alert(err.message || 'Ошибка добавления участника')
  }
}

function cancelEdit() {
  router.back()
}
</script>

<style scoped>
.edit-event-page {
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
  font-weight: bold;
}

input, textarea {
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.participant-section {
  margin-top: 1rem;
}

.participant-info {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.add-friend {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.add-friend input {
  flex: 1;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

button {
  padding: 0.7rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.save-btn {
  background-color: #2a7ae2;
  color: white;
  flex: 1;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
  flex: 1;
}

.add-btn {
  background-color: #4caf50;
  color: white;
  width: 100px;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
