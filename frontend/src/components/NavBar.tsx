import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { logout, getToken } from '../services/auth'

const NavBar: React.FC = () => {
  const navigate = useNavigate()
  const token = getToken()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `transition-colors px-3 py-2 rounded-md ${isActive ? 'bg-slate-100 text-slate-900' : 'text-slate-700 hover:bg-slate-100'}`

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
        <div className="text-xl font-semibold text-slate-900">Storefront Lite</div>
        <nav className="flex items-center gap-2">
          <NavLink to="/" className={linkClass}>
            Home
          </NavLink>
          <NavLink to="/products" className={linkClass}>
            Products
          </NavLink>
          <NavLink to="/orders" className={linkClass}>
            Orders
          </NavLink>
          <NavLink to="/profile" className={linkClass}>
            Profile
          </NavLink>
          {!token ? (
            <>
              <NavLink to="/login" className={linkClass}>
                Login
              </NavLink>
              <NavLink to="/signup" className={linkClass}>
                Signup
              </NavLink>
            </>
          ) : (
            <button
              onClick={handleLogout}
              className="px-3 py-2 rounded-md text-sm font-medium text-slate-700 hover:bg-slate-100"
              aria-label="Logout"
            >
              Logout
            </button>
          )}
        </nav>
      </div>
    </header>
  )
}

export default NavBar
