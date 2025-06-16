<template>
  <div class="notification"></div>
  <main class="container">
    <div class="views">
      <div class="choice-friend">
        <div class="avatarka">
          <img :src="userProfile.avatar_url || defaultAvatar" alt="avatar" id="avatar" width="100" height="100" />
        </div>
        <div class="nick">{{ userProfile.name }}</div>
        <button type="button" class="settings-btn" @click="openSettings">
          Редактирование профиля
        </button>
      </div>

      <div class="calendary">
        <h3>Шутка дня</h3>
        <p class="joke-text">{{ currentJoke }}</p>
      </div>
    </div>

    <!-- Модалка настроек профиля -->
    <div v-if="showSettingsModal" class="modal-overlay" @click.self="closeSettings">
      <div class="modal-content">
        <h3>Редактирование профиля</h3>

        <div class="form-group">
          <label for="editName">Новый никнейм</label>
          <input type="text" id="editName" v-model="editName" placeholder="Новый никнейм" />
        </div>

        <div class="form-group">
          <label for="newPrivacy">Настройки приватности</label>
          <select id="newPrivacy" v-model="newPrivacy">
            <option value="all">Все видят расписание</option>
            <option value="none">Никто не видит расписание</option>
          </select>
        </div>

        <div class="form-group">
          <label for="avatarUpload">Новая аватарка</label>
          <input type="file" id="avatarUpload" @change="onAvatarChange" />
        </div>
        
        <div class="form-group">
          <RouterLink to="/changePswd" class="password-change-btn">Сменить пароль</RouterLink>
        </div>
        <div class="modal-buttons">
          <button class="save-btn" @click="submitProfileUpdate">Сохранить</button>
          <button class="cancel-btn" @click="closeSettings">Отмена</button>
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { fetchUserProfile, updateUserProfile } from '../api-frontend/user'

const authStore = useAuthStore()
const userProfile = ref({})
const defaultAvatar = '/default-avatar.png'  // путь к дефолтной аватарке

const showSettingsModal = ref(false)
const editName = ref('')
const newPassword = ref('')
const newPrivacy = ref('all')
const newAvatarFile = ref(null)

const jokes = [
  "Почему программисты путают Хэллоуин и Рождество? Потому что OCT 31 == DEC 25.",
  "В чём разница между программистом и пользователем? Программист говорит: «Это не баг, это фича».",
  "99 маленьких багов в коде, 99 багов в коде... Поправил один, 127 багов в коде.",
  "Как программисты поздравляют друг друга? С Новым Release’ом!",
  "Поставил задачу на завтра. На всякий случай открыл пиво сегодня.",
  "Почему Java-разработчики носят очки? Потому что они не C#.",
  "Хороший код как шутка — не нужно объяснять.",
  "Frontend без багов как единорог — говорят, существует, но никто не видел.",
  "Git commit — лучший дневник программиста.",
  "«Работает? Не трогай!» — главный закон IT.",
  "Программисты спят, когда идёт билд.",
  "Не злите программиста: он может удалить production одной строкой.",
  "Алгоритмы — это способ решить проблему, которую вы даже не знали, что имеете.",
  "Сломалось? Перезапусти. Почти всегда помогает.",
  "Программист написал тесты. Тесты не прошли. Программист уволился.",
  "Как программисты называют обед? Перерыв на компиляцию.",
  "Любой проект можно закончить вовремя. Нужно только начать его позже.",
  "Есть два типа программистов: те, кто делает бэкапы, и те, кто будет делать бэкапы.",
  "Почему программисты не любят природу? В ней слишком много багов.",
  "Мир делится на тех, кто понимает двоичную систему, и тех, кто нет.",
  "Почему программисты любят тёмную тему? Потому что светлая вызывает баги.",
  "Ctrl+C, Ctrl+V — суперспособность современного программиста.",
  "Работа программиста: 10% — писать код, 90% — гуглить.",
  "Почему разработчики не плачут? Потому что в console.log нет эмоций.",
  "«Сейчас всё поправлю» — сказал программист и ушёл в отпуск.",
  "Commit early, commit often, commit nonsense.",
  "Никогда не бойся удалить что-то ненужное. Git всё запомнит.",
  "Debugging — это как быть детективом в запутанном фильме, где ты же его и написал.",
  "Рабочее место программиста: компьютер, кофе, отчаяние.",
  "Пишу код с комментариями. Комментарии потом удалю, чтобы было загадочнее.",
  "Почему твой проект не запущен? — Потому что билд идёт.",
  "Программисты не ругаются, они просто называют переменные.",
  "Почему код никогда не бывает идеальным? Потому что всегда можно его улучшить... и сломать.",
  "if (пятница) { deploy(); } // лучший план.",
  "Хуже багов могут быть только баги в пятницу вечером.",
  "На собеседовании: — Ваш самый большой успех? — Мой код с первого раза заработал.",
  "Почему программисты любят кошек? Потому что они тоже не реагируют на команды.",
  "Код — это как поэзия. Только без рифмы. И с багами.",
  "Если код не работает, добавь комментарий // todo fix later",
  "Пишу код как художник. Никто не понимает, но красиво.",
  "Что такое хороший код? — Тот, который не приходится читать.",
  "Есть два состояния кода: «ещё не работает» и «уже не работает».",
  "Зачем нужны тесты? Чтобы понять, насколько плохо написан код.",
  "Программист — это человек, который находит проблему там, где её не было, и решает её так, что никто больше не разберётся.",
  "Почему программисты любят понедельники? Потому что никто не трогает на выходных production.",
  "Программист без багов — как понедельник без кофе.",
  "Junior: «Почему мой код не работает?» Senior: «Почему он вообще работает?»",
  "Программирование — это как готовка: если что-то не получается, добавь больше соли... ой, логов.",
  "Только программист понимает, что значит «работает на моей машине».",
  "Мечта программиста — писать код, который не нужно поддерживать. Реальность — багфиксы по ночам."
]

const currentJoke = computed(() => {
  const day = new Date().getDate()
  const randomIndex = (day + jokes.length * Math.random()) % jokes.length
  return jokes[Math.floor(randomIndex)]
})

async function loadProfile() {
  userProfile.value = await fetchUserProfile(authStore.token)
  editName.value = userProfile.value.name
  newPrivacy.value = userProfile.value.privacy_setting
}

function openSettings() {
  showSettingsModal.value = true
}

function closeSettings() {
  showSettingsModal.value = false
}

function onAvatarChange(event) {
  newAvatarFile.value = event.target.files[0]
}

async function submitProfileUpdate() {
  const formData = new FormData()
  formData.append('name', editName.value)
  formData.append('privacy_setting', newPrivacy.value)
  if (newPassword.value) {
    formData.append('password', newPassword.value)
  }
  if (newAvatarFile.value) {
    formData.append('avatar', newAvatarFile.value)
  }

  await updateUserProfile(authStore.token, formData)
  alert('Профиль обновлен')
  closeSettings()
  await loadProfile()
}

onMounted(() => {
  loadProfile()
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
    /* box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3); */
    gap: 5px;

}

.match-btn {
  color: #333;
  background-color: rgb(207, 43, 43);
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
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
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
    flex: 3;

    background-color: white;
    border-radius: 4px;
    /* box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3); */
    padding-left: 20px;
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

.avatarka img {
  border-radius: 50%;
  object-fit: cover;
}

.joke-text {
  font-style: italic;
  margin-top: 1rem;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
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

.settings-btn {
    background-color: blue;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
}

.form-group {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.3rem;
  font-weight: bold;
}

.modal-buttons button,
.password-change-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  justify-content: center;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}

.password-change-btn {
  background-color: #2196F3;
  color: white;
}


</style>