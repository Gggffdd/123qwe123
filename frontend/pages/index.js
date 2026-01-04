import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useTelegram } from '../hooks/useTelegram'
import Dashboard from '../components/Dashboard'
import ProductList from '../components/ProductList'
import Chat from '../components/Chat'
import Bonuses from '../components/Bonuses'
import AdminPanel from '../components/AdminPanel'

export default function Home() {
  const { user, webApp } = useTelegram()
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isAdmin, setIsAdmin] = useState(false)

  useEffect(() => {
    if (user && user.is_admin) {
      setIsAdmin(true)
    }
  }, [user])

  const tabs = [
    { id: 'dashboard', label: '🏠 Главная', icon: '🏠' },
    { id: 'products', label: '🛍️ Все товары', icon: '🛍️' },
    { id: 'chat', label: '💬 Чат', icon: '💬' },
    { id: 'bonuses', label: '🎁 Бонусы', icon: '🎁' },
  ]

  if (isAdmin) {
    tabs.push({ id: 'admin', label: '⚙️ Админ', icon: '⚙️' })
  }

  return (
    <>
      <Head>
        <title>UNIVERSAL SHOP</title>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b dark:border-gray-700">
          <div className="container mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">US</span>
              </div>
              <h1 className="text-xl font-bold dark:text-white">UNIVERSAL SHOP</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => webApp?.setBackgroundColor?.(webApp.themeParams.bg_color)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {webApp?.colorScheme === 'dark' ? '🌙' : '☀️'}
              </button>
              
              <div className="relative">
                <input
                  type="text"
                  placeholder="Поиск..."
                  className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-6">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'products' && <ProductList />}
          {activeTab === 'chat' && <Chat />}
          {activeTab === 'bonuses' && <Bonuses />}
          {activeTab === 'admin' && isAdmin && <AdminPanel />}
        </main>

        {/* Bottom Navigation */}
        <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t dark:border-gray-700 py-3">
          <div className="flex justify-around">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-col items-center space-y-1 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === tab.id
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
    </>
  )
}
