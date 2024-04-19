'use client';
import { useEffect, useState } from 'react';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from '../../../firebase';

interface AuthState {
  user: User | null;
  loading: boolean;
}

export const useAuth = (): AuthState => {
  const [state, setState] = useState<AuthState>({ user: null, loading: true });

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, user => {
      if (user) {
        // ユーザーが認証されている場合は、UIDを取得
        const uid = user.uid;
        // 必要に応じてユーザー情報をデータベースから取得するなどの処理を行う
        // ...
      }
      setState({ user, loading: false });
    });

    return () => unsubscribe();
  }, []);

  return state;
};
