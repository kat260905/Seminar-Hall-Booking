import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer
} from "recharts";

const COLORS = ["#0088FE", "#FF8042", "#00C49F", "#FFBB28", "#845EC2"];

export default function EventTypeChart({ data }) {
  const counts = Object.entries(
    data.reduce((acc, item) => {
      const type = item["event Type"];
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {})
  ).map(([type, value]) => ({ type, value }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <PieChart>
        <Pie data={counts} dataKey="value" nameKey="type" cx="50%" cy="50%" outerRadius={120}>
          {counts.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}
