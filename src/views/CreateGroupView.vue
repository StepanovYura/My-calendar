<template>
  <div class="create-event-page">
    <h2>Создание группы</h2>
    <form @submit.prevent="submitGroup">
      <label>Название:</label>
      <input v-model="form.name" type="text" required />

      <label>Описание:</label>
      <textarea v-model="form.description" rows="4" />

      <label>Аватарка:</label>
      <input type="file" @change="handleFileUpload" accept="image/*" />

      <div class="buttons">
        <button type="submit">Создать группу</button>
        <button type="button" @click="router.back()">Назад</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groupsStore'

const router = useRouter()
const groupsStore = useGroupsStore()

const form = ref({
  name: '',
  description: ''
})
const file = ref(null)

const handleFileUpload = (e) => {
  file.value = e.target.files[0]
}

const submitGroup = async () => {
  try {
    const formData = new FormData()
    formData.append('name', form.value.name)
    formData.append('description', form.value.description)
    if (file.value.avatar) {
      formData.append('avatar', file.value.avatar)
    }

    await groupsStore.createGroup(formData)
    alert('Группа создана!')
    router.back()
  } catch (err) {
    alert(err.message || 'Ошибка при создании группы')
  }
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

@media (max-width: 768px) {
  .create-event-page {
    width: 90%;
    padding: 16px;
    margin: 20px auto;
  }

  input,
  textarea {
    font-size: 0.95rem;
    padding: 0.5rem;
  }

  button {
    font-size: 0.9rem;
    padding: 0.6rem;
  }

  .buttons {
    flex-direction: column;
    gap: 0.7rem;
  }
}

@media (max-width: 480px) {
  h2 {
    font-size: 1.2rem;
    text-align: center;
  }

  label {
    font-size: 0.95rem;
  }

  button {
    width: 100%;
  }

  .create-event-page {
    padding: 12px;
  }
}


</style>
