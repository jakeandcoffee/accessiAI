import { motion, type HTMLMotionProps } from "framer-motion";
import { clsx } from "clsx";

interface CardProps extends HTMLMotionProps<"div"> {
  gradient?: boolean;
  hoverable?: boolean;
}

export function Card({ gradient, hoverable = true, className, children, ...props }: CardProps) {
  return (
    <motion.div
      whileHover={hoverable ? { y: -2, boxShadow: "0 12px 40px rgba(108,142,255,0.06)" } : undefined}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={clsx(
        "rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg p-6 shadow-sm transition-colors",
        gradient && "bg-gradient-to-br from-white/[0.06] to-brand/[0.04]",
        className,
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}
