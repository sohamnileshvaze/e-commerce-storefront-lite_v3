import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getProduct, Product } from '../services/api'
import { showError } from '../utils/toast'

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!id) {
      navigate('/products')
      return
    }

    const fetchProduct = async () => {
      setLoading(true)
      try {
        const data = await getProduct(id)
        setProduct(data)
      } catch (error) {
        showError('Unable to load product details.')
        navigate('/products')
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [id, navigate])

  if (loading || !product) {
    return <p className="text-sm text-slate-500">Loading product...</p>
  }

  return (
    <section className="space-y-4 rounded-lg bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold text-slate-900">{product.name}</h1>
      <p className="text-slate-600">{product.description}</p>
      <p className="text-lg font-semibold text-slate-900">${product.price.toFixed(2)}</p>
    </section>
  )
}

export default ProductDetail
