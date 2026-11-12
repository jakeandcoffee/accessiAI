import { createContext, useState, useEffect, useCallback, type ReactNode } from "react";
import type { User, LoginCredentials, RegisterData } from "../types";
import * as authService from "../services/authService";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("accessiai_token");
    if (token) {
      authService
        .getMe()
        .then(setUser)
        .catch(() => localStorage.removeItem("accessiai_token"))
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    await authService.login(credentials);
    const me = await authService.getMe();
    setUser(me);
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    await authService.register(data);
    const me = await authService.getMe();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    authService.logout();
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, isLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}
