<template>
  <div class="notification" v-if="showNotification" :class="notificationType">
    {{ notificationMessage }}
  </div>
  <main class="container">
    <div class="holder-choice">
      <form id="choice">
        <select name="range" id="range-mode-select" v-model="rangeMode">
        <option value="day">День</option>
        <option value="week">Неделя</option>
        <option value="month">Месяц</option>
      </select>
      </form>
      <div class="view-choice">
        <div class="week-scroll">
          <button class="scroll-btn" @click="goToPreviousWeek">←</button>
          <div class="week-days">
            <div
              v-for="(day, index) in weekDays"
              :key="index"
              :class="{ selected: selectedDay.toDateString() === day.toDateString() }"
              @click="selectDay(day)"
              class="day-item" >
              {{ day.toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric' }) }}
            </div>
          </div>
          <button class="scroll-btn" @click="goToNextWeek">→</button>
        </div>
      </div>
    </div>
    <div class="views">
      <div class="choice-friend">
        <p>Фильтр по друзьям</p>
        <div v-if="eventsStore.hasFriends">
          <div
            v-for="friend in eventsStore.friends"
            :key="friend.id"
            class="friend-item"
            :class="{ selected: eventsStore.selectedFriend?.id === friend.id }"
            @click="eventsStore.selectFriend(friend)">
            {{ friend.name }}
          </div>
        </div>
        <p v-else>Пока друзей нет</p>
      </div>
      <div class="calendary">
        <div v-if="rangeMode === 'day'" class="day-schedule">
          <div v-for="slot in timeSlots" :key="slot" class="time-slot">
            <div class="slot-time">{{ slot }}</div>
            <div class="slot-content">
            </div>
          </div>
          <div
            v-for="event in eventsForSelectedDay()"
            :key="event.id"
            class="event-day"
            :class="{ friend: event._isFriend }"
            :style="getDayEventStyle(event, event._isFriend)"
            @click="openEventModal(event)">
            {{ event.title }}
          </div>
          <router-link to="/create-event" id="add-event-button">
            <img src="../assets/append-light-96.png" alt="Добавить" width="60" height="60">
          </router-link>
        </div>

        <div v-else-if="rangeMode === 'week'" class="week-schedule">
          <div class="week-row">
            <div v-for="(day, index) in weekDays" :key="index" class="day-column" 
              @click="openModal(day)">
              <div class="day-header">
                {{ day.toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric' }) }}
              </div>
              <div class="slots">
                <div
                  v-for="slot in timeSlots"
                  :key="slot"
                  class="time-slot">
                  <div class="slot-time">{{ slot }}</div>
                  <!-- <div class="slot-content">
                  </div> -->
                </div>
                <div
                  v-for="event in weekEventsForDay(day)"
                  :key="event.id"
                  class="event-week"
                  :class="{ friend: event._isFriend }"
                  :style="getWeekEventStyle(event, event._isFriend)"
                  >
                  <!-- {{ event.title }} -->
                </div>
              </div>
            </div>
          </div>
          <router-link to="/create-event" id="add-event-button">
            <img src="../assets/append-light-96.png" alt="Добавить" width="60" height="60">
          </router-link>
        </div>

        <div v-else>
        <Calendar />
        <router-link to="/create-event" id="add-event-button">
          <img src="../assets/append-light-96.png" alt="Добавить" width="60" height="60">
        </router-link>
        <!-- <CalendarMonth :month="selectedMonth" :events="eventsForMonth" @day-click="openDayModal" /> -->
        </div>
      </div>
    </div>
  </main>
  <footer class="app-footer">
    <div class="footer-content">
      <p>Телефон: +7 (916) 256-03-04</p>
      <p>Telegram: <a href="https://t.me/@YuRcHiCkNova" target="_blank">@YuRcHiCkNova</a></p>
      <p>Email: <a href="mailto:yurastep05@gmail.com">yurastep05@gmail.com</a></p>
    </div>
  </footer>

    <!-- Модальное окно -->
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
     <div class="modal-content">
      <h3>События на {{ selectedDateFormatted }}</h3>
      <ul class="events-list">
        <li v-if="weekEventsForDay(selectedDate).length == 0">Нет событий</li>
        <li v-else v-for="(event , index) in weekEventsForDay(selectedDate)" :key="index" class="event-modle" @click="openEventModal(event)">{{ event.title }}</li>
      </ul>
      <router-link :to="{ path: '/create-event', query: { date: selectedDate.toISOString() } }" class="add-btn">Добавить событие</router-link>
      <button class="close-btn" @click="closeModal">Закрыть</button>
    </div>
  </div>

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
      <button class="delete-btn" @click="deleteEvent(selectedEvent?.id)">Удалить</button>
      <button class="close-btn" @click="closeEventModal">Закрыть</button>
    </div>
  </div>
</template>

<!-- РЕАЛИЗОВАТЬ ПРОВЕРКУ ТОГО ЧТО СОБЫТИЯ НЕ НАСЛАИВАЮТСЯ ДРУГ НА ДРУГА ПРИ СОЗДАНИИ -->
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useEventsStore } from '../stores/eventsStore'
import { useAuthStore } from '../stores/authStore'
import Calendar from '../components/Calendar.vue'


const eventsStore = useEventsStore()
const authStore = useAuthStore()
const route = useRoute()

const today = new Date()
const selectedDay = ref(new Date())
const rangeMode = ref('day')
const showModal = ref(false)
const showEventModal = ref(false)
const selectedDate = ref(null)
const selectedEvent = ref(null)
const timeSlots = Array.from({ length: 17 }, (_, i) => `${(i + 8).toString().padStart(2, '0')}:00`)

const notificationMessage = ref('')
const notificationType = ref('') // 'error' | 'success' | 'info'
const showNotification = ref(false)

// Уведомления
function showNotify(message, type = 'info', duration = 3000) {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true

  setTimeout(() => {
    showNotification.value = false
    notificationMessage.value = ''
    notificationType.value = ''
  }, duration)
}

// Расчёт текущей недели
const startOfWeek = (date) => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  return new Date(d.setDate(diff))
}
const currentWeekStart = ref(startOfWeek(today))

const weekDays = computed(() => {
  const start = new Date(currentWeekStart.value)
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    return date
  })
})

function goToPreviousWeek() {
  const newDate = new Date(currentWeekStart.value)
  newDate.setDate(newDate.getDate() - 7)
  currentWeekStart.value = newDate
}

function goToNextWeek() {
  const newDate = new Date(currentWeekStart.value)
  newDate.setDate(newDate.getDate() + 7)
  currentWeekStart.value = newDate
}

function selectDay(date) {
  selectedDay.value = new Date(date)
}

const selectedDateFormatted = computed(() => {
  return selectedDate.value
    ? selectedDate.value.toLocaleDateString('ru-RU')
    : ''
})

function openModal(date) {
  selectedDate.value = date
  console.log('🔍 Выбранная дата в модалке:', date)
  console.log('🗓 События в store:', eventsStore.events)
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function openEventModal(event) {
  selectedEvent.value = event
  showEventModal.value = true
}

function closeEventModal() {
  showEventModal.value = false
}

async function deleteEvent(id) {
  if (!confirm('Удалить это событие?')) return
  try {
    await eventsStore.deleteEvent(id)
    closeEventModal()
  } catch (err) {
    showNotify(err.message, 'error')
    closeEventModal()
  }
}

// Получение событий на выбранный день
function eventsForSelectedDay() {
  const events = eventsStore.eventsForDay(selectedDate.value || selectedDay.value);
  return events;
}

// Получение событий на конкретный день (используется в режиме недели)
function weekEventsForDay(day) {
  console.log("day: ", day)
  console.log('ALL: ', eventsStore.eventsForDay(day), eventsStore.eventsForDay(day).length)
  return eventsStore.eventsForDay(day)
}

// высота одного временного слота (например, 50px)
const SLOT_HEIGHT = 50

function getEventStyle(event, isFriend = false) {
  const start = new Date(event.date_time)
  const startHour = 23
  const startMinutes = 0

  const topOffset = ((startHour - 8) + startMinutes / 60) * SLOT_HEIGHT
  const height = Math.max(20, (event.duration_minutes / 60) * SLOT_HEIGHT) // min 20px height
  // const height = (event.duration_minutes / 60) * SLOT_HEIGHT

  // Если фильтр по другу включён — делим пространство пополам
  const width = eventsStore.selectedFriend ? '50%' : '100%' // НУЖНО ПРАВИТЬ СТИЛИ
  const left = isFriend ? '50%' : '0'

  return {
    top: `${topOffset}px`,
    height: `${height}px`,
    width,
    left,
    right: `20px`,
    position: 'absolute'
  }
}

function getDayEventStyle(event, isFriend = false) {
  const START_HOUR = 8;
  const SLOT_HEIGHT = 61;

  const start = new Date(event.date_time);
  const startHour = start.getHours();
  const startMinutes = start.getMinutes();

  const topOffset = ((startHour - START_HOUR) + startMinutes / 60) * SLOT_HEIGHT;
  const height = Math.max(20, (event.duration_minutes / 60) * SLOT_HEIGHT);

  // ширина рассчитываемая
  let width = 'calc(100% - 70px)';
  if (eventsStore.selectedFriend) {
    width = 'calc((100% - 70px) / 2)';
  }

  const style = {
    top: `${topOffset}px`,
    height: `${height}px`,
    width: width
  };

  if (isFriend) {
    style.left = 'calc(70px + (100% - 70px) / 2)';
  }
  
  console.log(`Event "${event.title}": ${startHour}:${startMinutes} => top: ${topOffset}px, height: ${height}px`);
  return style;
}

function getWeekEventStyle(event, isFriend = false) {
  const START_HOUR = 8;
  const SLOT_HEIGHT = 40.2;

  const start = new Date(event.date_time);
  const startHour = start.getHours();
  const startMinutes = start.getMinutes();

  const topOffset = ((startHour - START_HOUR) + startMinutes / 60) * SLOT_HEIGHT;
  const height = Math.max(20, (event.duration_minutes / 60) * SLOT_HEIGHT);

  let width = 'calc(100% - 70px)';
  if (eventsStore.selectedFriend) {
    width = 'calc((100% - 70px) / 2)';
  }

  const style = {
    top: `${topOffset}px`,
    height: `${height}px`,
    width: width
  };

  if (isFriend) {
    style.left = 'calc(70px + (100% - 70px) / 2)';
  }

  return style;
}



// Загрузка при монтировании
onMounted(async () => {
  await eventsStore.fetchEvents()
  await eventsStore.fetchFriends()
  watch(
    () => route.query.date,
    (newDate) => {
      if (newDate) {
        const parsed = new Date(newDate)
        if (!isNaN(parsed)) {
          selectedDay.value = parsed
          rangeMode.value = 'day'
        }
      }
    },
    { immediate: true } // сработает сразу при заходе на страницу
  )
})
</script>


<style scoped>
body {
    font-family: "Arial", sans-serif;
    display: flex;
    flex-direction: column;
    min-height: 100vh;

    background-color: white;
    color: #333;
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
    margin-left: 80px;
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
    background: none;
    border: none;
    cursor: pointer;
}

.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  font-weight: bold;
  z-index: 10000;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  color: white;
  animation: fadeInOut 3s ease-in-out;
}

.notification.success {
  background-color: #2e7d32; /* зелёный */
}

.notification.error {
  background-color: #c62828; /* красный */
}

.notification.info {
  background-color: #0277bd; /* голубой */
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(-10px); }
  10%, 90% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-10px); }
}

.container {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
    flex-grow: 1;
}

.holder-choice {
    flex: 1;
    display: flex;
    flex-direction: row;
    min-height: 70px;
    max-height: 70px;

    background-color: white;
    border-radius: 4px;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
}

#choice {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 1rem 0 1rem;
}

.choice-friend {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: start;

    padding: 0 1rem 0 1rem;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
}

#range-mode-select {
    margin-top: 5px;
}

.friend-item {
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
}
.friend-item.selected {
  background-color: #4caf50;
  color: white;
}

.views {
    flex: 8;
    display: flex;
    flex-direction: row;
    gap: 1rem;

    background-color: white;
    border-radius: 4px;
}

.view-choice {
    flex: 8;
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-left: 1rem;

    background-color: white;
    border-radius: 4px;
}

.calendary {
    flex: 8;

    background-color: white;
    border-radius: 4px;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);

    margin: 0 auto;
    position: relative;
}

.week-scroll {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.week-days {
  display: flex;
  gap: 0.5rem;
  width: 481px;
}

.day-item {
  padding: 4.8px 9.6px;
  background-color: #eee;
  border-radius: 5px;
  cursor: pointer;
  min-width: 20px;
  max-width: 63.05px;
}

.day-item.selected {
  background-color: #4caf50;
  color: white;
}

.day-schedule {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  /* min-height: 100%; */
}

.time-slot {
  display: flex;
  flex-direction: row;
  margin-bottom: 0.5rem;
}

.slot-time {
  width: 60px;
  font-weight: bold;
}

.slot-content {
  flex: 1;
  position: relative;
  height: 50px; /* каждый час — 50px высоты */
  /* padding-left: 1rem; */
  border-bottom: 1px solid #ccc;
}

.event-day {
  position: absolute;
  left: 70px;
  background-color: #dcedc8;
  border: 1px solid #a5d6a7;
  border-radius: 4px;
  padding: 2px 4px;
  box-sizing: border-box;
  overflow: hidden;
}

.event {
  /* position: absolute;
  left: 0;
  right: 0;
  padding: 4px;
  background-color: #dcedc8;
  border-radius: 4px;
  z-index: 1; */
  
  position: absolute;
  left: 0;
  background-color: #dcedc8;
  border: 1px solid #a5d6a7;
  border-radius: 4px;
  padding: 2px 4px;
  box-sizing: border-box;
  overflow: hidden;
}

.event-modle {
  cursor: pointer;
}

#add-event-button {
  position: absolute;
  right: 50px;
  top: 700px;
  background: none;
  border: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  outline: none;
  z-index: 1000000;
  /* opacity: 0.4; */
}


footer {
  min-height: 60px;
  max-height: 90px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  text-align: center;
  width: 100%;
  font-size: 0.9rem;
  color: #555;
  display: flex;
  flex-direction: row;
  align-items:baseline;
  justify-content: space-around;
  border-radius: 20%;
  border-color: #333;
}

.footer-content a {
  color: #007BFF;
  text-decoration: none;
}

.footer-content a:hover {
  text-decoration: underline;
}

.week-schedule {
  display: flex;
  flex-direction: row;
  overflow-x: auto;
  min-height: 100%;
  max-height: 100%;
}

.week-row {
  display: flex;
  justify-content: center;
  min-width: 100%;
  gap: 1rem;
}

.event-week {
  position: absolute;
  left: 60px;
  background-color: #bbdefb;
  border: 1px solid #90caf9;
  border-radius: 4px;
  padding: 2px 4px;
  box-sizing: border-box;
  overflow: hidden;
}

.day-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  min-width: 100px;
  max-width: 160px;
  position: relative;
}

.day-header {
  background-color: #f5f5f5;
  padding: 0.5rem;
  font-weight: bold;
  text-align: center;
}

.slots {
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  /* min-height: 100%;
  max-height: 100%; */
  flex-grow: 1;
  justify-content: space-around;
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

.event.friend {
  background-color: #c5cae9; /* другой цвет для друга */
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

.scroll-btn {
  background-color: black;
}

@media (max-width: 768px) {
  .calendary {
    max-width: 100%;
  }
  .event {
    font-size: 0.8rem;
    padding: 1px 2px;
  }
}

.event-day.friend {
  background-color: aqua; /* синий для друга */
  border-color: rgb(41, 173, 173);
}

</style>
