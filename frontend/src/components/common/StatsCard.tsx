import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { type LucideIcon } from "lucide-react";
import { clsx } from "clsx";

interface StatsCardProps {
  label: string;
  value: number;
  icon: LucideIcon;
  color?: "brand" | "green" | "orange" | "red";
  delay?: number;
}

const colorMap = {
  brand: { bg: "bg-brand/10", text: "text-brand", icon: "text-brand" },
  green: { bg: "bg-green-500/10", text: "text-green-400", icon: "text-green-400" },
  orange: { bg: "bg-orange-500/10", text: "text-orange-400", icon: "text-orange-400" },
  red: { bg: "bg-red-500/10", text: "text-red-400", icon: "text-red-400" },
};

function useCountUp(target: number, duration = 1200) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (target === 0) { setCount(0); return; }
    const start = performance.now();
    function tick(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [target, duration]);
  return count;
}

export function StatsCard({ label, value, icon: Icon, color = "brand", delay = 0 }: StatsCardProps) {
  const displayValue = useCountUp(value);
  const c = colorMap[color];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, type: "spring", stiffness: 300, damping: 24 }}
      whileHover={{ y: -2, boxShadow: "0 12px 40px rgba(108,142,255,0.06)" }}
      className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg p-5"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-muted">{label}</span>
        <div className={clsx("w-9 h-9 rounded-lg flex items-center justify-center border border-white/[0.06]", c.bg)}>
          <Icon className={clsx("w-5 h-5", c.icon)} />
        </div>
      </div>
      <div className={clsx("text-3xl font-bold tabular-nums", c.text)}>
        {displayValue}
      </div>
    </motion.div>
  );
}
