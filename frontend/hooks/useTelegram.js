import { useEffect, useState } from 'react'

export const useTelegram = () => {
  const [user, setUser] = useState(null)
  const [webApp, setWebApp] = useState(null)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.ready()
      tg.expand()
      
      setWebApp(tg)
      
      // Extract user data
      const initData = tg.initDataUnsafe
      setUser({
        id: initData?.user?.id,
        first_name: initData?.user?.first_name,
        last_name: initData?.user?.last_name,
        username: initData?.user?.username,
        telegram_id: initData?.user?.id?.toString(),
        is_admin: initData?.user?.id === parseInt(process.env.NEXT_PUBLIC_ADMIN_ID)
      })
    }
  }, [])

  return { user, webApp }
}
