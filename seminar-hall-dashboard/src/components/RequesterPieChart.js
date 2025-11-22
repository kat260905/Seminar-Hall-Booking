import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer
} from "recharts";

const COLORS = ["#3F72AF", "#F67280", "#C06C84", "#66DE93"];

export default function RequesterPieChart({ data }) {
  const counts = Object.entries(
    data.reduce((acc, item) => {
      const type = item["Requester type"];
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {})
  ).map(([type, value]) => ({ type, value }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={counts} dataKey="value" cx="50%" cy="50%" outerRadius={120}>
          {counts.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}
