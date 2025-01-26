import Layout from './components/layout'
import Image from 'next/image'
import Link from 'next/link'
import { Search } from 'lucide-react'
import { api, getFullImageUrl } from '../services/api'

// 获取热门目的地数据
async function getPopularDestinations() {
  try {
    return await api.destinations.getPopular();
  } catch (error) {
    console.error('Error fetching popular destinations:', error);
    return [];
  }
}

export default async function Home() {
  // 获取热门目的地数据
  const popularDestinations = await getPopularDestinations();

  return (
    <Layout>
      <div className="container mx-auto px-4">
        {/* Hero Section */}
        <section className="relative h-[70vh] flex items-center justify-center overflow-hidden">
          <video 
            autoPlay 
            muted 
            loop 
            playsInline
            className="absolute w-full h-full object-cover"
          >
            <source src="/hero-video.mp4" type="video/mp4" />
          </video>
          <div className="absolute inset-0 bg-black/30 flex flex-col items-center justify-center text-white [text-shadow:_0_1px_2px_rgba(0,0,0,0.6)]">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">Discover Your Next Adventure</h1>
            <p className="text-xl md:text-2xl mb-8">Explore the world with our smart travel guide</p>
            <Link href="/destinations" className="bg-white text-blue-500 px-6 py-3 rounded-full text-lg font-semibold hover:bg-blue-100 transition duration-300">
              Start Exploring
            </Link>
          </div>
        </section>

        {/* Search Section */}
        <section className="my-12">
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <input type="text" placeholder="Search destinations..." className="w-full py-3 px-4 pr-10 rounded-full bg-white bg-opacity-30 backdrop-blur-md text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-lg hover:shadow-xl transition-shadow duration-300" />
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            </div>
          </div>
        </section>

        {/* Popular Destinations */}
        <section className="my-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Popular Destinations</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {popularDestinations.map((destination) => (
              <div key={destination.id} className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg overflow-hidden flex flex-col h-[380px]  shadow-md ">
                <div className="relative h-48">
                  <Image 
                    src={destination.cover_image ? getFullImageUrl(destination.cover_image.url) : "/placeholder.svg"} 
                    alt={destination.title} 
                    fill
                    className="object-cover"
                  />
                  {/* <div className="absolute top-2 right-2 bg-black/50 px-2 py-1 rounded-full">
                    <span className="text-sm text-yellow-400">★ {destination.rating.toFixed(1)}</span>
                  </div> */}
                </div>
                <div className="p-4 flex flex-col flex-grow">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">{destination.title}</h3>
                    <p className="text-gray-600 line-clamp-3 mb-2">{destination.description}</p>
                  </div>
                  <div className="mt-auto">
                    <Link 
                      href={`/destinations/${destination.id}`} 
                      className="inline-block bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600 transition duration-300"
                    >
                      Learn More
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="my-12">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Why Choose Us</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {['Smart Recommendations', 'Personalized Itineraries', 'Real-time Updates'].map((feature) => (
              <div key={feature} className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{feature}</h3>
                <p className="text-gray-600">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </Layout>
  )
}

