'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Menu, X, MapPin, Calendar, User } from 'lucide-react'
import { AuthModals } from './auth-modals'
import { UserMenu } from './user-menu'
import { useAuth } from '@/contexts/AuthContext'

export default function Layout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const { user, isLoading } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-200">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white bg-opacity-30 backdrop-blur-md">
        <nav className="container mx-auto px-4 py-2">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold text-gray-800">TravelGuide</Link>
            <div className="hidden md:flex items-center space-x-6">
              <Link href="/destinations" className="flex items-center text-gray-800 hover:text-gray-600 px-3 py-1">
                <MapPin className="w-5 h-5 mr-1" />
                Destinations
              </Link>
              {user && (
              <Link href="/planner" className="flex items-center text-gray-800 hover:text-gray-600 px-3 py-1">
                <Calendar className="w-5 h-5 mr-1" />
                Trip Planner
              </Link>
              )}
              <div className="flex items-center text-gray-800 hover:text-gray-600 px-3 py-1">
                {!isLoading && (
                  user ? <UserMenu /> : <AuthModals />
                )}
              </div>
            </div>
            <div className="md:hidden">
              <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="text-gray-800">
                {isSidebarOpen ? <X /> : <Menu />}
              </button>
            </div>
          </div>
        </nav>
      </header>

      {/* Mobile Sidebar */}
      {isSidebarOpen && (
        <div className="fixed inset-0 z-40 bg-white bg-opacity-30 backdrop-blur-md md:hidden">
          <div className="flex flex-col items-center justify-center h-full space-y-8">
            <Link href="/destinations" className="flex items-center text-gray-800 hover:text-gray-600 px-3 py-1" onClick={() => setIsSidebarOpen(false)}>
              <MapPin className="w-5 h-5 mr-1" />
              Destinations
            </Link>
            <Link href="/planner" className="flex items-center text-gray-800 hover:text-gray-600 px-3 py-1" onClick={() => setIsSidebarOpen(false)}>
              <Calendar className="w-5 h-5 mr-1" />
              Trip Planner
            </Link>
            {!user && (
              <Link href="/user" className="flex items-center text-gray-800 hover:text-gray-600 px-3 py-1" onClick={() => setIsSidebarOpen(false)}>
                <User className="w-5 h-5 mr-1" />
                My Account
              </Link>
            )}
            <div className="flex items-center text-gray-800 hover:text-gray-600 px-3 py-1">
              {!isLoading && (
                user ? <UserMenu /> : <AuthModals />
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="pt-16">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white bg-opacity-30 backdrop-blur-md text-gray-800 p-4 text-center">
        <p>&copy; 2024 TravelGuide. All rights reserved.</p>
      </footer>
    </div>
  )
}

