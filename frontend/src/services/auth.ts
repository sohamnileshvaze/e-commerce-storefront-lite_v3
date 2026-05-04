import api from './api'

interface Credentials {
  username: string
  password: string
}

interface SignupData {
  name: string
  email: string
  password: string
}

const TOKEN_KEY = 'access_token'

export const storeToken = (token: string) => {
  localStorage.setItem(TOKEN_KEY, token)
  api.defaults.headers.common.Authorization = `Bearer ${token}`
}

export const getToken = () => localStorage.getItem(TOKEN_KEY)

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY)
  delete api.defaults.headers.common.Authorization
}

export const signup = async (data: SignupData) => {
  const response = await api.post('/auth/signup', data)
  return response.data
}

export const login = async (credentials: Credentials) => {
  const response = await api.post('/auth/login', credentials)
  const token = response.data?.access_token
  if (!token) {
    throw new Error('Missing token in login response')
  }
  storeToken(token)
}
