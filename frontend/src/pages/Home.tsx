import React from 'react'
import { Link } from 'react-router-dom'

const Home: React.FC = () => (
  <section className="space-y-6">
    <h1 className="text-3xl font-semibold text-slate-900">Welcome to Storefront Lite</h1>
    <p className="text-slate-600">
      Browse curated products, view status of your orders, or manage your profile. Authentication is required for
      orders and profile management.
    </p>
    <div className="flex gap-3">
      <Link
        to="/products"
        className="rounded-md bg-slate-900 px-4 py-2 text-white shadow-sm hover:bg-slate-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500"
      >
        Browse Products
      </Link>
      <Link
        to="/signup"
        className="rounded-md border border-slate-900 px-4 py-2 text-slate-900 hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500"
      >
        Create Account
      </Link>
    </div>
  </section>
)

export default Home
