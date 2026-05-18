import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { HistoryEntry } from "../types";
import "./StatsChart.css";

const PIE_COLORS = ["#2e7d4a", "#c0392b"];
const BAR_COLOR = "#1b5e4a";

interface Props {
  history: HistoryEntry[];
}

export default function StatsChart({ history }: Props) {
  const diseaseCounts: Record<string, number> = {};
  let healthy = 0;
  let diseased = 0;

  for (const entry of history) {
    if (entry.is_healthy) healthy++;
    else diseased++;
    const key = entry.prediction.replace("Marigold – ", "");
    diseaseCounts[key] = (diseaseCounts[key] || 0) + 1;
  }

  const pieData = [
    { name: "Healthy", value: healthy },
    { name: "Diseased", value: diseased },
  ].filter((d) => d.value > 0);

  const barData = Object.entries(diseaseCounts).map(([name, count]) => ({ name, count }));

  if (history.length === 0) {
    return (
      <div className="stats-empty">
        <p>No scan data yet. Run your first analysis to populate charts.</p>
      </div>
    );
  }

  return (
    <div className="stats-grid">
      <div className="chart-card">
        <h4>Health split</h4>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={pieData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={4}
            >
              {pieData.map((_, i) => (
                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#fff",
                border: "1px solid var(--border)",
                borderRadius: 8,
                boxShadow: "var(--shadow)",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      {barData.length > 0 && (
        <div className="chart-card">
          <h4>By disease class</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={barData} layout="vertical" margin={{ left: 8, right: 16 }}>
              <XAxis type="number" allowDecimals={false} stroke="#5c6b62" fontSize={11} />
              <YAxis
                type="category"
                dataKey="name"
                width={110}
                tick={{ fontSize: 11, fill: "#5c6b62" }}
              />
              <Tooltip
                contentStyle={{
                  background: "#fff",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  boxShadow: "var(--shadow)",
                }}
              />
              <Bar dataKey="count" fill={BAR_COLOR} radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
