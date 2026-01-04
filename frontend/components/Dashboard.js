import { useState, useEffect } from 'react'
import { useTelegram } from '../hooks/useTelegram'
import GameCard from './GameCard'
import ProductCard from './ProductCard'
import axios from 'axios'

const Dashboard = () => {
  const { user, webApp } = useTelegram()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    try {
      const response = await axios.get('/api/dashboard', {
        headers: {
          Authorization: `Bearer ${webApp?.initData || user?.telegram_id}`
        }
      })
      setDashboardData(response.data)
    } catch (error) {
      console.error('Error fetching dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteViewHistory = async (productId) => {
    try {
      await axios.delete(`/api/view-history/${productId}`, {
        headers: {
          Authorization: `Bearer ${webApp?.initData || user?.telegram_id}`
        }
      })
      fetchDashboard()
    } catch (error) {
      console.error('Error deleting view history:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Games Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold dark:text-white">
            🎮 Игры
          </h2>
          <button className="text-blue-600 dark:text-blue-400 hover:underline">
            Смотреть все
          </button>
        </div>
        
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {dashboardData?.games?.map(game => (
            <GameCard key={game.id} game={game} />
          ))}
        </div>
      </section>

      {/* Apps Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold dark:text-white">
            📱 Приложения
          </h2>
          <button className="text-blue-600 dark:text-blue-400 hover:underline">
            Смотреть все
          </button>
        </div>
        
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {dashboardData?.apps?.map(app => (
            <GameCard key={app.id} game={app} isApp={true} />
          ))}
        </div>
      </section>

      {/* Last Viewed */}
      {dashboardData?.last_viewed && (
        <section>
          <h2 className="text-2xl font-bold dark:text-white mb-4">
            👀 Смотрел в последний раз
          </h2>
          
          <div className="relative">
            <ProductCard product={dashboardData.last_viewed} />
            <button
              onClick={() => handleDeleteViewHistory(dashboardData.last_viewed.id)}
              className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600"
            >
              Удалить
            </button>
          </div>
        </section>
      )}

      {/* All Products */}
      <section>
        <h2 className="text-2xl font-bold dark:text-white mb-4">
          🛒 Все товары
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dashboardData?.all_products?.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>
    </div>
  )
}

export default Dashboard
