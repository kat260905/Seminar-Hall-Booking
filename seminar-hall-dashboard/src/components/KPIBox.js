import { Paper, Typography } from "@mui/material";

export default function KPIBox({ title, value, color = "#1976d2" }) {
  return (
    <Paper elevation={3} sx={{
      p: 3,
      borderLeft: `6px solid ${color}`,
      borderRadius: "10px",
      height: "120px"
    }}>
      <Typography variant="subtitle2" sx={{ opacity: 0.7 }}>{title}</Typography>
      <Typography variant="h4" sx={{ fontWeight: "bold" }}>{value}</Typography>
    </Paper>
  );
}
