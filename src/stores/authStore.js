import { defineStore } from 'pinia'
import { loginUser, registerUser, logoutUser, checkAuth } from '../api-frontend/auth'
import { changePassword } from '../api-frontend/user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: (() => {
      try {
        const item = localStorage.getItem('user');
        return item && item !== "undefined" ? JSON.parse(item) : null;
      } catch {
        return null;
      }
    })(),

    error: null,
    loading: false
  }),

  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await loginUser(credentials)
        this.token = response.token
        this.user = response.user
        localStorage.setItem('token', response.token)
        localStorage.setItem('user', JSON.stringify(response.user))
        return true
      } catch (error) {
        this.error = error.message || 'Ошибка авторизации'
        return false
      } finally {
        this.loading = false
      }
    },

    async register(userData) {
      this.loading = true
      this.error = null
      try {
        const response = await registerUser(userData)
        return true
      } catch (error) {
        this.error = error.message || 'Ошибка регистрации'
        return false
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        await logoutUser(this.token)
      } finally {
        this.token = null
        this.user = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    },

    async checkAuth() {
      if (!this.token) return false
      try {
        const response = await checkAuth(this.token)
        this.user = response.user
        localStorage.setItem('user', JSON.stringify(response.user))
        return true
      } catch {
        this.logout()
        return false
      }
    },

    async changePassword(passwordData) {
      this.loading = true
      this.error = null
      try {
        await changePassword({
          ...passwordData,
          token: this.token
        })
        return true
      } catch (error) {
        this.error = error.message || 'Ошибка смены пароля'
        return false
      } finally {
        this.loading = false
      }
    }
  }
})
