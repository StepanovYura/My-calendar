<template>
  <main class="admin-container">
    <h2>Админка</h2>
    <p>Панель администратора: управление пользователями.</p>

    <div v-if="isLoading" class="spinner">Загрузка пользователей...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Email</th>
            <th>Приватность</th>
            <th>Роль</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>
              <input v-model="user.name" />
            </td>
            <td>
              <input v-model="user.email" />
            </td>
            <td>
              <select v-model="user.privacy_setting">
                <option value="all">all</option>
                <option value="none">none</option>
              </select>
            </td>
            <td>{{ user.role }}</td>
            <td>
              <button class="all-btn" @click="updateUser(user)">Сохранить</button>
              <button class="all-btn" @click="deleteUser(user.id)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { getAllUsers, updateUserByAdmin, deleteUserByAdmin } from '../api-frontend/admin'

const authStore = useAuthStore()
const users = ref([])
const isLoading = ref(false)
const error = ref(null)

onMounted(async () => {
  await loadUsers()
})

async function loadUsers() {
  isLoading.value = true
  error.value = null
  try {
    const data = await getAllUsers(authStore.token)
    users.value = data
  } catch (err) {
    error.value = err.message || 'Ошибка загрузки пользователей'
  } finally {
    isLoading.value = false
  }
}

const filteredUsers = computed(() => {
  return users.value.filter(user => user.role !== 'admin')
})

async function updateUser(user) {
  try {
    await updateUserByAdmin(authStore.token, user.id, {
      name: user.name,
      email: user.email,
      privacy_setting: user.privacy_setting
    })
    alert('Пользователь обновлён')
  } catch (err) {
    alert('Ошибка обновления: ' + (err.message || 'Не удалось обновить пользователя'))
  }
}

async function deleteUser(userId) {
  if (!confirm('Удалить пользователя?')) return
  try {
    await deleteUserByAdmin(authStore.token, userId)
    users.value = users.value.filter(u => u.id !== userId)
    alert('Пользователь удалён')
  } catch (err) {
    alert('Ошибка удаления: ' + (err.message || 'Не удалось удалить пользователя'))
  }
}
</script>

<style scoped>
.admin-container {
  padding: 1rem;
}

.spinner {
  font-weight: bold;
}

.error {
  color: red;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.admin-table th,
.admin-table td {
  border: 1px solid #ccc;
  padding: 0.5rem;
}

.admin-table input,
.admin-table select {
  width: 90%;
}

.admin-table button {
  margin-right: 0.25rem;
}

.all-btn {
  background-color: black;
}

@media (max-width: 768px) {
  .admin-table {
    font-size: 0.85rem;
  }

  .admin-table input,
  .admin-table select {
    width: 100%;
    font-size: 0.85rem;
  }

  .admin-table th,
  .admin-table td {
    padding: 0.3rem;
  }

  .admin-table button {
    font-size: 0.85rem;
    padding: 0.3rem 0.5rem;
  }
}

@media (max-width: 600px) {
  .admin-table thead {
    display: none;
  }

  .admin-table tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 0.5rem;
  }

  .admin-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 0;
    border: none;
    border-bottom: 1px solid #eee;
  }

  .admin-table td::before {
    content: attr(data-label);
    font-weight: bold;
    margin-right: 0.5rem;
    min-width: 90px;
    color: #555;
  }

  .admin-table td:last-child {
    border-bottom: none;
  }

  .admin-table input,
  .admin-table select {
    width: 60%;
  }

  .admin-table button {
    margin-top: 0.3rem;
  }
}


</style>

