import { useState } from 'react'
import { useTelegram } from '../hooks/useTelegram'
import axios from 'axios'

const PaymentModal = ({ product, onClose }) => {
  const { user, webApp } = useTelegram()
  const [paymentMethod, setPaymentMethod] = useState('ton')
  const [loading, setLoading] = useState(false)
  const [orderData, setOrderData] = useState(null)

  const handlePayment = async () => {
    setLoading(true)
    try {
      const response = await axios.post('/api/orders', {
        product_id: product.id,
        payment_method: paymentMethod
      }, {
        headers: {
          Authorization: `Bearer ${webApp?.initData || user?.telegram_id}`
        }
      })

      setOrderData(response.data)

      if (!response.data.requires_manual_payment) {
        // Open crypto payment
        webApp?.openLink(response.data.payment_url)
      }
    } catch (error) {
      console.error('Error creating order:', error)
      alert('Ошибка при создании заказа')
    } finally {
      setLoading(false)
    }
  }

  const paymentMethods = [
    { id: 'ton', name: 'TON', icon: '⚡', color: 'bg-blue-500' },
    { id: 'usdt', name: 'USDT (TRC20)', icon: '💰', color: 'bg-green-500' },
    { id: 'bank_transfer', name: 'Перевод по реквизитам', icon: '🏦', color: 'bg-yellow-500' },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-md">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold dark:text-white">Оплата</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {!orderData ? (
            <>
              {/* Product Info */}
              <div className="flex items-center space-x-4 mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                <img
                  src={product.image_url || '/placeholder.jpg'}
                  alt={product.name}
                  className="w-16 h-16 rounded-lg object-cover"
                />
                <div>
                  <h3 className="font-bold dark:text-white">{product.name}</h3>
                  <p className="text-2xl font-bold text-red-500">{product.price} ₽</p>
                </div>
              </div>

              {/* Payment Methods */}
              <div className="space-y-3 mb-6">
                <h3 className="font-bold dark:text-white mb-3">Способ оплаты:</h3>
                {paymentMethods.map(method => (
                  <label
                    key={method.id}
                    className={`flex items-center space-x-3 p-4 rounded-xl cursor-pointer border-2 transition-all ${
                      paymentMethod === method.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-gray-700'
                        : 'border-gray-200 dark:border-gray-700 hover:border-blue-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="payment"
                      value={method.id}
                      checked={paymentMethod === method.id}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="hidden"
                    />
                    <div className={`w-10 h-10 rounded-full ${method.color} flex items-center justify-center`}>
                      <span className="text-white text-lg">{method.icon}</span>
                    </div>
                    <span className="font-medium dark:text-white">{method.name}</span>
                  </label>
                ))}
              </div>

              <button
                onClick={handlePayment}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 rounded-xl font-bold hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {loading ? 'Обработка...' : 'Перейти к оплате'}
              </button>
            </>
          ) : (
            <div className="text-center">
              {orderData.requires_manual_payment ? (
                <>
                  <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">🏦</span>
                  </div>
                  <h3 className="text-xl font-bold dark:text-white mb-4">
                    Переведите по реквизитам
                  </h3>
                  
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-4 mb-6 text-left">
                    <div className="space-y-2">
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Банк:</span>
                        <p className="font-medium dark:text-white">{orderData.bank_details.bank_name}</p>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Номер карты:</span>
                        <p className="font-medium dark:text-white">{orderData.bank_details.card_number}</p>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Получатель:</span>
                        <p className="font-medium dark:text-white">{orderData.bank_details.account_holder}</p>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Сумма:</span>
                        <p className="font-medium dark:text-white">{product.price} ₽</p>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    После перевода администратор проверит оплату и отправит товар
                  </p>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">✅</span>
                  </div>
                  <h3 className="text-xl font-bold dark:text-white mb-4">
                    Открываю оплату...
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Если оплата не открылась автоматически, нажмите кнопку ниже
                  </p>
                  <button
                    onClick={() => webApp?.openLink(orderData.payment_url)}
                    className="w-full bg-green-500 text-white py-4 rounded-xl font-bold hover:opacity-90 transition-opacity"
                  >
                    Открыть оплату
                  </button>
                </>
              )}
              
              <button
                onClick={onClose}
                className="w-full mt-4 py-3 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300 font-medium"
              >
                Закрыть
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PaymentModal
