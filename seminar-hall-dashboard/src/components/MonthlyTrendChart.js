import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer
} from "recharts";
import moment from "moment";

export default function MonthlyTrendChart({ data }) {
  const monthly = {};

  data.forEach(item => {
    const date = moment(item["Booking date"]).format("YYYY-MM");
    monthly[date] = (monthly[date] || 0) + 1;
  });

  const chartData = Object.entries(monthly).map(([month, count]) => ({
    month, count
  }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={chartData}>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="count" stroke="#009FFD" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
