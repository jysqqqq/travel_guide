'use client'

import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import { storage } from '../lib/storage';
import axios from 'axios';

interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, email: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = storage.getItem('access_token');
      if (token) {
        const userData = await api.auth.getUserInfo();
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      storage.removeItem('access_token');
      storage.removeItem('refresh_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await api.auth.login(username, password);
      storage.setItem('access_token', response.access);
      storage.setItem('refresh_token', response.refresh);
      const userData = await api.auth.getUserInfo();
      setUser(userData);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          throw new Error('用户名或密码错误');
        } else if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail);
        }
      }
      throw new Error('登录失败，请稍后重试');
    }
  };

  const register = async (username: string, password: string, email: string) => {
    try {
      await api.auth.register({ username, password, email });
      await login(username, password);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.data?.username) {
          throw new Error('用户名已存在');
        } else if (error.response?.data?.email) {
          throw new Error('邮箱已被注册');
        } else if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail);
        } else if (error.response?.data?.password) {
          const passwordErrors = Array.isArray(error.response.data.password) 
            ? error.response.data.password.join('，') 
            : error.response.data.password;
          throw new Error(passwordErrors);
        }
      }
      throw new Error('注册失败，请稍后重试');
    }
  };

  const logout = () => {
    storage.removeItem('access_token');
    storage.removeItem('refresh_token');
    setUser(null);
    window.location.href = '/';
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 