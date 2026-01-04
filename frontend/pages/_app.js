import '../styles/globals.css'
import { useEffect } from 'react'

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    // Инициализация Telegram WebApp
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp
      
      // Расширяем на весь экран
      tg.expand()
      
      // Применяем тему Telegram
      document.documentElement.classList.toggle('dark', tg.colorScheme === 'dark')
      
      // Устанавливаем цвет фона
      document.body.style.backgroundColor = tg.themeParams.bg_color || '#ffffff'
    }
  }, [])

  return <Component {...pageProps} />
}

export default MyApp
