import { useState } from 'react'
import { useTelegram } from '../hooks/useTelegram'
import axios from 'axios'
import PaymentModal from './PaymentModal'

const ProductCard = ({ product }) => {
  const { user, webApp } = useTelegram()
  const [showPayment, setShowPayment] = useState(false)

  const handleView = async () => {
    try {
      await axios.post(`/api/products/${product.id}/view`, {}, {
        headers: {
          Authorization: `Bearer ${webApp?.initData || user?.telegram_id}`
        }
      })
    } catch (error) {
      console.error('Error tracking view:', error)
    }
  }

  const handleBuy = () => {
    handleView()
    setShowPayment(true)
  }

  return (
    <>
      <div 
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
        onClick={handleView}
      >
        <div className="relative">
          <img 
            src={product.image_url || '/placeholder.jpg'} 
            alt={product.name}
            className="w-full h-48 object-cover"
          />
          <div className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
            {product.price} ₽
          </div>
        </div>
        
        <div className="p-4">
          <h3 className="font-bold text-lg dark:text-white mb-2">
            {product.name}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
            {product.description}
          </p>
          
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleBuy()
            }}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg font-bold hover:opacity-90 transition-opacity"
          >
            Купить
          </button>
        </div>
      </div>

      {showPayment && (
        <PaymentModal
          product={product}
          onClose={() => setShowPayment(false)}
        />
      )}
    </>
  )
}

export default ProductCard
