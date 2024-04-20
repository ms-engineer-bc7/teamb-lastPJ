'use client'; 
import React from 'react';
import { FiSearch, FiUser } from 'react-icons/fi'; // Feather アイコンをインポートします
import { MdOutlineLogout } from "react-icons/md";
import Link from 'next/link'; // Next.js の Link コンポーネントをインポート
import { useRouter } from 'next/navigation'; // next/navigation から useRouter をインポート
import { auth } from '../../../firebase';
import { signOut } from 'firebase/auth';
import { FirebaseError } from 'firebase/app'; // Firebaseエラーの型
import { useUser } from '../context/user-context'; // UserContext フック
import { useEffect } from 'react';

const Header: React.FC = () => {
  const { user } = useUser(); // ユーザー情報を取得
  const router = useRouter(); // useRouter フックの使用

  // ログアウト処理の関数
  const handleLogout = async () => {
    try {
      await signOut(auth); // FirebaseのsignOut関数を呼び出し
      alert('ログアウトしました');
      router.push('/logins'); // ログアウト後にログインページにリダイレクト
    } catch (error: any) {
      if (error instanceof FirebaseError) { // Firebase固有のエラーを処理
        console.error('ログアウトに失敗しました:', error.message);
      } else if (error instanceof Error) { // 一般的なエラーを処理
        console.error('ログアウトに失敗しました:', error.message);
      }
      alert('ログアウトに失敗しました');
    }
  };

  useEffect(() => {
    // ここで handleLogout を呼び出す具体的な条件があれば設定可能
    // 例: ログアウトを自動的にトリガーする
    // handleLogout();
  }, [handleLogout]); // handleLogout を依存配列に追加

  return (
    <div className="bg-yellow-200 p-4 flex justify-between items-center">
      <div className="flex items-center space-x-4">
        <div className="rounded-full h-12 w-12 flex items-center justify-center bg-pink-200">
         <Link href="/">
          <img src="/negamon.png" className="h-8 w-8" alt="Logo" />
         </Link>
        </div>
        <span className="text-2xl font-bold">Bu.Ra.Ri</span>
      </div>
      <div className="flex space-x-6">

      <h1 className="text-lg">こんにちは： 
                {/* {user && (
                    <p>User: {user.displayName || "User"}!</p>  // ユーザー名を表示
                )} */}
                <span>{user ? user.displayName + "さん" || "User" : "ゲストさん"}
                </span>
      </h1>
        
       <Link href="/mains">
        <button>
          <FiSearch className="text-2xl"/> {/* 検索アイコン */}
        </button>
       </Link>

       <Link href="/logins">
        <button>
          <FiUser className="text-2xl"/> {/* ユーザーアイコン */}
        </button>
       </Link>
       
       <Link href="/logins">
        <button onClick={handleLogout}>
          <MdOutlineLogout className="text-2xl" /> {/* ログアウト */}
        </button>
       </Link>
       
      </div>
    </div>
  );
};

export default Header;
