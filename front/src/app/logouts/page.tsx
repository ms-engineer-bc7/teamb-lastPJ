// 'use client';  // Next.js 13 の App Directory でクライアント側のコードを明示するための指示
// import React, { useEffect } from 'react';
// import { useRouter } from 'next/navigation'; // next/navigation から useRouter をインポート
// import { auth } from '../../../firebase';
// import { signOut } from 'firebase/auth';
// import { FirebaseError } from 'firebase/app'; // Firebaseエラーの型

// const LogoutButton: React.FC = () => {
//   const router = useRouter(); // 新しい useRouter フックの使用

//   // handleLogout を useEffect の外に移動
//   const handleLogout = async () => {
//     try {
//       await signOut(auth);
//       alert('ログアウトしました');
//       router.push('/logins'); // ログアウト後にログインページにリダイレクト
//     } catch (error: any) {
//       if (error instanceof FirebaseError) { // Firebase固有のエラーを処理
//         console.error('ログアウトに失敗しました:', error.message);
//       } else if (error instanceof Error) { // 一般的なエラーを処理
//         console.error('ログアウトに失敗しました:', error.message);
//       }
//       alert('ログアウトに失敗しました');
//     }
//   };

//   useEffect(() => {
//     // ここで handleLogout を呼び出す具体的な条件があれば設定可能
//     // 例: ログアウトを自動的にトリガーする
//     // handleLogout();
//   }, [handleLogout]); // handleLogout を依存配列に追加

//   return (
//     <button
//       className="bg-yellow-200 hover:bg-yellow-300 text-gray-700 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
//       onClick={handleLogout}  // onClick イベントハンドラに handleLogout を直接設定
//     >
//       ログアウト
//     </button>
//   );
// };

// export default LogoutButton;