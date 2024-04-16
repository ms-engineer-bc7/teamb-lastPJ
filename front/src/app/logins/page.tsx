'use client'
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation'; // 追加
import { auth } from '../../../firebase'; // Firebaseの設定ファイルをインポート
import { signInWithEmailAndPassword,signInWithRedirect,getRedirectResult,GoogleAuthProvider,createUserWithEmailAndPassword,sendEmailVerification} from 'firebase/auth';

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // シンプルなメール形式チェック用の正規表現

  const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [newEmail, setNewEmail] = useState(''); // 新しいstateを追加
  const [newPassword, setNewPassword] = useState(''); // 新しいstateを追加
  const router = useRouter()

  // ユーザーが認証後にリダイレクトされたときの結果を処理
  useEffect(() => {
    getRedirectResult(auth).then((result) => {
      if (result) {
        // ユーザーが認証された場合、管理画面へリダイレクト
        router.push('/managements');
      }
      // リダイレクト結果がnullの場合、何もしない
      // 認証エラーがあればここで処理できる
    }).catch((error) => {
      // エラーハンドリング
      console.error('リダイレクト後の認証エラー:', error);
    });
  }, [router]);

  // メール/パスワードによるログイン処理
  const handleLoginWithEmail = async () => {
    if (!emailRegex.test(email)) {
      alert('無効なメールアドレス形式です。');
      return;
    }
    try {
      await signInWithEmailAndPassword(auth, email, password);
      router.push('/managements');
    } catch (error) {
      console.error('ログインエラー:', error);
      alert('ログインに失敗しました。メールアドレスまたはパスワードが正しくありません。');
    }
  };

  // Google認証の処理（リダイレクトを使用）
  const handleLoginWithGoogle = () => {
    const provider = new GoogleAuthProvider();
    signInWithRedirect(auth, provider);
  };

  // 新規登録処理を追加
  const handleSignUp = async () => {
    if (!emailRegex.test(newEmail)) {
      alert('無効な新規メールアドレス形式です。');
      return;
    }
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, newEmail, newPassword);
      await sendEmailVerification(userCredential.user);
      router.push('/managements');
    } catch (error) {
      console.error('新規登録エラー:', error);
      alert('新規登録に失敗しました。入力したメールアドレスが無効です。');
    }
  };

  // ログアウト処理
  const handleLogout = async () => {
    try {
      await auth.signOut();
      alert('ログアウトしました');
      router.push('/login'); // ログアウト後、ログインページにリダイレクト
    } catch (error) {
      console.error('ログアウトに失敗しました:', error);
      alert('ログアウトに失敗しました');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-yellow-300">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center mb-4">ログイン</h1>
        {/* Existing User Login */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
            メールアドレス
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="メールアドレス"
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
            パスワード
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="パスワード"
          />
        </div>
        <div className="mb-6">
          <button
            className="bg-yellow-200 hover:bg-yellow-300 text-gray-700 font-bold py-2 px-4 w-full rounded focus:outline-none focus:shadow-outline"
            type="button"
            onClick={handleLoginWithEmail}
          >
            メールでログイン
          </button>
        </div>
        <div className="mb-6">
          <button
            className="bg-yellow-200 hover:bg-yellow-300 text-gray-700 font-bold py-2 px-4 w-full rounded focus:outline-none focus:shadow-outline"
            type="button"
            onClick={handleLoginWithGoogle}
          >
            Googleアカウントでログイン
          </button>
        </div>
        {/* New User Registration */}
        <h1 className="text-2xl font-bold text-center mb-4">新規登録</h1>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="newEmail">
            新規メールアドレス
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="newEmail"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            placeholder="新規メールアドレス"
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="newPassword">
            新規パスワード
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="newPassword"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="新規パスワード"
          />
        </div>
        <div className="mb-6">
          <button
            className="bg-yellow-200 hover:bg-yellow-300 text-gray-700 font-bold py-2 px-4 w-full rounded focus:outline-none focus:shadow-outline"
            type="button"
            onClick={handleSignUp}
          >
            新規登録
          </button>
        </div>
        <div className="flex justify-center">
         <button
           className=" bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
           type="button"
           onClick={() => router.push('/')}
         >
           TOPへ戻る
         </button>
        </div>
        <p className="text-center text-gray-500 text-xs">&copy;2024 Bu.ra.ri Company. All rights reserved.</p>
      </div>
    </div>
  );
};

export default LoginPage;

