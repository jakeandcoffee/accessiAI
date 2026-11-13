import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { clsx } from "clsx";
import { ChevronDown, Globe, Radar } from "lucide-react";
import { Button } from "../common/Button";
import { useTriggerScan } from "../../hooks/useScans";
import type { ScanMode } from "../../types";

interface ScanButtonProps {
  websiteId: string;
  className?: string;
}

const OPTIONS: { mode: ScanMode; label: string; description: string; icon: typeof Radar }[] = [
  { mode: "entered", label: "Scan", description: "Only the URLs you entered", icon: Radar },
  { mode: "all", label: "Scan all", description: "Find and scan every page on the site", icon: Globe },
];

export function ScanButton({ websiteId, className }: ScanButtonProps) {
  const { mutate, isPending, variables } = useTriggerScan();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const toggleRef = useRef<HTMLButtonElement>(null);
  const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const menuId = useId();

  useEffect(() => {
    if (!open) return;
    itemRefs.current[0]?.focus();
    const onPointerDown = (e: PointerEvent) => {
      if (!containerRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  const startScan = (mode: ScanMode) => {
    setOpen(false);
    mutate(
      { websiteId, mode },
      { onSuccess: (scan) => navigate(`/scans/${scan.id}`) },
    );
  };

  const onMenuKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    const items = itemRefs.current.filter(Boolean) as HTMLButtonElement[];
    const current = items.indexOf(document.activeElement as HTMLButtonElement);
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      const step = e.key === "ArrowDown" ? 1 : -1;
      items[(current + step + items.length) % items.length]?.focus();
    } else if (e.key === "Escape" || e.key === "Tab") {
      if (e.key === "Escape") e.preventDefault();
      setOpen(false);
      toggleRef.current?.focus();
    }
  };

  const pendingLabel = variables?.mode === "all" ? "Starting full scan..." : "Starting...";

  return (
    <div ref={containerRef} className={clsx("relative flex", className)}>
      <Button
        size="sm"
        className="flex-1 relative overflow-hidden rounded-r-none"
        onClick={() => startScan("entered")}
        isLoading={isPending}
        title="Scan only the URLs you entered"
      >
        {isPending && (
          <span className="absolute inset-0 rounded-lg border-2 border-white/30 animate-pulse-ring" />
        )}
        {!isPending && <Radar className="w-4 h-4" />}
        {isPending ? pendingLabel : "Scan"}
      </Button>
      <Button
        ref={toggleRef}
        size="sm"
        className="rounded-l-none border-l border-l-white/20 px-2"
        onClick={() => setOpen((o) => !o)}
        disabled={isPending}
        aria-label="More scan options"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={open ? menuId : undefined}
      >
        <ChevronDown className={clsx("w-4 h-4 transition-transform", open && "rotate-180")} />
      </Button>

      <AnimatePresence>
        {open && (
          <motion.div
            id={menuId}
            role="menu"
            aria-label="Scan options"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.12 }}
            onKeyDown={onMenuKeyDown}
            className="absolute right-0 top-full mt-1 z-30 w-64 rounded-lg border border-white/10 bg-[#12121f] p-1 shadow-xl"
          >
            {OPTIONS.map(({ mode, label, description, icon: Icon }, i) => (
              <button
                key={mode}
                ref={(el) => {
                  itemRefs.current[i] = el;
                }}
                type="button"
                role="menuitem"
                onClick={() => startScan(mode)}
                className="w-full flex items-start gap-3 rounded-md px-3 py-2 text-left hover:bg-white/[0.06] focus:bg-white/[0.08] focus:outline-none"
              >
                <Icon className="w-4 h-4 mt-0.5 text-brand shrink-0" />
                <span>
                  <span className="block text-sm font-semibold text-ink">{label}</span>
                  <span className="block text-xs text-muted">{description}</span>
                </span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
