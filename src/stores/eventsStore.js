import { defineStore } from 'pinia'
import {
  getUserEvents,
  deleteEvent as apiDeleteEvent,
  createEvent as apiCreateEvent,
  updateEvent as apiUpdateEvent
} from '../api-frontend/events'
import { getFriendList } from '../api-frontend/friends'
import { useAuthStore } from './authStore'

export const useEventsStore = defineStore('events', {
  state: () => ({
    events: [],
    friends: [],
    selectedFriend: null,
    isLoading: false,
    error: null
  }),

  actions: {
    async fetchEvents(filters = {}) {
      try {
        this.isLoading = true
        const authStore = useAuthStore()
        const token = authStore.token
        if (!authStore.token || authStore.token == 'null') {
          console.error('Токен отсутствует!');
          return []; // Возвращаем пустой массив если не авторизован
        }
        const result = []

        // Сначала получаем СВОИ события
        const ownEvents = await getUserEvents(token)
        // Проверяем, что это массив
        if (!Array.isArray(ownEvents)) {
          throw new Error('Сервер вернул некорректные данные');
        }
        result.push(...ownEvents)

        // Если выбран друг — пробуем получить и его события
        if (this.selectedFriend) {
          try {
            const friendEvents = await getUserEvents(token, { user_id: this.selectedFriend.id })
            result.push(...friendEvents.map(ev => ({ ...ev, _isFriend: true })))
          } catch (err) {
            // Обработка отказа в доступе к событиям друга
            if (err.message.includes('доступ') || err.message.includes('не можете просматривать')) {
              this.error = `Пользователь ${this.selectedFriend.name} ограничил доступ к своим событиям.`
            } else {
              this.error = `Ошибка загрузки событий друга: ${err.message}`
            }

            // Показываем только свои события
            this.selectedFriend = null
          }
        }

        this.events = result
      } catch (err) {
        throw new Error(err.message || 'Не удалось загрузить события')
      } finally {
        this.isLoading = false
      }
    },

    async fetchFriends() {
      try {
        this.isLoading = true
        const authStore = useAuthStore()
        const token = authStore.token

        const response = await getFriendList(token)
        this.friends = response.friends || []
        this.error = null
      } catch (err) {
        throw new Error(err.message || 'Ошибка загрузки друзей')
      } finally {
        this.isLoading = false
      }
    },

    async deleteEvent(eventId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await apiDeleteEvent(token, eventId)
        this.events = this.events.filter(e => e.id !== eventId)
      } catch (err) {
        throw new Error(err.message || 'Ошибка удаления события')
      }
    },

    async createEvent(eventData) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        const newEvent = await apiCreateEvent(token, eventData)
        this.events.push(newEvent)
      } catch (err) {
        throw new Error(err.message || 'Ошибка создания события')
      }
    },

    async updateEvent(eventId, updatedData) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        const updated = await apiUpdateEvent(token, eventId, updatedData)
        const index = this.events.findIndex(e => e.id === eventId)
        if (index !== -1) this.events[index] = updated
      } catch (err) {
        throw new Error(err.message || 'Ошибка обновления события')
      }
    },

    selectFriend(friend) {
      // Если друг уже выбран — сбрасываем фильтр
      if (this.selectedFriend && this.selectedFriend.id === friend.id) {
        this.clearFriendSelection()
      } else {
        this.selectedFriend = friend
        this.fetchEvents()
      }
    },

    clearFriendSelection() {
      this.selectedFriend = null
      this.fetchEvents()
    }
  },

  getters: {
    eventsForDay: (state) => (day) => {
      const dayStr = new Date(day).toDateString()
      console.log('События для дня 1:', day, state.events.filter(e =>
        new Date(e.date_time).toDateString() === dayStr
      )); 
      console.log('все события: ', state.events);
      return state.events.filter(e =>
        new Date(e.date_time).toDateString() === dayStr
      )
    },
    hasFriends: (state) => state.friends.length > 0,
    selectedFriendName: (state) => state.selectedFriend?.name || null
  }
})
