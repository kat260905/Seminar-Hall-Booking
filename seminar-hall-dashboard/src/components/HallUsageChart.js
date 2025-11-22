import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";

export default function HallUsageChart({ data }) {
  const hallCounts = Object.entries(
    data.reduce((acc, item) => {
      const hall = item["Hall name"];
      acc[hall] = (acc[hall] || 0) + 1;
      return acc;
    }, {})
  ).map(([hall, count]) => ({ hall, count }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={hallCounts}>
        <XAxis dataKey="hall" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" fill="#2A2A72" />
      </BarChart>
    </ResponsiveContainer>
  );
}
