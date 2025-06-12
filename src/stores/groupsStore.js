import { defineStore } from 'pinia'
import {
  getMyGroups,
  createGroup,
  deleteGroup,
  editGroup,
  getGroupDetail,
  joinGroup,
  leaveGroup,
  inviteToGroup
} from '../api-frontend/groups'

import { useAuthStore } from './authStore'

export const useGroupsStore = defineStore('groups', {
  state: () => ({
    groups: [],
    selectedGroup: null,
    groupDetails: null,
    isLoading: false,
    error: null
  }),

  actions: {
    async fetchGroups() {
      try {
        this.isLoading = true
        const authStore = useAuthStore()
        const token = authStore.token

        const result = await getMyGroups(token)
        this.groups = result
        this.error = null
      } catch (err) {
        this.error = err.message || 'Ошибка загрузки групп'
      } finally {
        this.isLoading = false
      }
    },

    async fetchGroupDetail(groupId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        this.groupDetails = await getGroupDetail(token, groupId)
        this.selectedGroup = groupId
        this.error = null
      } catch (err) {
        this.error = err.message || 'Ошибка загрузки информации о группе'
        this.groupDetails = null
      }
    },

    async createGroup(groupData) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await createGroup(token, groupData)
        await this.fetchGroups()
      } catch (err) {
        this.error = err.message || 'Ошибка при создании группы'
      }
    },

    async updateGroup(groupId, updatedData) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await editGroup(token, groupId, updatedData)
        await this.fetchGroups()
        await this.fetchGroupDetail(groupId)
      } catch (err) {
        this.error = err.message || 'Ошибка при редактировании группы'
      }
    },

    async deleteGroup(groupId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await deleteGroup(token, groupId)
        this.groups = this.groups.filter(group => group.id !== groupId)
        this.groupDetails = null
        this.selectedGroup = null
      } catch (err) {
        this.error = err.message || 'Ошибка при удалении группы'
      }
    },

    async joinGroup(groupId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await joinGroup(token, groupId)
        await this.fetchGroups()
      } catch (err) {
        this.error = err.message || 'Ошибка при вступлении в группу'
      }
    },

    async leaveGroup(groupId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await leaveGroup(token, groupId)
        await this.fetchGroups()
      } catch (err) {
        this.error = err.message || 'Ошибка при выходе из группы'
      }
    },

    async inviteUser(groupId, userId) {
      try {
        const authStore = useAuthStore()
        const token = authStore.token

        await inviteToGroup(token, groupId, userId)
      } catch (err) {
        this.error = err.message || 'Ошибка при приглашении в группу'
      }
    }
  },

  getters: {
    selectedGroupInfo: (state) => state.groupDetails,
    groupById: (state) => (id) => state.groups.find(g => g.id === id)
  }
})
