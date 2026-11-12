import { clsx } from "clsx";

interface BadgeProps {
  variant: "critical" | "serious" | "moderate" | "minor" | "open" | "in_progress" | "resolved" | "ignored";
  children: React.ReactNode;
}

const styles: Record<string, string> = {
  critical: "bg-red-500/15 text-red-400 border-red-500/20",
  serious: "bg-orange-500/15 text-orange-400 border-orange-500/20",
  moderate: "bg-yellow-500/15 text-yellow-400 border-yellow-500/20",
  minor: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  open: "bg-white/5 text-gray-400 border-white/10",
  in_progress: "bg-purple-500/15 text-purple-400 border-purple-500/20",
  resolved: "bg-green-500/15 text-green-400 border-green-500/20",
  ignored: "bg-white/5 text-gray-500 border-white/10",
};

export function Badge({ variant, children }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        styles[variant],
      )}
    >
      {children}
    </span>
  );
}
