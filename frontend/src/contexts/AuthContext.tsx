import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { apiService } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (u: string, p: string) => Promise<void>;
  smartCardLogin: (cardUid: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: string) => boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('librasync_token');
      if (token) {
        try {
          const currentUser = await apiService.getCurrentUser();
          setUser(currentUser);
        } catch (e) {
          console.error('Session expired or invalid', e);
          localStorage.removeItem('librasync_token');
          localStorage.removeItem('librasync_smartcard');
          setUser(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (u: string, p: string) => {
    const data = await apiService.login({ username: u, password: p });
    localStorage.setItem('librasync_token', data.access_token);
    setUser(data.user);
  };

  const smartCardLogin = async (cardUid: string) => {
    const data = await apiService.smartCardLogin(cardUid);
    localStorage.setItem('librasync_token', data.access_token);
    localStorage.setItem('librasync_smartcard', cardUid);
    setUser(data.user);
  };

  const logout = () => {
    localStorage.removeItem('librasync_token');
    localStorage.removeItem('librasync_smartcard');
    setUser(null);
  };

  const hasRole = (role: string) => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.roles.includes(role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        smartCardLogin,
        logout,
        hasRole,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
