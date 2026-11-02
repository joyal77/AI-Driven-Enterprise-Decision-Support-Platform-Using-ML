import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-chart-tooltip glass-card" style={{ padding: "12px 16px", borderRadius: "12px" }}>
        <p className="tooltip-date" style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "4px" }}>
          Date: {label}
        </p>
        <p className="tooltip-value" style={{ fontSize: "16px", fontWeight: "700", color: "#6366f1" }}>
          Revenue: ${payload[0].value?.toLocaleString()}
        </p>
      </div>
    );
  }
  return null;
};

function SalesChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>
        No historical sales data available.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
          </linearGradient>
        </defs>

        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />

        <XAxis 
          dataKey="date" 
          stroke="#64748b" 
          fontSize={12} 
          tickLine={false}
          axisLine={{ stroke: "rgba(255, 255, 255, 0.1)" }}
        />

        <YAxis 
          stroke="#64748b" 
          fontSize={12} 
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `$${value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value}`}
        />

        <Tooltip content={<CustomTooltip />} />

        <Area
          type="monotone"
          dataKey="sales"
          stroke="#6366f1"
          strokeWidth={3}
          fillOpacity={1}
          fill="url(#salesGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export default SalesChart;