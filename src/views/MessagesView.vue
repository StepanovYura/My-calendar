<template>
  <div class="notification"></div>
  <main class="container">
    <div class="views">
      <div class="choice-friend">
        <button class="filter-btn" @click="toggleRequestFilter">Запросы
            <span v-if="isRequestFilterActive">✓</span>
        </button>
        <button class="filter-btn" @click="toggleAlertFilter">Оповещения
            <span v-if="isAlertFilterActive">✓</span>
        </button>
      </div>

      <div class="calendary">
        <h3>Ваши уведомления</h3>

        <div v-if="isLoading" class="spinner">Загрузка...</div>

        <ul class="notification-list" v-else>
          <li v-for="note in notifications" :key="note.id" :class="{ read: note.read_status }">
            <div class="note-content">
              <p><strong>{{ note.sender_name }}</strong>: {{ note.message }}</p>
              <small>{{ new Date(note.created_at).toLocaleString() }}</small>
            </div>
            <div class="note-actions">
              <button @click="toggleRead(note)">
                {{ note.read_status ? 'Не прочитано' : 'Прочитано' }}
              </button>
              <button 
                v-if="note.type === 'invitation' && (note.group_id !== null || note.friend_request_id !== null)" 
                @click="openRespondModal(note)">
                Ответить
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Модалка ответа -->
    <div v-if="showRespondModal" class="modal-overlay" @click.self="closeRespondModal">
      <div class="modal-content">
        <h3>Ответить на приглашение</h3>
        <p>{{ selectedNote?.message }}</p>
        <div class="modal-buttons">
          <button class="all-btn" @click="respondToInvitation('accept')">Согласиться</button>
          <button class="all-btn" @click="respondToInvitation('decline')">Отказаться</button>
          <button class="all-btn" @click="closeRespondModal">Назад</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import {
  getAllNotifications,
  getInvitationNotifications,
  getGeneralNotifications,
  markNotificationAsRead
} from '../api-frontend/notifications'
import { respondToFriendRequest } from '../api-frontend/friends'
import { respondToGroupInvitation } from '../api-frontend/groups' // предположим, у тебя есть такой API

const authStore = useAuthStore()
const isRequestFilterActive = ref(false)
const isAlertFilterActive = ref(false)

const notifications = ref([])
const cache = {
  all: null,
  invitations: null,
  general: null
}

const isLoading = ref(false)
const showRespondModal = ref(false)
const selectedNote = ref(null)

onMounted(() => {
  loadAll()
})

async function toggleRequestFilter() {
  isRequestFilterActive.value = !isRequestFilterActive.value
  await applyFilters()
}

async function toggleAlertFilter() {
  isAlertFilterActive.value = !isAlertFilterActive.value
  await applyFilters()
}

async function applyFilters() {
  const token = authStore.token
  isLoading.value = true

  try {
    if (
      (isRequestFilterActive.value && isAlertFilterActive.value) ||
      (!isRequestFilterActive.value && !isAlertFilterActive.value)
    ) {
      // Обе нажаты или обе не нажаты — загружаем все
      if (cache.all) {
        notifications.value = cache.all
      } else {
        notifications.value = await getAllNotifications(token)
        cache.all = notifications.value
      }
    } else if (isRequestFilterActive.value) {
      if (cache.invitations) {
        notifications.value = cache.invitations
      } else {
        notifications.value = await getInvitationNotifications(token)
        cache.invitations = notifications.value
      }
    } else if (isAlertFilterActive.value) {
      if (cache.general) {
        notifications.value = cache.general
      } else {
        notifications.value = await getGeneralNotifications(token)
        cache.general = notifications.value
      }
    }
  } catch (err) {
    alert('Ошибка загрузки уведомлений: ' + err.message)
  } finally {
    isLoading.value = false
  }
}

async function loadAll() {
  if (cache.all) {
    notifications.value = cache.all
    return
  }
  isLoading.value = true
  const token = authStore.token
  notifications.value = await getAllNotifications(token)
  cache.all = notifications.value
  isLoading.value = false
}

async function filterInvitations() {
  if (cache.invitations) {
    notifications.value = cache.invitations
    return
  }
  isLoading.value = true
  const token = authStore.token
  notifications.value = await getInvitationNotifications(token)
  cache.invitations = notifications.value
  isLoading.value = false
}

async function filterGeneral() {
  if (cache.general) {
    notifications.value = cache.general
    return
  }
  isLoading.value = true
  const token = authStore.token
  notifications.value = await getGeneralNotifications(token)
  cache.general = notifications.value
  isLoading.value = false
}

async function toggleRead(note) {
  const token = authStore.token
  await markNotificationAsRead(token, note.id)
  note.read_status = !note.read_status
}

function openRespondModal(note) {
  selectedNote.value = note
  showRespondModal.value = true
}

function closeRespondModal() {
  showRespondModal.value = false
  selectedNote.value = null
}

async function respondToInvitation(action) {
  if (!selectedNote.value) return
  const token = authStore.token

  try {
    if (selectedNote.value.type === 'invitation') {
      if (selectedNote.value.group_id === null) {
        // Приглашение в друзья
        await respondToFriendRequest(token, selectedNote.value.friend_request_id, action)
        alert(`Вы ${action === 'accept' ? 'приняли' : 'отклонили'} заявку в друзья`)
      } else {
        // Приглашение в группу
        await respondToGroupInvitation(token, selectedNote.value.group_id, action)
        alert(`Вы ${action === 'accept' ? 'приняли' : 'отклонили'} приглашение в группу`)
      }
    }

    // После ответа очищаем кеш приглашений и перезагружаем
    cache.invitations = null
    await filterInvitations()
  } catch (err) {
    alert('Ошибка при ответе: ' + err.message)
  } finally {
    closeRespondModal()
  }
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
  background-color: black;
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

.notification-list {
  list-style: none;
  padding: 0;
}

.notification-list li {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.notification-list li.read {
  background-color: #f0f0f0;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.notification-list {
  list-style: none;
  padding: 0;
}

.notification-list li {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.notification-list li.read {
  background-color: #f0f0f0;
}

.note-actions button {
  margin-right: 0.5rem;
  background-color: black;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.filter-btn {
  margin-bottom: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: black;
}

.spinner {
  text-align: center;
  font-weight: bold;
  padding: 1rem;
}

.all-btn {
  background-color: black;
}

@media (max-width: 768px) {
  .views {
    flex-direction: column;
    gap: 0.5rem;
  }

  .choice-friend {
    padding: 1rem 0.5rem;
    gap: 0.5rem;
  }

  .filter-btn {
    width: 100%;
    font-size: 0.9rem;
  }

  .calendary {
    padding: 0.5rem;
  }

  .notification-list li {
    padding: 0.8rem;
    font-size: 0.9rem;
  }

  .note-actions {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .note-actions button {
    width: 100%;
  }

  .modal-content {
    width: 90%;
    padding: 1rem;
  }

  footer {
    padding: 10px;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .filter-btn {
    font-size: 0.8rem;
    padding: 0.4rem;
  }

  .notification-list li {
    font-size: 0.85rem;
  }

  .modal-content {
    width: 95%;
  }

  .modal-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }

  .all-btn {
    font-size: 0.85rem;
  }
}


</style>