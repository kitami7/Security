// auth/AuthContext.tsx
import React, { createContext, useState, useEffect } from "react";
import { apiClient } from "../lib/apiClient";
import type { AuthContextType, AuthProviderProps, User } from "./authTypes";
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  

  const fetchUser = async () => {
    try {
      const { data, error } = await apiClient.GET("/me");
      setUser(error ? null : data ?? null);
    } catch (err) {
      console.error(err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await fetch("/logout", { method: "POST", credentials: "include" });
    setUser(null);
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, fetchUser, logout, loading}}>
      {children}
    </AuthContext.Provider>
  );
};
