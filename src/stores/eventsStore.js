import { defineStore } from 'pinia'
import {
  getUserEvents,
  deleteEvent as apiDeleteEvent,
  createEvent as apiCreateEvent,
  updateEvent as apiUpdateEvent,
  addParticipantToEvent as apiAddParticipantToEvent,
  getEventParticipants
} from '../api-frontend/events'
import { getFriendList, removeFriend as apiRemoveFriend } from '../api-frontend/friends'
import { useAuthStore } from './authStore'

export const useEventsStore = defineStore('events', {
  state: () => ({
    events: [],
    friends: [],
    selectedFriend: null,
    isLoading: false,
    error: null,
    participantsByEvent: {},
    userEvents: [],
    currentUsername: null,
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
    
    async fetchUserEvents() {
      try {
        const authStore = useAuthStore()
        const token = authStore.token
        const result = await getUserEvents(token)
        this.currentUsername = authStore.user?.username || null

        this.userEvents = result.sort((a, b) =>
          new Date(a.date_time) - new Date(b.date_time)
        )

        // Подгружаем участников для каждого события
        for (const event of this.userEvents) {
          await this.fetchEventParticipants(event.id)
        }
      } catch (error) {
        console.error('Ошибка при загрузке своих событий:', error)
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

    async fetchEventParticipants(eventId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token
        const participants = await getEventParticipants(token, eventId)

        // Сохраняем по eventId
        this.participantsByEvent[eventId] = participants
        this.error = null
      } catch (err) {
        this.error = `Ошибка загрузки участников события: ${err.message}`
        this.participantsByEvent[eventId] = []
      }
    },

    async deleteEvent(eventId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await apiDeleteEvent(token, eventId)
        this.events = this.events.filter(e => e.id !== eventId)
        await this.fetchEvents()
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
        await this.fetchEvents()
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
        await this.fetchEvents()
      } catch (err) {
        throw new Error(err.message || 'Ошибка обновления события')
      }
    },

    async addParticipantToEvent(eventId, username) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token
        await apiAddParticipantToEvent(token, eventId, username)
        await this.fetchEventParticipants(eventId)
      } catch (err) {
        throw new Error(err.message || 'Ошибка добавления участника')
      }
    },
    
    async removeFriend(friendId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await apiRemoveFriend(token, friendId)
        this.friends = this.friends.filter(f => f.id !== friendId)
      } catch (err) {
        this.error = err.message || 'Ошибка при удалении друга'
        throw err
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
      if (!day) return []

      const targetDate = new Date(day)
      //console.log("targetDate: ", targetDate)
      // console.log('state.events: ', state.events)
      return state.events.filter(e => {
        const eventDate = new Date(e.date_time) 
        //console.log("eventDate || targetDate : ", eventDate, targetDate, eventDate.getFullYear() === targetDate.getFullYear(), eventDate.getMonth() === targetDate.getMonth(), eventDate.getDate() === targetDate.getDate())
        console.log('state.events || result: ', state.events, eventDate.getFullYear() === targetDate.getFullYear() &&
              eventDate.getMonth() === targetDate.getMonth() &&
              eventDate.getDate() === targetDate.getDate())
        return (
          eventDate.getFullYear() === targetDate.getFullYear() &&
          eventDate.getMonth() === targetDate.getMonth() &&
          eventDate.getDate() === targetDate.getDate()
        )
      })
    },
    hasFriends: (state) => state.friends.length > 0,
    selectedFriendName: (state) => state.selectedFriend?.name || null,
    getParticipantsByEvent: (state) => (eventId) => {
      return state.participantsByEvent[eventId] || []
    }
  }
})
