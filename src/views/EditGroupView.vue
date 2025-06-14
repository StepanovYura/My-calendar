<template>
  <div class="create-event-page">
    <h2>Редактирование группы</h2>
    <form @submit.prevent="submitGroupEdit" enctype="multipart/form-data">
      <label>Название:</label>
      <input v-model="form.name" type="text" required />

      <label>Описание:</label>
      <textarea v-model="form.description" rows="4" />

      <label>Аватарка:</label>
      <input type="file" @change="handleFileUpload" accept="image/*" />

      <div class="buttons">
        <button type="submit">Сохранить изменения</button>
        <button type="button" @click="router.back()">Назад</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { getGroupDetail, editGroup } from '../api-frontend/groups'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const groupId = parseInt(route.params.groupId)
const form = ref({
  name: '',
  description: '',
})
const file = ref(null)

const handleFileUpload = (e) => {
  file.value = e.target.files[0]
}

onMounted(async () => {
    await authStore.checkAuth()
    console.log('authStore.user after checkAuth:', authStore.user)
    const token = authStore.token
    const group = await getGroupDetail(token, groupId)
    // if (group.created_by !== authStore.user.id) {
    //     alert('Вы не можете редактировать эту группу')
    //     router.back()
    // }
    form.value.name = group.name
    form.value.description = group.description
})

const submitGroupEdit = async () => {
  const token = authStore.token
  const formData = new FormData()
  formData.append('name', form.value.name)
  formData.append('description', form.value.description)
  if (file.value) {
    formData.append('avatar', file.value)
  }

  await editGroup(token, groupId, formData)
//   alert('Группа обновлена')
  router.back()
}
</script>

<style scoped>

.create-event-page {
  max-width: 500px;
  margin: 40px auto;
  padding: 20px;
  background: white;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  margin-top: 1rem;
  margin-bottom: 0.3rem;
}

input,
textarea {
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

button {
  margin-top: 1rem;
  padding: 0.7rem;
  background-color: #2a7ae2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.slot-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.buttons {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

</style>
