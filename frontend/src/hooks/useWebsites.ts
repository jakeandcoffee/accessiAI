import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as websiteService from "../services/websiteService";

export function useWebsites() {
  return useQuery({
    queryKey: ["websites"],
    queryFn: websiteService.getWebsites,
  });
}

export function useWebsite(id: string) {
  return useQuery({
    queryKey: ["websites", id],
    queryFn: () => websiteService.getWebsite(id),
    enabled: !!id,
  });
}

export function useCreateWebsite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: websiteService.createWebsite,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["websites"] }),
  });
}

export function useUpdateWebsite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: { id: string; name?: string; url?: string }) =>
      websiteService.updateWebsite(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["websites"] }),
  });
}

export function useDeleteWebsite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: websiteService.deleteWebsite,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["websites"] }),
  });
}
