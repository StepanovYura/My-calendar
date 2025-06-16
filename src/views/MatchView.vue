<template>
  <div class="notification"></div>
  <main class="container">
    <div class="views">
      <div class="choice-friend">
        <!-- Кнопка группы -->
        <div class="dropdown">
          <button type="button" class="match-btn" @click="toggleGroupDropdown">
            Группы
          </button>
          <div class="dropdown-content" v-if="showGroupDropdown">
            <div v-for="group in groupsStore.groups" :key="group.id" @click="selectGroup(group)">
              {{ group.name }}
            </div>
          </div>
        </div>

        <!-- Кнопка друзья -->
        <div class="dropdown">
          <button type="button" class="match-btn" @click="toggleFriendDropdown">
            Друзья
          </button>
          <div class="dropdown-content" v-if="showFriendDropdown">
            <div v-for="friend in friendsStore.friends" :key="friend.id" @click="selectFriend(friend)">
              {{ friend.username }}
            </div>
          </div>
        </div>

        <button @click="exportToExcel" class="match-btn">
          Экспорт в Excel
        </button>
      </div>

      <div class="calendary">
        <CalendarMatch
          :match-days="matchDays"
          :current-year="currentYear"
          :current-month="currentMonth"
          @change-month="handleMonthChange"
          @open-modal="openModal"
        />
      </div>
    </div>  
  </main>
  <!-- Модальное окно-->
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <h3>Совпадения на {{ selectedDateFormatted }}</h3>
      <ul v-if="currentDayMatches?.matches.length">
        <li v-for="(match, index) in currentDayMatches.matches" :key="index">
          {{ match.interval }}: {{ match.users.join(', ') }}
        </li>
      </ul>
      <p v-else>Нет совпадений</p>
      <button class="close-btn" @click="closeModal">Закрыть</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGroupsStore } from '../stores/groupsStore'
import { useFriendsStore } from '../stores/friendsStore'
import { useAuthStore } from '../stores/authStore'
import { getMatchDays } from '../api-frontend/match'
import * as XLSX from 'xlsx'
import CalendarMatch from '../components/CalendarMatch.vue'

const groupsStore = useGroupsStore()
const friendsStore = useFriendsStore()
const authStore = useAuthStore()

const showGroupDropdown = ref(false)
const showFriendDropdown = ref(false)

const selectedGroup = ref(null)
const selectedFriend = ref(null)
const matchDays = ref({})
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth())

const showModal = ref(false)
const selectedDate = ref(null)

const selectedDateFormatted = computed(() =>
  selectedDate.value
    ? selectedDate.value.toISOString().split('T')[0]
    : ''
)

const currentDayMatches = computed(() => {
  return matchDays.value[selectedDateFormatted.value] || null
})

function openModal(date) {
  selectedDate.value = date
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

onMounted(() => {
  groupsStore.fetchGroups()
  friendsStore.fetchFriends()
})

function toggleGroupDropdown() {
  showGroupDropdown.value = !showGroupDropdown.value
  showFriendDropdown.value = false
}

function toggleFriendDropdown() {
  showFriendDropdown.value = !showFriendDropdown.value
  showGroupDropdown.value = false
}

function selectGroup(group) {
  selectedGroup.value = group
  selectedFriend.value = null
  showGroupDropdown.value = false
  loadMatches()
}

function selectFriend(friend) {
  selectedFriend.value = friend
  selectedGroup.value = null
  showFriendDropdown.value = false
  loadMatches()
}

async function loadMatches() {
  const authStore = useAuthStore()
  const token = authStore.token

  const participants = selectedGroup.value
    ? selectedGroup.value.members?.map(m => m.id) || []
    : selectedFriend.value
    ? [selectedFriend.value.id]
    : []

  if (participants.length === 0) {
    console.warn('Нет выбранных участников для загрузки совпадений')
    return
  }

  try {
    isLoading.value = true
    const data = await getMatchDays(token, participants, currentYear.value, currentMonth.value + 1)
    matchDays.value = data
    error.value = null
  } catch (err) {
    console.error('Ошибка загрузки совпадений:', err)
    error.value = err.message || 'Ошибка загрузки совпадений'
  } finally {
    isLoading.value = false
  }
}

function handleMonthChange({ year, month }) {
  currentYear.value = year
  currentMonth.value = month
  loadMatches()
}

function exportToExcel() {
  const rows = []

  for (const [date, data] of Object.entries(matchDays.value)) {
    if (data.matches.length === 0) {
      rows.push({
        Дата: date,
        Цвет: data.color.toUpperCase(),
        Интервал: 'Нет совпадений',
        Участники: ''
      })
    } else {
      for (const match of data.matches) {
        rows.push({
          Дата: date,
          Цвет: data.color.toUpperCase(),
          Интервал: match.interval,
          Участники: match.users.join(', ')
        })
      }
    }
  }

  const ws = XLSX.utils.json_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Match Statistics')
  XLSX.writeFile(wb, 'match_statistics.xlsx')
}
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

.search {
    visibility: hidden;
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

    padding: 2rem 1rem 0 1rem;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
    gap: 5px;

}

.match-btn {
  color: #333;
  background-color: rgb(209, 204, 204);
  min-height: 40px;
  min-width: 120px;
}

#range-select {
    margin-top: 5px;
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
}

footer {
    min-height: 90px;
    padding-left: 20px;
}

.dropdown {
  position: relative;
}
.dropdown-content {
  position: absolute;
  background-color: #f9f9f9;
  min-width: 160px;
  border: 1px solid #ccc;
  z-index: 1;
}
.dropdown-content div {
  padding: 8px 12px;
  cursor: pointer;
}
.dropdown-content div:hover {
  background-color: #f1f1f1;
}

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
  max-width: 90%;
  width: 400px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.close-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  border: none;
  background-color: #2a7ae2;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

</style>
