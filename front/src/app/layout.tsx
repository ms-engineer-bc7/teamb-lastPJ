import { Inter } from "next/font/google";
import "./globals.css";
import Header from './component/Header';
import { UserProvider } from './context/user-context';
import type { ReactNode } from 'react';

const inter = Inter({ subsets: ["latin"] });

interface RootLayoutProps {
  children: ReactNode;
}

export const metadata = {
  title: "Bu.Ra.Ri -さんぽっと-",
  description: "BC7th Generation created this app",
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className={inter.className}>
       <head>
        {/* ファビコンの設定をここに移動 */}
        <link rel="icon" href="/negamon.ico" />
      </head>
      <body>
       <UserProvider>
        <Header />
        {children}
       </UserProvider>
      </body>
    </html>
  );
}