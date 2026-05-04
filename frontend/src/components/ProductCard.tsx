import React from 'react'
import { Link } from 'react-router-dom'

export interface ProductCardProps {
  id: string
  name: string
  price: number
  description: string
}

const ProductCard: React.FC<ProductCardProps> = ({ id, name, price, description }) => (
  <Link
    to={`/products/${id}`}
    className="block rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-slate-400"
    aria-label={`View details for ${name}`}
  >
    <div className="text-lg font-semibold text-slate-900">{name}</div>
    <div className="mt-2 text-sm text-slate-500">{description}</div>
    <div className="mt-3 text-base font-semibold text-slate-900">${price.toFixed(2)}</div>
  </Link>
)

export default ProductCard
