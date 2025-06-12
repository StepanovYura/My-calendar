<template>
  <div class="notification"></div>
  <main class="container">
    <div class="views">
      <div class="choice-friend">
        <button type="button" id="comm-event-choice" class="comm-btn" @click="loadEvents">
          <img src="" alt="событие">
        </button>
        <button type="button" id="comm-group-choice" class="comm-btn" @click="loadGroups">
          <img src="" alt="группа">
        </button>
        <button type="button" id="comm-friends-choice" class="comm-btn" @click="loadFriends">
          <img src="" alt="друзья">
        </button>
      </div>
      <div class="calendary">
        <div v-if="showEvents">
          <h3>Ваши события:</h3>
          <div class="event-list">
            <div class="event-card" v-for="event in eventsStore.userEvents" :key="event.id">
              <div class="event-info">
                <span class="event-title">{{ event.title }}</span>
                <span class="event-inline">{{ new Date(event.date_time).toLocaleString() }}
                  <span v-if="event.description"> — {{ event.description }}</span>
                  <span
                    v-if="eventsStore.getParticipantsByEvent(event.id).length === 2"
                  > — С другом:
                    {{
                      eventsStore
                        .getParticipantsByEvent(event.id)
                        .find(p => p.username !== eventsStore.currentUsername)?.username
                    }}
                  </span>
                  <!-- Показываем, если событие связано с группой -->
                  <span v-if="event.group_id">
                    — Группа: {{ groupsStore.groupById(event.group_id)?.name || `ID ${event.group_id}` }}
                  </span>
                </span>
              </div>
              <div class="event-actions">
                <router-link :to="`/edit-event/${event?.id}`">
                  <button class="edit-btn">Редактировать</button>
                </router-link>
                <button @click="deleteEvent(event.id)">Удалить</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showGroups">
          <h3>Ваши группы:</h3>
          <div class="group-list">
            <div class="group-card" v-for="group in groupsStore.groups" :key="group.id">
              <router-link :to="`/group/${group.id}`" class="group-info">
                {{ group.name }}
              </router-link>
              <div class="group-actions">
                <button @click="createDraft(group.id)">Создать черновик</button>
                <button v-if="group.created_by === currentUserId" @click="editGroup(group)">Редактировать</button>
                <button
                  v-if="group.created_by === currentUserId"
                  @click="deleteGroup(group)"
                  class="delete-btn"
                >Удалить</button>
                <button
                  v-else
                  @click="leaveGroup(group)"
                  class="leave-btn"
                >Выйти</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showFriends">
          <h3>Ваши друзья:</h3>
          <div class="friend-list">
            <div class="friend-card" v-for="friend in eventsStore.friends" :key="friend.id">
              <div class="friend-info">
                {{ friend.name }} ({{ friend.username }})
              </div>
              <button class="remove-btn" @click="removeFriend(friend)">Удалить</button>
            </div>
          </div>
        </div>

        <button type="button" id="add-event-button">
          <img src="../assets/append-light-96.png" alt="Добавить" width="60" height="60">
        </button>
      </div>
    </div>
  </main>
  <footer>
    <p>Пока заглушка</p>
  </footer>
</template>

<script setup>
import { useEventsStore } from '../stores/eventsStore'
import { onMounted, ref } from 'vue'
import { useGroupsStore } from '../stores/groupsStore'

const groupsStore = useGroupsStore()
const eventsStore = useEventsStore()
const showEvents = ref(true)
const showFriends = ref(false)
const showGroups = ref(false)
const currentUserId = useEventsStore().currentUser?.id || null // если есть

const createDraft = (groupId) => {
  alert(`Создание черновика в группе #${groupId}`)
}

const editGroup = (group) => {
  alert(`Редактировать группу: ${group.name}`)
}

const deleteGroup = async (group) => {
  if (!confirm(`Удалить группу "${group.name}"?`)) return
  try {
    await groupsStore.deleteGroup(group.id)
  } catch (err) {
    alert('Ошибка при удалении группы: ' + err.message)
  }
}

const leaveGroup = async (group) => {
  if (!confirm(`Покинуть группу "${group.name}"?`)) return
  try {
    await groupsStore.leaveGroup(group.id)
  } catch (err) {
    alert('Ошибка при выходе из группы: ' + err.message)
  }
}

const loadGroups = async () => {
  if (showGroups.value) {
    showGroups.value = false
  } else {
    await groupsStore.fetchGroups()
    showGroups.value = true
    showEvents.value = false
    showFriends.value = false
  }
}

const loadFriends = async () => {
  if (showFriends.value) {
    showFriends.value = false
  } else {
    await eventsStore.fetchFriends()
    showFriends.value = true
    showEvents.value = false // чтобы не дублировалось с событиями
  }
}

const loadEvents = async () => {
  if (showEvents.value) {
    showEvents.value = false // Скрываем список, если он уже показан
  } else {
    await eventsStore.fetchUserEvents()
    showEvents.value = true // Показываем, если был скрыт
    showFriends.value = false
  }
}

const deleteEvent = async (eventId) => {
  if (!confirm('Удалить это событие?')) return
  try {
    await eventsStore.deleteEvent(eventId)
    await eventsStore.fetchUserEvents()
  } catch (err) {
    alert('Ошибка при удалении события: ' + err.message)
  }
}

const removeFriend = async (friend) => {
  if (!confirm(`Удалить друга ${friend.name}?`)) return
  try {
    await eventsStore.removeFriend(friend.id)
    await eventsStore.fetchFriends()
  } catch (err) {
    alert('Ошибка при удалении друга: ' + err.message)
  }
}

// Загрузка при монтировании
onMounted(async () => {
  await eventsStore.fetchUserEvents()
  await groupsStore.fetchGroups()
  await eventsStore.fetchFriends()
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

.comm-btn {
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

  /* Добавим фиксированную высоту и скролл */
  height: 743px; /*или сколько тебе нужно */
  overflow-y: auto;
  position: relative;
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

.event-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.event-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #bbb;
  border-radius: 8px;
  padding: 0.8rem 1rem;
  background-color: #f9f9f9;
  transition: box-shadow 0.2s;
}

.event-card:hover {
  box-shadow: 0 0 8px rgba(0,0,0,0.1);
}

.event-info {
  display: flex;
  flex-direction: column;
  font-size: 0.95rem;
  gap: 4px;
}

.event-title {
  font-weight: bold;
  font-size: 1.1rem;
}

.event-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.event-actions {
  display: flex;
  gap: 10px;
}

.event-actions button {
  background-color: #dcdcdc;
  border: none;
  padding: 6px 10px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.event-actions button:hover {
  background-color: #c2c2c2;
}

/* Chrome, Safari */
.calendary::-webkit-scrollbar {
  width: 0;
  height: 0;
}

/* Firefox */
.calendary {
  scrollbar-width: none;
}

/* IE и Edge */
.calendary {
  -ms-overflow-style: none;
}

.event-description,
.event-partner,
.event-group {
  font-size: 0.9rem;
  color: #555;
  margin-top: 4px;
}

.friend-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.friend-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  background-color: #f5f5f5;
}

.friend-info {
  font-size: 1rem;
  color: #333;
}

.remove-btn {
  background-color: #f07070;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.remove-btn:hover {
  background-color: #e05252;
}

.group-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.group-card {
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  background-color: #f0f8ff;
}

.group-info {
  font-size: 1.05rem;
  font-weight: bold;
  color: #2a7fd4;
  text-decoration: none;
  margin-bottom: 6px;
}

.group-info:hover {
  text-decoration: underline;
}

.group-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.group-actions button {
  background-color: #dcdcdc;
  border: none;
  padding: 6px 10px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.group-actions button:hover {
  background-color: #c2c2c2;
}

.leave-btn {
  background-color: #ffaaaa;
}

.leave-btn:hover {
  background-color: #ff8c8c;
}

.delete-btn {
  background-color: #f07070;
  color: white;
}

.delete-btn:hover {
  background-color: #e05252;
}

</style>