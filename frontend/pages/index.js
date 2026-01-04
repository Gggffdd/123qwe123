import { useEffect, useState } from 'react'
import Head from 'next/head'
import Dashboard from '../components/Dashboard'
import axios from 'axios'

export default function Home() {
  const [theme, setTheme] = useState('light')
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Инициализация Telegram WebApp
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp
      
      // Расширяем на весь экран
      tg.expand()
      
      // Устанавливаем тему
      setTheme(tg.colorScheme === 'dark' ? 'dark' : 'light')
      
      // Создаем пользователя из данных Telegram
      const tgUser = tg.initDataUnsafe?.user
      if (tgUser) {
        setUser({
          id: tgUser.id,
          telegram_id: String(tgUser.id),
          first_name: tgUser.first_name,
          last_name: tgUser.last_name,
          username: tgUser.username,
          is_admin: String(tgUser.id) === process.env.NEXT_PUBLIC_ADMIN_ID
        })
        
        // Сохраняем initData для API запросов
        window.TELEGRAM_INIT_DATA = tg.initData
      }
    }
  }, [])

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      <Head>
        <title>UNIVERSAL SHOP</title>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </Head>

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b dark:border-gray-700 shadow-sm">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">US</span>
            </div>
            <h1 className="text-xl font-bold dark:text-white">UNIVERSAL SHOP</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {theme === 'dark' ? '🌙' : '☀️'}
            </button>
            
            <div className="relative">
              <input
                type="text"
                placeholder="Поиск товаров..."
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white w-40 md:w-64"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 pb-24">
        <Dashboard user={user} theme={theme} />
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t dark:border-gray-700 py-3 shadow-lg">
        <div className="flex justify-around">
          {[
            { id: 'dashboard', label: 'Главная', icon: '🏠' },
            { id: 'products', label: 'Товары', icon: '🛍️' },
            { id: 'chat', label: 'Чат', icon: '💬' },
            { id: 'bonuses', label: 'Бонусы', icon: '🎁' },
          ].map(tab => (
            <button
              key={tab.id}
              className={`flex flex-col items-center space-y-1 px-4 py-2 rounded-lg transition-colors ${
                tab.id === 'dashboard'
                  ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-gray-700'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <span className="text-xs font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  )
}
