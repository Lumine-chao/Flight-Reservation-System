import { defineStore } from 'pinia'

import { clearCustomerAuth, loadCustomerAuth, saveCustomerAuth } from './token'

export const useUserStore = defineStore('user', {
  state: () => ({ auth: loadCustomerAuth() }),
  getters: {
    token: (s) => s.auth?.token || null,
    username: (s) => s.auth?.username || '',
  },
  actions: {
    setAuth(auth) {
      this.auth = auth
      saveCustomerAuth(auth)
    },
    logout() {
      this.auth = null
      clearCustomerAuth()
    },
  },
})
