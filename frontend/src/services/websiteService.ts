import api from "./api";
import type { Website } from "../types";

export async function getWebsites(): Promise<Website[]> {
  const { data } = await api.get<Website[]>("/api/websites");
  return data;
}

export async function getWebsite(id: string): Promise<Website> {
  const { data } = await api.get<Website>(`/api/websites/${id}`);
  return data;
}

export async function createWebsite(payload: { name: string; url: string }): Promise<Website> {
  const { data } = await api.post<Website>("/api/websites", payload);
  return data;
}

export async function updateWebsite(id: string, payload: { name?: string; url?: string }): Promise<Website> {
  const { data } = await api.put<Website>(`/api/websites/${id}`, payload);
  return data;
}

export async function deleteWebsite(id: string): Promise<void> {
  await api.delete(`/api/websites/${id}`);
}
