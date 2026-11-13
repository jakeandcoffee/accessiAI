import { useEffect, useRef, useState } from "react";

interface PandaMascotProps {
  size?: number;
}

export function PandaMascot({ size = 80 }: PandaMascotProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [eyeOffset, setEyeOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    function handleMouseMove(e: MouseEvent) {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const maxOffset = size * 0.04;
      const scale = Math.min(maxOffset / (dist || 1), maxOffset / 60);
      setEyeOffset({ x: dx * scale, y: dy * scale });
    }
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [size]);

  const s = size;
  const half = s / 2;

  return (
    <div ref={containerRef} style={{ width: s, height: s }} className="relative select-none">
      <svg viewBox="0 0 100 100" width={s} height={s} xmlns="http://www.w3.org/2000/svg">
        {/* Ears */}
        <circle cx="22" cy="22" r="16" fill="#1a1a2e" />
        <circle cx="78" cy="22" r="16" fill="#1a1a2e" />
        <circle cx="22" cy="22" r="10" fill="#2a2a3e" />
        <circle cx="78" cy="22" r="10" fill="#2a2a3e" />

        {/* Head */}
        <ellipse cx="50" cy="52" rx="38" ry="36" fill="#f0f0f0" />

        {/* Eye patches */}
        <ellipse cx="34" cy="46" rx="14" ry="13" fill="#1a1a2e" transform="rotate(-8 34 46)" />
        <ellipse cx="66" cy="46" rx="14" ry="13" fill="#1a1a2e" transform="rotate(8 66 46)" />

        {/* Eye whites */}
        <ellipse cx="35" cy="46" rx="8" ry="8.5" fill="white" />
        <ellipse cx="65" cy="46" rx="8" ry="8.5" fill="white" />

        {/* Pupils (move with mouse) */}
        <g>
          <circle
            cx={35 + eyeOffset.x}
            cy={46 + eyeOffset.y}
            r="4.5"
            fill="#1a1a2e"
          />
          <circle
            cx={35 + eyeOffset.x + 1.2}
            cy={46 + eyeOffset.y - 1.2}
            r="1.5"
            fill="white"
          />
        </g>
        <g>
          <circle
            cx={65 + eyeOffset.x}
            cy={46 + eyeOffset.y}
            r="4.5"
            fill="#1a1a2e"
          />
          <circle
            cx={65 + eyeOffset.x + 1.2}
            cy={46 + eyeOffset.y - 1.2}
            r="1.5"
            fill="white"
          />
        </g>

        {/* Nose */}
        <ellipse cx="50" cy="58" rx="5" ry="3.5" fill="#1a1a2e" />

        {/* Mouth */}
        <path
          d="M 45 62 Q 50 67 55 62"
          fill="none"
          stroke="#1a1a2e"
          strokeWidth="1.5"
          strokeLinecap="round"
        />

        {/* Blush */}
        <ellipse cx="24" cy="58" rx="6" ry="4" fill="#ff9baa" opacity="0.3" />
        <ellipse cx="76" cy="58" rx="6" ry="4" fill="#ff9baa" opacity="0.3" />
      </svg>
    </div>
  );
}
