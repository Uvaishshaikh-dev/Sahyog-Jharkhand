
import api from './api'

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/api/v1/auth/login', { email, password })
    return response.data
  },

  me: async () => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },

  register: async (payload) => {
    const response = await api.post('/api/v1/auth/register', payload)
    return response.data
  },

  logout: () => {
    localStorage.removeItem('sih_token')
    localStorage.removeItem('sih_user')
  },
}
