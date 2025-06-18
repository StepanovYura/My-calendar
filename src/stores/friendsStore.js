import { defineStore } from 'pinia'
import { getFriendList } from '../api-frontend/friends'
import { useAuthStore } from './authStore'

export const useFriendsStore = defineStore('friends', {
  state: () => ({
    friends: [],
    error: null
  }),
  actions: {
    async fetchFriends() {
      console.log('fetchFriends вызван')
      try {
        const authStore = useAuthStore()
        const token = authStore.token
        console.log('fetchFriends2 вызван')
        console.log('Токен: ', authStore.token)
        const data = await getFriendList(token)
        this.friends = data.friends
        console.log('CheckDATA: ', data, data.friends)
        this.error = null
      } catch (err) {
        this.error = err.message || 'Ошибка загрузки друзей'
      }
    }
  }
})
