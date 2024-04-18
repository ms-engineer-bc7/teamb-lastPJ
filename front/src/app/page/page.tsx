'use client';
import React from 'react'; // Reactをインポート
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "../hooks/useAuth";
import Dashboard from '../routes/dashboard';
import NoAccess from '../routes/no-access';
import LoginPage from '../logins/page';  // ログインページのコンポーネント
import Home2 from '../mains/page';  // ログイン後のページ

const AppPage = () => {
    const pathname = usePathname(); // pathnameを取得
    const { user, loading } = useAuth();
    const router = useRouter();
  
    if (loading) {
        return <div>Loading...</div>;
      }
  
      if (!user) {
        return <LoginPage />;
      }
  
      // ログイン後のページリダイレクトを削除し、条件に基づいてコンポーネントを直接レンダリング
      switch (pathname) {
          case "/dashboard":
              return <Dashboard />;
          case "/no-access":
              return <NoAccess />;
          case "/mains":
              return <Home2 />; // Home2 コンポーネントを使用する
          default:
              return <div>Page Not Found</div>;
      }
  };
  
  export default AppPage;