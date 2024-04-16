import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from './component/Header';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Bu.Ra.Ri -さんぽっと-",
  description: "BC7 by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className={inter.className}>
      <Header />
        {children}</body>
    </html>
  );
  }