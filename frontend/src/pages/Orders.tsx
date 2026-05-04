import React, { useEffect, useState } from 'react'
import { getOrders, OrdersResponse, Order } from '../services/api'
import { showError } from '../utils/toast'

const Orders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(5)
  const [totalPages, setTotalPages] = useState(1)

  const fetchOrders = async (pageParam: number) => {
    setLoading(true)
    try {
      const data: OrdersResponse = await getOrders(pageParam, pageSize)
      setOrders(data.data)
      setTotalPages(Math.max(1, Math.ceil(data.total / data.page_size)))
    } catch (error) {
      showError('Unable to load orders.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrders(page)
  }, [page])

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Orders</h1>
      </header>
      {loading && <p className="text-sm text-slate-500">Loading orders...</p>}
      {!loading && orders.length === 0 && (
        <p className="rounded-md border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-500">
          No orders found yet.
        </p>
      )}
      {!loading && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-semibold text-slate-900">Order {order.id}</p>
                  <p className="text-sm text-slate-500">Placed {new Date(order.placed_at).toLocaleDateString()}</p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs uppercase tracking-wide text-slate-600">
                  {order.status}
                </span>
              </div>
              <p className="mt-2 text-slate-700">Total: ${order.total.toFixed(2)}</p>
            </div>
          ))}
        </div>
      )}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
          disabled={page === 1}
          className="rounded-md border border-slate-200 px-3 py-1 text-sm"
        >
          Previous
        </button>
        <span className="text-sm text-slate-600">
          Page {page} of {totalPages}
        </span>
        <button
          onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
          disabled={page === totalPages}
          className="rounded-md border border-slate-200 px-3 py-1 text-sm"
        >
          Next
        </button>
      </div>
    </section>
  )
}

export default Orders
