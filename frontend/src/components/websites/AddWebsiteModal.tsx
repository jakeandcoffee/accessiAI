import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Globe } from "lucide-react";
import { Modal } from "../common/Modal";
import { Button } from "../common/Button";
import { useCreateWebsite } from "../../hooks/useWebsites";

const schema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  url: z.string().url("Must be a valid URL starting with http:// or https://"),
});

type FormData = z.infer<typeof schema>;

interface AddWebsiteModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AddWebsiteModal({ isOpen, onClose }: AddWebsiteModalProps) {
  const { mutate, isPending } = useCreateWebsite();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  function onSubmit(data: FormData) {
    mutate(data, {
      onSuccess: () => {
        reset();
        onClose();
      },
    });
  }

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
        <div className="flex gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button type="submit" isLoading={isPending} className="flex-1">
            Add Website
          </Button>
        </div>
      </form>
    </Modal>
  );
}
