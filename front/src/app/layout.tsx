import { Inter } from "next/font/google";
import "./globals.css";
import Header from './component/Header';
import type { ReactNode } from 'react';

const inter = Inter({ subsets: ["latin"] });

interface RootLayoutProps {
  children: ReactNode;
}

export const metadata = {
  title: "Bu.Ra.Ri -さんぽっと-",
  description: "BC7 by create next app",
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        <Header />
        {children}
      </body>
    </html>
  );
}
