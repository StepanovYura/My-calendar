<template>
  <div class="calendar-container">
    <div class="calendar-header">
      <button @click="prevMonth">←</button>
      <h2>{{ monthYearLabel }}</h2>
      <button @click="nextMonth">→</button>
    </div>
    <div class="calendar-grid">
      <div class="day-name" v-for="(day, index) in dayNames" :key="'name-' + index">{{ day }}</div>
      <div
        class="day-cell"
        v-for="(day, index) in calendarDays"
        :key="'cell-' + index"
        :style="getDayStyle(day.date)"
        @click="day.date && emit('open-modal', day.date)"
      >
        {{ day.day }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  matchDays: Object,
  currentYear: Number,
  currentMonth: Number
})

const emit = defineEmits(['change-month'])

const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const monthYearLabel = computed(() => {
  return new Date(props.currentYear, props.currentMonth).toLocaleDateString('ru-RU', {
    month: 'long',
    year: 'numeric'
  })
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

const calendarDays = computed(() => {
  return getCalendarDays(props.currentYear, props.currentMonth)
})

function getDayStyle(date) {
  if (!date) return {}
  const dateStr = date.toISOString().split('T')[0]
  const color = props.matchDays[dateStr]
  if (color === 'green') return { backgroundColor: 'lightgreen' }
  if (color === 'yellow') return { backgroundColor: 'khaki' }
  if (color === 'red') return { backgroundColor: 'lightcoral' }
  return {}
}

function prevMonth() {
  let month = props.currentMonth - 1
  let year = props.currentYear
  if (month < 0) {
    month = 11
    year--
  }
  emit('change-month', { year, month })
}

function nextMonth() {
  let month = props.currentMonth + 1
  let year = props.currentYear
  if (month > 11) {
    month = 0
    year++
  }
  emit('change-month', { year, month })
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
  min-width: 300px;
  max-width: 500px;
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
</style>
