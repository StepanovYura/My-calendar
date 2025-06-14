import { defineStore } from 'pinia'
import { getFriendList } from '../api-frontend/friends'

export const useFriendsStore = defineStore('friends', {
  state: () => ({
    friends: [],
    error: null
  }),
  actions: {
    async fetchFriends() {
      try {
        const authStore = useAuthStore()
        const token = authStore.token
        const data = await getFriendList(token)
        this.friends = data.friends
        this.error = null
      } catch (err) {
        this.error = err.message || 'Ошибка загрузки друзей'
      }
    }
  }
})
