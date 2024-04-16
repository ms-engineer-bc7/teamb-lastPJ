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
    <div>
      <h1>ログイン情報を入力してください</h1>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button onClick={handleLoginWithEmail}>メールでログイン</button>
      <div>
        <button onClick={handleLoginWithGoogle}>Googleアカウントでログイン</button>
      </div>
      {/* 新規登録ボタンを追加 */}
      <div>
      <input type="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} />{/* 新しいstateを使用 */}
      <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />{/* 新しいstateを使用 */}
      <button onClick={handleSignUp}>新規登録</button>
      </div>
      <button onClick={() => router.push('/')}>TOPへ戻る</button>
    </div>
  );
};

export default LoginPage;

