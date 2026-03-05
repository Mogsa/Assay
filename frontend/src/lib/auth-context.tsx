"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { agents as agentsApi, auth as authApi } from "./api";
import type { AgentProfile } from "./types";

interface AuthState {
  user: AgentProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, displayName: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AgentProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const profile = await agentsApi.me();
      setUser(profile);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = async (email: string, password: string) => {
    await authApi.login(email, password);
    await refresh();
  };

  const signup = async (email: string, password: string, displayName: string) => {
    await authApi.signup(email, password, displayName);
    await authApi.login(email, password);
    await refresh();
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
