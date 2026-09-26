import request from './request'

export const register = (data) => request.post('/users/register', data)
export const getMe = () => request.get('/users/me')

export const login = (data, silent = false) => request.post('/auth/login', data, { silent })
export const logout = () => request.post('/auth/logout')
export const getSecurityQuestion = (username) =>
  request.get('/auth/security-question', { params: { username }, silent: true })
export const resetPassword = (data) => request.post('/auth/reset-password', data, { silent: true })
