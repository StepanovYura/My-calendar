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
                        .find(p => p.name !== eventsStore.currentUsername)?.name
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
              <div class="group-info">
                {{ group.name }}
              </div>
              <div class="group-actions">
                <router-link :to="`/create-draft/${group.id}`">
                  <button>Создать черновик</button>
                </router-link>
                <router-link v-if="group.created_by === currentUser.id" :to="`/groups/${group.id}/edit`">
                  <button>Редактировать</button>
                </router-link>
                <button @click="openGroupInfo(group)">Информация</button>
                <button @click="openInvite(group)">Пригласить</button>
                <button @click="openVoting(group)">Голосования</button>
                <button @click="openSchedule(group)">Расписание</button>
                <button
                  v-if="group.created_by === currentUser.id"
                  @click="deleteGroup(group)"
                  class="delete-btn"
                >Удалить</button>
                <button
                  v-else
                  @click="leaveGroup(group)"
                  class="leave-btn"
                >Выйти</button>
                <div class="avatarka">
                  <img :src="getGroupAvatarUrl(group)" alt="avatar" id="avatar" width="50" height="50" />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showFriends">
          <h3>Ваши друзья:</h3>
          <div class="friend-list">
            <div class="friend-card" v-for="friend in eventsStore.friends" :key="friend.id">
              <div class="friend-info">
                {{ friend.name }}
              </div>
              <button class="remove-btn" @click="removeFriend(friend)">Удалить</button>
            </div>
          </div>
        </div>

        <button type="button" id="add-event-button" @click="openAddModal">
          <img src="../assets/append-light-96.png" alt="Добавить" width="60" height="60">
        </button>
      </div>
    </div>

    <!-- Модалка информации о группе -->
    <div v-if="showGroupInfoModal" class="modal">
      <div class="modal-content">
        <h3>Информация о группе</h3>
        <img
          v-if="selectedGroup?.avatar_url"
          :src="selectedGroup.avatar_url"
          alt="Аватарка группы"
          style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px"
        />
        <p><strong>Название:</strong> {{ selectedGroup?.name }}</p>
        <p><strong>Описание:</strong> {{ selectedGroup?.description || '—' }}</p>
        <p><strong>Создатель:</strong> {{ selectedGroup?.creator_name || '—' }}</p>
        <p><strong>Участники:</strong></p>
        <ul>
          <li v-for="member in selectedGroup?.members" :key="member.user_id">
            {{ member.user_name }} (ID: {{ member.user_id }}) — вступил: {{ new Date(member.joined_at).toLocaleDateString() }}
          </li>
        </ul>
        <button class="all-btn" @click="showGroupInfoModal = false">Закрыть</button>
      </div>
    </div>

    <!-- Модалка приглашения -->
    <div v-if="showInviteModal" class="modal">
      <div class="modal-content">
        <h3>Пригласить в группу "{{ selectedGroup?.name }}"</h3>
        <input type="text" placeholder="Имя пользователя или email" v-model="inviteUsername" />
        <div class="modal-buttons">
          <button class="all-btn" @click="sendInvite">Отправить</button>
          <button class="all-btn" @click="showInviteModal = false">Назад</button>
        </div>
      </div>
    </div>

    <!-- Модалка голосований -->
    <div v-if="showVotingModal" class="modal">
      <div class="modal-content">
        <h3>Голосования в группе "{{ selectedGroup?.name }}"</h3>
        <ul v-if="groupsStore.groupDetails?.drafts?.length">
          <li v-for="draft in groupsStore.groupDetails.drafts" :key="draft.id">
            <a href="#" @click.prevent="openDraftVote(draft)">{{ draft.title }}</a>
          </li>
        </ul>
        <p v-else>Нет активных голосований</p>
        <button class="all-btn" @click="showVotingModal = false">Закрыть</button>
      </div>
    </div>

    <!-- Модалка голосования -->
    <div v-if="showVoteModal" class="modal">
      <div class="modal-content">
        <h3>Хотите ли вы участвовать в "{{ selectedDraft?.title }}"?</h3>
        <p>Дата: {{ new Date(selectedDraft?.date).toLocaleDateString() }}</p>
        <button class="all-btn" @click="voteYes">Да</button>
        <button class="all-btn" @click="voteNo">Нет</button>
        <button class="all-btn" @click="showVoteModal = false">Назад</button>
      </div>
    </div>

    <!-- Модалка ввода слотов -->
    <div v-if="showSlotsModal" class="modal">
      <div class="modal-content">
        <h3>Укажите свои слоты для "{{ selectedDraft?.title }}"</h3>
        <div v-for="(slot, index) in voteSlots" :key="index" class="slot-row">
          <input type="time" v-model="slot.start" required />
          <input type="time" v-model="slot.end" required />
          <button class="all-btn" @click.prevent="removeSlot(index)">Удалить</button>
        </div>
        <button class="all-btn" @click.prevent="addSlot">Добавить слот</button>
        <button class="all-btn" @click="submitVoteWithSlots">Отправить</button>
        <button class="all-btn" @click="showSlotsModal = false">Отмена</button>
      </div>
    </div>

    <!-- Модалка расписания -->
    <div v-if="showGroupScheduleModal" class="modal">
      <div class="modal-content">
        <h3>События группы "{{ selectedGroup?.name }}"</h3>
        <ul v-if="groupSchedule.length">
          <li v-for="event in groupSchedule" :key="event.id">
            <strong>{{ event.title }}</strong> —
            {{ new Date(event.date_time).toLocaleString() }} ({{ event.duration_minutes }} мин)
            <div v-if="event.description">{{ event.description }}</div>
          </li>
        </ul>
        <p v-else>Нет событий</p>
        <button class="all-btn" @click="showGroupScheduleModal = false">Закрыть</button>
      </div>
    </div>

    <!-- Модалка выбора действия при добавлении -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content">
        <h3>Что вы хотите сделать?</h3>
        <div class="modal-buttons">
          <button class="modal-my" @click="openAddFriend">Добавить друга</button>
          <router-link to="/create-event">
            <button class="modal-my">Создать событие</button>
          </router-link>
          <router-link to="/create-group">
            <button class="modal-my">Создать группу</button>
          </router-link>
        </div>
        <button class="close-btn" @click="closeAddModal">Назад</button>
      </div>
    </div>

    <!-- Модалка добавления друга -->
    <div v-if="showAddFriendModal" class="modal-overlay" @click.self="closeAddFriendModal">
      <div class="modal-content">
        <h3>Добавить друга</h3>
        <input type="text" v-model="friendSearchQuery" placeholder="Имя пользователя или email" />
        <div class="modal-buttons">
          <button class="modal-my" @click="sendFriendRequest">Отправить запрос</button>
          <button class="modal-my" @click="closeAddFriendModal">Назад</button>
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
</template>

<script setup>
import { useEventsStore } from '../stores/eventsStore'
import { computed, onMounted, ref } from 'vue'
import { useGroupsStore } from '../stores/groupsStore'
import { getGroupDetail } from '../api-frontend/groups'
import { searchUsers } from '../api-frontend/user'
import { API_BASE_URL } from '../config';

const groupsStore = useGroupsStore()
const eventsStore = useEventsStore()
const showEvents = ref(true)
const showFriends = ref(false)
const showGroups = ref(false)
const currentUser = computed(() => eventsStore.userProfile)
const showGroupInfoModal = ref(false)
const showInviteModal = ref(false)
const showVotingModal = ref(false)
const showGroupScheduleModal = ref(false)
const selectedGroup = ref(null)
const inviteUsername = ref('')
const selectedDraft = ref(null)
const showVoteModal = ref(false)
const showSlotsModal = ref(false)
const voteSlots = ref([])
const groupSchedule = ref([])
const showAddModal = ref(false)
const showAddFriendModal = ref(false)
const friendSearchQuery = ref('')

const getGroupAvatarUrl = (group) => {
  return group.avatar_url
    ? `${API_BASE_URL}${group.avatar_url}`
    : '';
}

const openAddModal = () => {
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
}

const openAddFriend = () => {
  showAddModal.value = false
  showAddFriendModal.value = true
}

const closeAddFriendModal = () => {
  showAddFriendModal.value = false
}

const sendFriendRequest = async () => {
  const query = friendSearchQuery.value.trim()
  if (!query) {
    alert('Введите имя пользователя или email')
    return
  }

  try {
    const token = localStorage.getItem('token')
    const results = await searchUsers(token, query)

    if (!results.length) {
      alert('Пользователь не найден')
      return
    }

    const user = results[0]

    await eventsStore.sendFriendRequest(user.id)
    alert(`Запрос дружбы отправлен пользователю ${user.name}`)
    closeAddFriendModal()
    friendSearchQuery.value = ''
  } catch (err) {
    console.error('Ошибка при отправке запроса:', err)
    alert('Ошибка при отправке запроса: ' + JSON.stringify(err))
  }
}

const addSlot = () => {
  voteSlots.value.push({ start: '', end: '' })
}

const removeSlot = (index) => {
  voteSlots.value.splice(index, 1)
}

const submitVoteWithSlots = async () => {
  try {
    const slotsData = voteSlots.value.map(slot => ({
      start: `${selectedDraft.value.date.split('T')[0]}T${slot.start}`,
      end: `${selectedDraft.value.date.split('T')[0]}T${slot.end}`
    }))
    await eventsStore.voteForDraft(selectedDraft.value.id, {
      consent: true,
      slots: slotsData
    })

    alert("Ваш голос учтён")
    showSlotsModal.value = false
  } catch (err) {
    alert("Ошибка: " + err.message)
  }
}

const voteYes = () => {
  showVoteModal.value = false
  showSlotsModal.value = true
  voteSlots.value = [{ start: '', end: '' }]  // начальный слот
}

const voteNo = async () => {
  try {
    await eventsStore.voteForDraft(selectedDraft.value.id, { consent: false })
    alert("Ваш голос ПРОТИВ учтён")
    showVoteModal.value = false
  } catch (err) {
    alert("Ошибка: " + err.message)
  }
}

const openGroupInfo = async (group) => {
  const token = localStorage.getItem('token')
  const detailedGroup = await groupsStore.fetchGroupDetail(group.id)
  selectedGroup.value = groupsStore.groupDetails
  showGroupInfoModal.value = true
}

const openInvite = (group) => {
  selectedGroup.value = group
  showInviteModal.value = true
}

const openVoting = async (group) => {
  selectedGroup.value = group
  await groupsStore.fetchGroupDetail(group.id)  // чтобы получить актуальные голосования
  showVotingModal.value = true
}

const openSchedule = async (group) => {
  try {
    selectedGroup.value = group
    groupSchedule.value = await groupsStore.fetchGroupSchedule(group.id)
    showGroupScheduleModal.value = true
  } catch (err) {
    alert('Ошибка загрузки расписания: ' + err.message)
  }
}

const openDraftVote = (draft) => {
  selectedDraft.value = draft
  console.log('CHECK', draft, selectedDraft.value)
  const userId = currentUser.value?.id
  const consent = draft.consents?.find(c => c.user_id === userId)

  if (draft.created_by === userId) {
    alert("Вы создали этот черновик, ждите завершения голосования")
  } else if (consent && consent.consent) {
    alert("Вы уже проголосовали, ждите завершения голосования")
  } else {
    showVoteModal.value = true
  }
}

const sendInvite = async () => {
  const query = inviteUsername.value.trim()
  if (!query) {
    alert('Введите имя пользователя или email')
    return
  }

  try {
    const token = localStorage.getItem('token')
    const results = await searchUsers(token, query)

    if (!results.length) {
      alert('Пользователь не найден')
      return
    }

    const user = results[0] // Берём первого из найденных

    await groupsStore.inviteUser(selectedGroup.value.id, user.id)

    alert(`Приглашение отправлено пользователю ${user.name}`)
    showInviteModal.value = false
    inviteUsername.value = ''
  } catch (err) {
    alert('Ошибка при отправке приглашения: ' + err.message)
  }
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
    showGroups.value = false
  }
}

const loadEvents = async () => {
  if (showEvents.value) {
    showEvents.value = false // Скрываем список, если он уже показан
  } else {
    await eventsStore.fetchUserEvents()
    showEvents.value = true // Показываем, если был скрыт
    showFriends.value = false
    showGroups.value = false
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
  eventsStore.fetchUserProfile()
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
  height: 30px;
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

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
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

.modal-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
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

.modal-my {
  width: 100%;
  background-color: #2a7ae2
}

.all-btn {
  background-color: black;
}

.avatarka img {
  border-radius: 50%;
  object-fit: cover;
}

@media (max-width: 768px) {
  .container {
    padding: 0.5rem;
  }

  .views {
    flex-direction: column;
    gap: 0.5rem;
  }

  .holder-choice {
    flex-direction: column;
    max-height: none;
    padding: 0.5rem;
  }

  .choice-friend {
    padding: 1rem 0.5rem;
  }

  .comm-btn {
    min-width: auto;
    width: 100%;
  }

  .calendary {
    height: auto;
    max-height: none;
    overflow-y: visible;
  }

  .event-card,
  .friend-card,
  .group-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .event-actions,
  .group-actions {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .event-info {
    font-size: 0.9rem;
  }

  .event-title {
    font-size: 1rem;
  }

  #add-event-button {
    position: fixed;
    bottom: 10px;
    right: 10px;
    top: auto;
    z-index: 1000;
  }

  .modal-content {
    padding: 1rem;
    width: 90%;
  }

  footer .footer-content {
    flex-direction: column;
    gap: 0.5rem;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .comm-btn {
    font-size: 0.8rem;
    padding: 0.4rem;
  }

  .event-title {
    font-size: 0.9rem;
  }

  .event-inline {
    font-size: 0.75rem;
  }

  .friend-info {
    font-size: 0.9rem;
  }

  .modal-content {
    width: 95%;
  }

  .modal-buttons {
    gap: 0.5rem;
  }

  .close-btn,
  .modal-my {
    width: 100%;
    font-size: 0.85rem;
  }

  .group-info {
    font-size: 0.95rem;
  }

  .group-actions button {
    font-size: 0.75rem;
    height: auto;
    padding: 4px 6px;
  }

  .avatarka img {
    width: 40px;
    height: 40px;
  }
}


</style>