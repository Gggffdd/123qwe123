import { useState } from 'react'
import { useTelegram } from '../hooks/useTelegram'
import axios from 'axios'

const AdminPanel = () => {
  const { user, webApp } = useTelegram()
  const [activeTab, setActiveTab] = useState('products')
  const [showAddForm, setShowAddForm] = useState(false)

  const tabs = [
    { id: 'products', label: 'Товары' },
    { id: 'games', label: 'Игры' },
    { id: 'apps', label: 'Приложения' },
    { id: 'orders', label: 'Заказы' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex space-x-2 overflow-x-auto pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'products' && <ProductManager />}
      {activeTab === 'games' && <GameManager />}
      {activeTab === 'apps' && <AppManager />}
      {activeTab === 'orders' && <OrderManager />}
    </div>
  )
}

const ProductManager = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    delivery_data: '',
    game_id: '',
    app_id: '',
    image: null
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    // Implementation for creating product
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold dark:text-white">Товары</h3>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
        >
          + Добавить товар
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="bg-gray-50 dark:bg-gray-700 p-6 rounded-xl space-y-4">
          <input
            type="text"
            placeholder="Название товара"
            className="w-full p-3 rounded-lg border dark:bg-gray-800 dark:border-gray-600"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
          />
          
          <textarea
            placeholder="Описание"
            className="w-full p-3 rounded-lg border dark:bg-gray-800 dark:border-gray-600"
            rows="3"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
          
          <input
            type="number"
            placeholder="Цена"
            className="w-full p-3 rounded-lg border dark:bg-gray-800 dark:border-gray-600"
            value={formData.price}
            onChange={(e) => setFormData({...formData, price: e.target.value})}
          />
          
          <textarea
            placeholder="Данные для выдачи (логин:пароль)"
            className="w-full p-3 rounded-lg border dark:bg-gray-800 dark:border-gray-600"
            rows="2"
            value={formData.delivery_data}
            onChange={(e) => setFormData({...formData, delivery_data: e.target.value})}
          />
          
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFormData({...formData, image: e.target.files[0]})}
          />
          
          <div className="flex space-x-3">
            <button
              type="submit"
              className="flex-1 bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600"
            >
              Сохранить
            </button>
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="flex-1 bg-gray-500 text-white py-3 rounded-lg hover:bg-gray-600"
            >
              Отмена
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

const GameManager = () => {
  return (
    <div>
      <h3 className="text-xl font-bold dark:text-white mb-4">Игры</h3>
      {/* Game management implementation */}
    </div>
  )
}

const AppManager = () => {
  return (
    <div>
      <h3 className="text-xl font-bold dark:text-white mb-4">Приложения</h3>
      {/* App management implementation */}
    </div>
  )
}

const OrderManager = () => {
  return (
    <div>
      <h3 className="text-xl font-bold dark:text-white mb-4">Заказы</h3>
      {/* Order management implementation */}
    </div>
  )
}

export default AdminPanel
