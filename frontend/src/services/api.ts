import axios from 'axios'
import { getToken } from './auth'

const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface ProductsQuery {
  search?: string
  category?: string
  min_price?: number
  max_price?: number
  sort_by?: string
  page?: number
  page_size?: number
}

export interface Product {
  id: string
  name: string
  description: string
  price: number
}

export interface ProductListResponse {
  data: Product[]
  page: number
  page_size: number
  total: number
}

export interface Order {
  id: string
  status: string
  total: number
  placed_at: string
}

export interface OrdersResponse {
  data: Order[]
  page: number
  page_size: number
  total: number
}

export const getProducts = async (params: ProductsQuery) => {
  const response = await api.get<ProductListResponse>('/products', { params })
  return response.data
}

export const getProduct = async (id: string) => {
  const response = await api.get<Product>(`/products/${id}`)
  return response.data
}

export const getOrders = async (page: number, page_size: number) => {
  const response = await api.get<OrdersResponse>('/orders', { params: { page, page_size } })
  return response.data
}

export const getOrder = async (id: string) => {
  const response = await api.get(`/orders/${id}`)
  return response.data
}

export const getDashboardSummary = async () => {
  const response = await api.get('/dashboard')
  return response.data
}

export default api
