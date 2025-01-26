'use client'

import Layout from '../components/layout'
import Image from 'next/image'
import { Settings, MapPin, Heart } from 'lucide-react'
import { useAuth } from "@/contexts/AuthContext"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default function UserCenter() {
  const { user } = useAuth();
  if (!user) {
    return null;
  }

  const trips = [
    { id: 1, name: 'Summer in Paris', date: '2024-07-15' },
    { id: 2, name: 'Tokyo Adventure', date: '2024-09-22' },
  ]

  const favorites = [
    { id: 1, name: 'Bali', image: '/placeholder.svg?height=100&width=100' },
    { id: 2, name: 'New York', image: '/placeholder.svg?height=100&width=100' },
    { id: 3, name: 'Rome', image: '/placeholder.svg?height=100&width=100' },
  ]

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">User Center</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* User Profile */}
          <div className="md:col-span-2">
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6 mb-8">
              <div className="flex items-center mb-4">
                <Avatar className="w-16 h-16 hover:ring-2 hover:ring-blue-500 transition-all mr-4">
                  <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`} />
                  <AvatarFallback>{user.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                </Avatar>
                <div>
                  <h2 className="text-2xl font-semibold text-gray-800">{user.username}</h2>
                  <p className="text-gray-600">{user.email}</p>
                </div>
              </div>
              <button className="flex items-center justify-center px-4 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition duration-300">
                <Settings className="mr-2" size={20} />
                Edit Profile
              </button>
            </div>

            {/* My Trips */}
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6 mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">My Trips</h2>
              <ul className="space-y-4">
                {trips.map((trip) => (
                  <li key={trip.id} className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium text-gray-800">{trip.name}</h3>
                      <p className="text-gray-600">{trip.date}</p>
                    </div>
                    <button className="text-blue-400 hover:text-blue-300">View</button>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Favorites */}
          <div>
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Favorite Destinations</h2>
              <ul className="space-y-4">
                {favorites.map((fav) => (
                  <li key={fav.id} className="flex items-center">
                    <Image src={fav.image} alt={fav.name} width={50} height={50} className="rounded-full mr-3" />
                    <span className="text-white">{fav.name}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

