import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import type { SeverityBreakdown } from "../../types";

const COLORS: Record<string, string> = {
  critical: "#ff5c5c",
  serious: "#ff9f43",
  moderate: "#ffd43b",
  minor: "#5c9cff",
};

interface SeverityChartProps {
  data: SeverityBreakdown[];
}

export function SeverityChart({ data }: SeverityChartProps) {
  const chartData = data.map((d) => ({
    name: d.severity.charAt(0).toUpperCase() + d.severity.slice(1),
    value: d.count,
    color: COLORS[d.severity] || "#7a8ba8",
  }));

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2 }}
    >
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={4}
            dataKey="value"
            animationBegin={300}
            animationDuration={1200}
          >
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} stroke="none" />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "rgba(18, 18, 30, 0.9)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "8px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
              color: "#e2e8f0",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex justify-center gap-4 mt-2">
        {chartData.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5 text-xs text-muted">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
            {d.name} ({d.value})
          </div>
        ))}
      </div>
    </motion.div>
  );
}
