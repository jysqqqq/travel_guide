'use client'

import { useState } from 'react'
import Layout from '../components/layout'
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd'
import { MapPin, Calendar, Save, Share2 } from 'lucide-react'

export default function TripPlanner() {
  const [items, setItems] = useState([
    { id: 'item1', content: 'Visit Eiffel Tower' },
    { id: 'item2', content: 'Explore Louvre Museum' },
    { id: 'item3', content: 'Cruise on Seine River' },
    { id: 'item4', content: 'Walk around Montmartre' },
  ])

  const onDragEnd = (result) => {
    if (!result.destination) {
      return
    }

    const newItems = Array.from(items)
    const [reorderedItem] = newItems.splice(result.source.index, 1)
    newItems.splice(result.destination.index, 0, reorderedItem)

    setItems(newItems)
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8">Trip Planner</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6 mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Your Itinerary</h2>
              <DragDropContext onDragEnd={onDragEnd}>
                <Droppable droppableId="list">
                  {(provided) => (
                    <ul {...provided.droppableProps} ref={provided.innerRef} className="space-y-4">
                      {items.map((item, index) => (
                        <Draggable key={item.id} draggableId={item.id} index={index}>
                          {(provided) => (
                            <li
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className="bg-white bg-opacity-20 backdrop-blur-md rounded-lg p-4 flex items-center"
                            >
                              <Calendar className="text-white mr-3" size={20} />
                              <span className="text-gray-800">{item.content}</span>
                            </li>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </ul>
                  )}
                </Droppable>
              </DragDropContext>
            </div>

            <div className="flex space-x-4">
              <button className="flex items-center justify-center px-4 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition duration-300">
                <Save className="mr-2" size={20} />
                Save Trip
              </button>
              <button className="flex items-center justify-center px-4 py-2 bg-green-500 text-white rounded-full hover:bg-green-600 transition duration-300">
                <Share2 className="mr-2" size={20} />
                Share Trip
              </button>
            </div>
          </div>

          <div className="bg-white bg-opacity-30 backdrop-blur-md rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Trip Map</h2>
            <div className="h-96 bg-gray-300 rounded-lg flex items-center justify-center">
              <MapPin className="text-gray-500" size={48} />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

