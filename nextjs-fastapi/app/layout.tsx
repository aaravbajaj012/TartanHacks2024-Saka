import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Improv Arena',
  description: 'A game of competitive improv',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full overflow-hidden light bg-slate-100">
      <body className={inter.className + '  bg-slate-100 h-full'}>{children}</body>
    </html>
  )
}
