import { motion } from "framer-motion";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { ScoreHistoryEntry } from "../../types";

interface ScoreHistoryProps {
  data: ScoreHistoryEntry[];
}

export function ScoreHistory({ data }: ScoreHistoryProps) {
  const formatted = data.map((d) => ({
    ...d,
    date: new Date(d.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={formatted}>
          <defs>
            <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6C8EFF" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#6C8EFF" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#7a8ba8" }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: "#7a8ba8" }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{
              background: "rgba(18, 18, 30, 0.9)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "8px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
              color: "#e2e8f0",
            }}
          />
          <Area
            type="monotone"
            dataKey="score"
            stroke="#6C8EFF"
            strokeWidth={2.5}
            fill="url(#scoreGradient)"
            animationDuration={1500}
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
