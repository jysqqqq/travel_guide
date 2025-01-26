'use client'

import Layout from '../../components/layout'
import Image from 'next/image'
import { MapPin, Sun, Cloud, Wind, Droplet } from 'lucide-react'

export default function DestinationDetail({ params }: { params: { id: string } }) {
  // 这里应该根据 params.id 获取实际的目的地数据
  const destination = {
    id: params.id,
    name: 'Paris',
    image: '/placeholder.svg?height=600&width=1200',
    description: 'Paris, the City of Light, is the capital city of France, and the largest city in France. The Paris Region had a GDP of €681 billion (US$850 billion) in 2016, accounting for 31 percent of the GDP of France. It has the largest concentration of multinational headquarters in Europe, and maintains its position as the world\'s leading tourist destination.',
    weather: { temp: 22, condition: 'Partly Cloudy', humidity: 60, windSpeed: 10 },
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">{destination.name}</h1>

        {/* Image Carousel (simplified for this example) */}
        <div className="mb-8 relative h-[50vh]">
          <Image src={destination.image} alt={destination.name} layout="fill" objectFit="cover" className="rounded-lg" />
        </div>

        {/* Destination Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6 mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">About {destination.name}</h2>
              <p className="text-gray-600">{destination.description}</p>
            </div>

            {/* Map Component (placeholder) */}
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6 mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Map</h2>
              <div className="h-64 bg-gray-300 rounded-lg flex items-center justify-center">
                <MapPin className="text-gray-500" size={48} />
              </div>
            </div>
          </div>

          <div>
            {/* Weather Info */}
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6 mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Weather</h2>
              <div className="flex items-center mb-4">
                <Sun className="text-yellow-400 mr-2" size={24} />
                <span className="text-gray-800 text-xl">{destination.weather.temp}°C</span>
              </div>
              <p className="text-gray-600">{destination.weather.condition}</p>
              <div className="flex items-center mt-2">
                <Droplet className="text-blue-400 mr-2" size={16} />
                <span className="text-gray-600">Humidity: {destination.weather.humidity}%</span>
              </div>
              <div className="flex items-center mt-2">
                <Wind className="text-gray-400 mr-2" size={16} />
                <span className="text-gray-600">Wind: {destination.weather.windSpeed} km/h</span>
              </div>
            </div>

            {/* Related Recommendations */}
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">You Might Also Like</h2>
              <ul className="space-y-4">
                <li>
                  <a href="#" className="flex items-center text-gray-800 hover:text-gray-300">
                    <Image src="/placeholder.svg?height=50&width=50" alt="London" width={50} height={50} className="rounded-full mr-3" />
                    <span>London, UK</span>
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center text-gray-800 hover:text-gray-300">
                    <Image src="/placeholder.svg?height=50&width=50" alt="Rome" width={50} height={50} className="rounded-full mr-3" />
                    <span>Rome, Italy</span>
                  </a>
                </li>
                <li>
                  <a href="#" className="flex items-center text-gray-800 hover:text-gray-300">
                    <Image src="/placeholder.svg?height=50&width=50" alt="Barcelona" width={50} height={50} className="rounded-full mr-3" />
                    <span>Barcelona, Spain</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

