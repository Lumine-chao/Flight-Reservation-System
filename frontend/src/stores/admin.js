import { defineStore } from 'pinia'

import { clearAdminAuth, loadAdminAuth, saveAdminAuth } from './token'

export const useAdminStore = defineStore('admin', {
  state: () => ({ auth: loadAdminAuth() }),
  getters: {
    token: (s) => s.auth?.token || null,
    username: (s) => s.auth?.username || '',
    role: (s) => s.auth?.role || '',
  },
  actions: {
    setAuth(auth) {
      this.auth = auth
      saveAdminAuth(auth)
    },
    logout() {
      this.auth = null
      clearAdminAuth()
    },
  },
})
