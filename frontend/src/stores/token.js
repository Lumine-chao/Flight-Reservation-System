const CUSTOMER_KEY = 'fr_customer_auth'
const ADMIN_KEY = 'fr_admin_auth'

function load(key) {
  try {
    return JSON.parse(localStorage.getItem(key))
  } catch {
    return null
  }
}

export const loadCustomerAuth = () => load(CUSTOMER_KEY)
export const saveCustomerAuth = (auth) => localStorage.setItem(CUSTOMER_KEY, JSON.stringify(auth))
export const clearCustomerAuth = () => localStorage.removeItem(CUSTOMER_KEY)

export const loadAdminAuth = () => load(ADMIN_KEY)
export const saveAdminAuth = (auth) => localStorage.setItem(ADMIN_KEY, JSON.stringify(auth))
export const clearAdminAuth = () => localStorage.removeItem(ADMIN_KEY)
