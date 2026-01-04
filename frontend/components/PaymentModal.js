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
    { id: 'usdt', name: 'USDT (TRC20)', icon: '💰
