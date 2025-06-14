<template>
  <div class="create-event-page">
    <h2>Создание черновика события</h2>
    <form @submit.prevent="submitDraft">
      <label>Название:</label>
      <input v-model="form.title" type="text" required />

      <label>Описание:</label>
      <textarea v-model="form.description" rows="4" />

      <label>Дата:</label>
      <input v-model="form.date" type="date" required />

      <label>Временные слоты:</label>
      <div v-for="(slot, index) in slots" :key="index" class="slot-row">
        <input type="time" v-model="slot.start" required />
        <span>—</span>
        <input type="time" v-model="slot.end" required />
        <button @click.prevent="removeSlot(index)">Удалить</button>
      </div>
      <button @click.prevent="addSlot" type="button">Добавить слот</button>

      <div class="buttons">
        <button type="submit">Создать черновик</button>
        <button type="button" @click="router.back()">Назад</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groupsStore'

const router = useRouter()
const route = useRoute()
const groupsStore = useGroupsStore()

const groupId = parseInt(route.params.groupId)

const form = ref({
  title: '',
  description: '',
  date: ''
})

const slots = ref([
  { start: '', end: '' }
])

const addSlot = () => {
  slots.value.push({ start: '', end: '' })
}

const removeSlot = (index) => {
  slots.value.splice(index, 1)
}

const submitDraft = async () => {
  try {
    const draftData = {
      title: form.value.title,
      description: form.value.description,
      group_id: groupId,
      date_time: `${form.value.date}T00:00:00`,
      slots: slots.value.map(slot => ({
        start: `${form.value.date}T${slot.start}`,
        end: `${form.value.date}T${slot.end}`
      }))
    }

    await groupsStore.createDraft(draftData)
    alert('Черновик успешно создан')
    router.back()
  } catch (err) {
    alert(err.message || 'Ошибка при создании черновика')
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
</style>
