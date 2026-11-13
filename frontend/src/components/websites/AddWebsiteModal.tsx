import { useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Globe, Paperclip, X, FileText } from "lucide-react";
import { Modal } from "../common/Modal";
import { Button } from "../common/Button";
import { useCreateWebsite } from "../../hooks/useWebsites";
import { uploadAttachment } from "../../services/websiteService";
import { parsePageUrls, validatePageUrls } from "./pageUrls";

const schema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  url: z.string().url("Must be a valid URL starting with http:// or https://"),
  page_urls: z.string().optional().superRefine((value, ctx) => {
    const result = validatePageUrls(value);
    if (result !== true) ctx.addIssue({ code: z.ZodIssueCode.custom, message: result });
  }),
});

type FormData = z.infer<typeof schema>;

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface AddWebsiteModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AddWebsiteModal({ isOpen, onClose }: AddWebsiteModalProps) {
  const { mutateAsync, isPending } = useCreateWebsite();
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  function addFiles(files: FileList | null) {
    if (!files) return;
    const newFiles = Array.from(files);
    setPendingFiles((prev) => [...prev, ...newFiles]);
  }

  function removeFile(index: number) {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  }

  async function onSubmit(data: FormData) {
    setSubmitting(true);
    try {
      const website = await mutateAsync({
        ...data,
        page_urls: parsePageUrls(data.page_urls),
      });
      if (pendingFiles.length > 0) {
        await Promise.all(
          pendingFiles.map((file) => uploadAttachment(website.id, file))
        );
      }
      reset();
      setPendingFiles([]);
      onClose();
    } finally {
      setSubmitting(false);
    }
  }

  const loading = isPending || submitting;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Website">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-ink mb-1">
            Website Name
          </label>
          <input
            id="name"
            {...register("name")}
            className="w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-ink placeholder:text-muted/50 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand/50"
            placeholder="My Website"
          />
          {errors.name && (
            <p className="text-red-400 text-xs mt-1" role="alert">{errors.name.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-ink mb-1">
            Website URL
          </label>
          <div className="relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
            <input
              id="url"
              {...register("url")}
              className="w-full rounded-lg border border-white/10 bg-white/[0.04] pl-9 pr-3 py-2 text-sm text-ink placeholder:text-muted/50 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand/50"
              placeholder="https://example.com"
            />
          </div>
          {errors.url && (
            <p className="text-red-400 text-xs mt-1" role="alert">{errors.url.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="page_urls" className="block text-sm font-medium text-ink mb-1">
            Additional Pages <span className="text-muted font-normal">(optional)</span>
          </label>
          <textarea
            id="page_urls"
            {...register("page_urls")}
            rows={4}
            aria-describedby="page_urls_hint"
            className="w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-ink font-mono placeholder:text-muted/50 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand/50"
            placeholder={"https://example.com/about\nhttps://example.com/contact"}
          />
          <p id="page_urls_hint" className="text-xs text-muted mt-1">
            One URL per line. Every page is scanned and reported separately.
          </p>
          {errors.page_urls && (
            <p className="text-red-400 text-xs mt-1" role="alert">{errors.page_urls.message}</p>
          )}
        </div>

        <div className="border-t border-white/[0.06] pt-4 space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-ink">
              Scan Guidelines <span className="text-muted font-normal">(optional)</span>
            </label>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
            >
              <Paperclip className="w-3.5 h-3.5" /> Attach
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.png,.jpg,.jpeg,.txt,.csv,.docx,.xlsx"
              multiple
              onChange={(e) => {
                addFiles(e.target.files);
                e.target.value = "";
              }}
            />
          </div>

          {pendingFiles.length === 0 ? (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
              className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed py-6 transition-colors ${
                dragOver ? "border-brand bg-brand/5" : "border-white/10 hover:border-white/20"
              }`}
            >
              <Paperclip className="w-5 h-5 text-muted mb-1.5" />
              <p className="text-sm text-muted">Drop files here or click Attach</p>
              <p className="text-xs text-muted/60 mt-1">PDF, text, docs -- read as scan reference guidelines</p>
            </div>
          ) : (
            <div
              className="space-y-1"
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
            >
              {pendingFiles.map((file, i) => (
                <div
                  key={`${file.name}-${i}`}
                  className="flex items-center justify-between rounded-lg border border-white/[0.06] px-3 py-2 group hover:bg-white/[0.03] transition-colors"
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    <FileText className="w-4 h-4 text-muted shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm text-ink truncate">{file.name}</p>
                      <p className="text-xs text-muted">{formatSize(file.size)}</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(i)}
                    className="p-1.5 rounded-md hover:bg-red-500/20 text-muted hover:text-red-400 transition-colors"
                    title="Remove"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
              {dragOver && (
                <div className="flex items-center justify-center rounded-lg border-2 border-dashed border-brand bg-brand/5 py-3 mt-1">
                  <p className="text-sm text-brand">Drop to add</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button type="submit" isLoading={loading} className="flex-1">
            Add Website
          </Button>
        </div>
      </form>
    </Modal>
  );
}
