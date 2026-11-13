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

export async function createWebsite(payload: {
  name: string;
  url: string;
  page_urls?: string[];
}): Promise<Website> {
  const { data } = await api.post<Website>("/api/websites", payload);
  return data;
}

export async function updateWebsite(
  id: string,
  payload: { name?: string; url?: string; page_urls?: string[] },
): Promise<Website> {
  const { data } = await api.put<Website>(`/api/websites/${id}`, payload);
  return data;
}

export async function deleteWebsite(id: string): Promise<void> {
  await api.delete(`/api/websites/${id}`);
}

export interface Attachment {
  id: string;
  filename: string;
  size: number;
  content_type: string;
  uploaded_at: string;
}

export async function uploadAttachment(
  websiteId: string,
  file: File,
): Promise<Attachment> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<Attachment>(
    `/api/websites/${websiteId}/attachments`,
    form,
  );
  return data;
}

export async function deleteAttachment(
  websiteId: string,
  attachmentId: string,
): Promise<void> {
  await api.delete(`/api/websites/${websiteId}/attachments/${attachmentId}`);
}

export function getAttachmentUrl(websiteId: string, attachmentId: string): string {
  return `/api/websites/${websiteId}/attachments/${attachmentId}`;
}
