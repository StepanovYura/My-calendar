<template>
  <div class="calendar-container">
    <div class="calendar-header">
      <button class="scroll-btn" @click="prevMonth">←</button>
      <h2>{{ monthYearLabel }}</h2>
      <button class="scroll-btn" @click="nextMonth">→</button>
    </div>
    <div class="calendar-grid">
      <div class="day-name" v-for="(day, index) in dayNames" :key="'name-' + index">{{ day }}</div>
      <div class="day-cell"
           v-for="(day, index) in calendarDays"
           :key="'cell-' + index"
           :class="{ 'today': isToday(day.date), 'clickable': day.date, 
           'has-event': day.date && daysWithEvents.includes(`${day.date.getFullYear()}-${day.date.getMonth()}-${day.date.getDate()}`)
           }"
           @click="day.date && openModal(day.date)">
        {{ day.day }}
      </div>
    </div>

    <!-- Модалка на день -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3>События на {{ selectedDateFormatted }}</h3>
        <ul class="events-list">
          <li v-if="dayEvents.length === 0">Нет событий</li>
          <li v-for="event in dayEvents" :key="event.id" @click="openEventModal(event)" class="clickable-event">
            {{ event.title }}
          </li>
        </ul>
        <router-link :to="{ path: '/create-event', query: { date: selectedDate.toISOString() } }" class="add-btn">Добавить событие</router-link>
        <button class="close-btn" @click="closeModal">Закрыть</button>
      </div>
    </div>

    <!-- Модалка подробностей события -->
    <div v-if="showEventModal" class="modal-overlay" @click.self="closeEventModal">
      <div class="modal-content">
        <h3>Событие: {{ selectedEvent?.title }}</h3>
        <p><strong>Описание:</strong> {{ selectedEvent?.description || 'нет' }}</p>
        <p><strong>Время начала:</strong> {{ new Date(selectedEvent?.date_time).toLocaleString('ru-RU') }}</p>
        <p><strong>Длительность:</strong> {{ selectedEvent?.duration_minutes }} минут</p>
        <p v-if="selectedEvent?.group_name"><strong>Группа:</strong> {{ selectedEvent.group_name }}</p>
        <p v-if="selectedEvent?.friend_name"><strong>С другом:</strong> {{ selectedEvent.friend_name }}</p>

        <router-link :to="`/edit-event/${selectedEvent?.id}`">
          <button class="edit-btn">Редактировать</button>
        </router-link>
        <button class="close-btn" @click="closeEventModal">Закрыть</button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, computed } from 'vue'
import { useEventsStore } from '../stores/eventsStore'

const eventsStore = useEventsStore()

const today = new Date()
const currentMonth = ref(today.getMonth())
const currentYear = ref(today.getFullYear())

const showModal = ref(false)
const showEventModal = ref(false)
const selectedDate = ref(null)
const selectedEvent = ref(null)
const dayEvents = ref([])
const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const monthYearLabel = computed(() => {
  return new Date(currentYear.value, currentMonth.value).toLocaleDateString('ru-RU', {
    month: 'long',
    year: 'numeric'
  })
})

const selectedDateFormatted = computed(() => {
  return selectedDate.value
    ? selectedDate.value.toLocaleDateString('ru-RU')
    : ''
})

function getCalendarDays(year, month) {
  const start = new Date(year, month, 1)
  const end = new Date(year, month + 1, 0)
  const daysInMonth = end.getDate()
  const startWeekDay = (start.getDay() + 6) % 7

  const days = []

  for (let i = 0; i < startWeekDay; i++) {
    days.push({ day: '', date: null })
  }

  for (let day = 1; day <= daysInMonth; day++) {
    days.push({
      day,
      date: new Date(year, month, day)
    })
  }

  return days
}

const daysWithEvents = computed(() => {
  return eventsStore.events.map(e => {
    const d = new Date(e.date_time)
    return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
  })
})

const calendarDays = computed(() => {
  console.log("AAAAAA: ", currentYear.value, currentMonth.value)
  return getCalendarDays(currentYear.value, currentMonth.value)
})

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value -= 1
  } else {
    currentMonth.value -= 1
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value += 1
  } else {
    currentMonth.value += 1
  }
}

function isToday(date) {
  if (!date) return false
  const d = new Date()
  return date.getDate() === d.getDate() &&
         date.getMonth() === d.getMonth() &&
         date.getFullYear() === d.getFullYear()
}

function openModal(date) {
  selectedDate.value = date
  dayEvents.value = eventsStore.eventsForDay(date)
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function openEventModal(event) {
  selectedEvent.value = event
  console.log('event-info: ', event)
  showEventModal.value = true
}

function closeEventModal() {
  showEventModal.value = false
}
</script>


<style scoped>
.calendar-container {
  padding: 1rem;
  position: relative;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 5px;
  margin-top: 1rem;
}

.day-name {
  font-weight: bold;
  text-align: center;
  color: #555;
}

.day-cell {
  text-align: center;
  padding: 10px 0;
  border-radius: 4px;
  background: #f5f5f5;
}

.day-cell.today {
  background-color: #b3d4fc;
  font-weight: bold;
}

.day-cell.clickable {
  cursor: pointer;
  transition: background-color 0.2s;
}

.day-cell.clickable:hover {
  background-color: #d0e6ff;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.events-list {
  margin: 1rem 0;
}

.add-btn,
.close-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  border: none;
  background-color: #2a7ae2;
  color: white;
  cursor: pointer;
  border-radius: 4px;
}

.close-btn {
  background-color: #aaa;
  margin-left: 0.5rem;
}

.has-event {
  background-color: yellow;
}
.has-event.friend {
  background-color: aqua;
}
.clickable-event {
  cursor: pointer;
  padding: 4px;
}

.scroll-btn {
  background-color: black;
}

</style>
