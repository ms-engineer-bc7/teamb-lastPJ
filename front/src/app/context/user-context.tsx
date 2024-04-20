'use client';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { auth } from '../../../firebase'; // Firebaseの設定ファイルへのパスを適切に設定
import { User, onAuthStateChanged } from 'firebase/auth';

interface UserContextType {
  user: User | null;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
    children: ReactNode;  // 子コンポーネントを受け取るためのプロパティ
  }

export const UserProvider:  React.FC<UserProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <UserContext.Provider value={{ user }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
