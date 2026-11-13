import { useState, type FormEvent } from "react";
import { Modal } from "../common/Modal";
import { Button } from "../common/Button";
import { useUpdateWebsite } from "../../hooks/useWebsites";
import type { Website } from "../../types";
import { parsePageUrls, validatePageUrls } from "./pageUrls";
import { Attachments } from "./Attachments";

interface ManagePagesModalProps {
  website: Website;
  isOpen: boolean;
  onClose: () => void;
}

export function ManagePagesModal({ website, isOpen, onClose }: ManagePagesModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Scan Configuration">
      {/* Remount on open so the form starts from the saved pages */}
      <PagesForm key={String(isOpen)} website={website} onClose={onClose} />
    </Modal>
  );
}

function PagesForm({ website, onClose }: Omit<ManagePagesModalProps, "isOpen">) {
  const { mutate, isPending } = useUpdateWebsite();
  const [value, setValue] = useState(() => (website.page_urls ?? []).join("\n"));
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const result = validatePageUrls(value);
    if (result !== true) {
      setError(result);
      return;
    }
    mutate(
      { id: website.id, page_urls: parsePageUrls(value) },
      {
        onSuccess: onClose,
        onError: () => setError("Could not save pages. Check the URLs and try again."),
      },
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <p className="text-sm text-muted">
        The main URL <span className="text-ink">{website.url}</span> is always scanned. Add any
        other pages below — each one is scanned and reported separately.
      </p>
      <div>
        <label htmlFor="manage_page_urls" className="block text-sm font-medium text-ink mb-1">
          Additional Pages
        </label>
        <textarea
          id="manage_page_urls"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          rows={6}
          aria-describedby="manage_page_urls_hint"
          className="w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-ink font-mono placeholder:text-muted/50 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand/50"
          placeholder={"https://example.com/about\nhttps://example.com/contact"}
        />
        <p id="manage_page_urls_hint" className="text-xs text-muted mt-1">
          One URL per line.
        </p>
        {error && (
          <p className="text-red-400 text-xs mt-1" role="alert">{error}</p>
        )}
      </div>

      <div className="border-t border-white/[0.06] pt-4">
        <Attachments
          websiteId={website.id}
          attachments={website.attachments ?? []}
        />
      </div>

      <div className="flex gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onClose} className="flex-1">
          Cancel
        </Button>
        <Button type="submit" isLoading={isPending} className="flex-1">
          Save
        </Button>
      </div>
    </form>
  );
}
