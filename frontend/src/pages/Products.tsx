import React, { useEffect, useState } from 'react'
import ProductCard from '../components/ProductCard'
import { getProducts, ProductListResponse, ProductsQuery } from '../services/api'
import { showError } from '../utils/toast'

const Products: React.FC = () => {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize] = useState(8)
  const [loading, setLoading] = useState(false)
  const [items, setItems] = useState<ProductListResponse | null>(null)

  const fetchProducts = async (query: ProductsQuery) => {
    setLoading(true)
    try {
      const data = await getProducts(query)
      setItems(data)
    } catch (error) {
      showError('Unable to load products.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts({ search, page, page_size: pageSize })
  }, [search, page, pageSize])

  const pageCount = Math.ceil((items?.total ?? 0) / pageSize)

  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Products</h1>
        <input
          placeholder="Search products"
          value={search}
          onChange={(event) => {
            setPage(1)
            setSearch(event.target.value)
          }}
          className="rounded-md border border-slate-200 p-2 focus:border-slate-400 focus:outline-none"
        />
      </header>
      {loading && <p className="text-sm text-slate-500">Loading products...</p>}
      {!loading && items && items.data.length === 0 && (
        <p className="rounded-md border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-500">
          No products match your search yet.
        </p>
      )}
      {!loading && items && items.data.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {items.data.map((product) => (
            <ProductCard key={product.id} {...product} />
          ))}
        </div>
      )}
      {items && pageCount > 1 && (
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
            disabled={page === 1}
            className="rounded-md border border-slate-200 px-3 py-1 text-sm"
          >
            Previous
          </button>
          <span className="text-sm text-slate-600">
            Page {page} of {pageCount}
          </span>
          <button
            onClick={() => setPage((prev) => Math.min(prev + 1, pageCount))}
            disabled={page === pageCount}
            className="rounded-md border border-slate-200 px-3 py-1 text-sm"
          >
            Next
          </button>
        </div>
      )}
    </section>
  )
}

export default Products
