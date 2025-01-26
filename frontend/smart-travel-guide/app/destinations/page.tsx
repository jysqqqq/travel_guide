'use client'

import Layout from '../components/layout'
import Image from 'next/image'
import Link from 'next/link'
import { Search, Filter } from 'lucide-react'

export default function Destinations() {
  const destinations = [
    { id: 1, name: 'Paris', image: '/placeholder.svg?height=300&width=400', region: 'Europe', type: 'City', season: 'Spring' },
    { id: 2, name: 'Bali', image: '/placeholder.svg?height=300&width=400', region: 'Asia', type: 'Beach', season: 'Summer' },
    { id: 3, name: 'New York', image: '/placeholder.svg?height=300&width=400', region: 'North America', type: 'City', season: 'Fall' },
    { id: 4, name: 'Swiss Alps', image: '/placeholder.svg?height=300&width=400', region: 'Europe', type: 'Mountain', season: 'Winter' },
    { id: 5, name: 'Tokyo', image: '/placeholder.svg?height=300&width=400', region: 'Asia', type: 'City', season: 'Spring' },
    { id: 6, name: 'Maldives', image: '/placeholder.svg?height=300&width=400', region: 'Asia', type: 'Beach', season: 'Winter' },
  ]

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">Explore Destinations</h1>

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-grow relative">
            <input type="text" placeholder="Search destinations..." className="w-full py-2 px-4 pr-10 rounded-full bg-white/50 backdrop-blur-md text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white" />
          </div>
          <button className="flex items-center justify-center px-4 py-2 bg-white bg-opacity-30 backdrop-blur-md text-white rounded-full hover:bg-opacity-40 transition duration-300">
            <Filter className="mr-2" />
            Filters
          </button>
        </div>

        {/* Destinations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {destinations.map((dest) => (
            <Link href={`/destinations/${dest.id}`} key={dest.id} className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg overflow-hidden hover:shadow-lg transition duration-300">
              <Image src={dest.image} alt={dest.name} width={400} height={300} className="w-full h-48 object-cover" />
              <div className="p-4">
                <h2 className="text-xl font-semibold text-gray-800 mb-2">{dest.name}</h2>
                <p className="text-gray-600">{dest.region} • {dest.type} • Best in {dest.season}</p>
              </div>
            </Link>
          ))}
        </div>

        {/* Pagination */}
        <div className="flex justify-center mt-8">
          <button className="mx-1 px-4 py-2 bg-white bg-opacity-30 backdrop-blur-md text-white rounded-full hover:bg-opacity-40 transition duration-300">1</button>
          <button className="mx-1 px-4 py-2 bg-white bg-opacity-30 backdrop-blur-md text-white rounded-full hover:bg-opacity-40 transition duration-300">2</button>
          <button className="mx-1 px-4 py-2 bg-white bg-opacity-30 backdrop-blur-md text-white rounded-full hover:bg-opacity-40 transition duration-300">3</button>
        </div>
      </div>
    </Layout>
  )
}

