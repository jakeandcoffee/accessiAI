import api from "./api";
import type { LoginCredentials, RegisterData, TokenResponse, User } from "../types";

export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/api/auth/login", credentials);
  localStorage.setItem("accessiai_token", data.access_token);
  return data;
}

export async function register(userData: RegisterData): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/api/auth/register", userData);
  localStorage.setItem("accessiai_token", data.access_token);
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>("/api/auth/me");
  return data;
}

export function logout(): void {
  localStorage.removeItem("accessiai_token");
  window.location.href = "/login";
}
