import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Paperclip, Upload, Trash2, FileText, Download } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "../common/Button";
import {
  uploadAttachment,
  deleteAttachment,
} from "../../services/websiteService";
import api from "../../services/api";
import type { Attachment } from "../../types";

interface AttachmentsProps {
  websiteId: string;
  attachments: Attachment[];
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function Attachments({ websiteId, attachments }: AttachmentsProps) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadAttachment(websiteId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["website", websiteId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (attachmentId: string) =>
      deleteAttachment(websiteId, attachmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["website", websiteId] });
    },
  });

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    for (let i = 0; i < files.length; i++) {
      uploadMutation.mutate(files[i]);
    }
  };

  const handleDownload = async (attachment: Attachment) => {
    const response = await api.get(
      `/api/websites/${websiteId}/attachments/${attachment.id}`,
      { responseType: "blob" },
    );
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = attachment.filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-ink">
          Scan Guidelines <span className="text-muted font-normal">(optional)</span>
        </label>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          isLoading={uploadMutation.isPending}
        >
          <Upload className="w-3.5 h-3.5" /> Upload
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg,.txt,.csv,.docx,.xlsx"
          multiple
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {uploadMutation.isError && (
        <p className="text-xs text-red-400">
          Upload failed: {(uploadMutation.error as Error).message}
        </p>
      )}

      {attachments.length === 0 ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFiles(e.dataTransfer.files);
          }}
          className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed py-6 transition-colors ${
            dragOver
              ? "border-brand bg-brand/5"
              : "border-white/10 hover:border-white/20"
          }`}
        >
          <Paperclip className="w-5 h-5 text-muted mb-1.5" />
          <p className="text-sm text-muted">
            Drop files here or click Upload
          </p>
          <p className="text-xs text-muted/60 mt-1">
            PDF, text, docs -- read as scan reference guidelines
          </p>
        </div>
      ) : (
        <div
          className="space-y-1"
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFiles(e.dataTransfer.files);
          }}
        >
          <AnimatePresence mode="popLayout">
            {attachments.map((attachment) => (
              <motion.div
                key={attachment.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="flex items-center justify-between rounded-lg border border-white/[0.06] px-3 py-2 group hover:bg-white/[0.03] transition-colors"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <FileText className="w-4 h-4 text-muted shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm text-ink truncate">
                      {attachment.filename}
                    </p>
                    <p className="text-xs text-muted">
                      {formatSize(attachment.size)}
                      <span className="mx-1.5 text-muted/40">·</span>
                      {new Date(attachment.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    type="button"
                    onClick={() => handleDownload(attachment)}
                    className="p-1.5 rounded-md hover:bg-white/10 text-muted hover:text-ink transition-colors"
                    title="Download"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMutation.mutate(attachment.id)}
                    disabled={deleteMutation.isPending}
                    className="p-1.5 rounded-md hover:bg-red-500/20 text-muted hover:text-red-400 transition-colors"
                    title="Remove"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {dragOver && (
            <div className="flex items-center justify-center rounded-lg border-2 border-dashed border-brand bg-brand/5 py-3 mt-1">
              <p className="text-sm text-brand">Drop to upload</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
