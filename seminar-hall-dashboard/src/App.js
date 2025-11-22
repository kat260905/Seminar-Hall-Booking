import React, { useEffect, useState } from "react";
import { Grid, Typography } from "@mui/material";
import Sidebar from "./components/Sidebar";
import KPIBox from "./components/KPIBox";
import HallUsageChart from "./components/HallUsageChart";
import MonthlyTrendChart from "./components/MonthlyTrendChart";
import EventTypeChart from "./components/EventTypeChart";
import RequesterPieChart from "./components/RequesterPieChart";
import HeatmapChart from "./components/HeatmapChart";
import { fetchBookings } from "./api";
import "./index.css";

function App() {

  const [data, setData] = useState([]);

  useEffect(() => {
    fetchBookings().then(res => setData(res.data));
  }, []);

  const approved = data.filter(d => d["Booking status"] === "approved").length;
  const rejected = data.filter(d => d["Booking status"] === "rejected").length;
  const pending = data.filter(d => d["Booking status"] === "pending").length;

  return (
    <>
      <Sidebar />

      <div className="main-content">

        <Typography variant="h4" sx={{ fontWeight: "bold", mb: 3 }}>
          📊 Seminar Hall Dashboard
        </Typography>

        {/* KPI Row */}
        <Grid container spacing={2}>
          <Grid item md={3}><KPIBox title="Total Bookings" value={data.length} /></Grid>
          <Grid item md={3}><KPIBox title="Approved" value={approved} color="#4caf50" /></Grid>
          <Grid item md={3}><KPIBox title="Rejected" value={rejected} color="#f44336" /></Grid>
          <Grid item md={3}><KPIBox title="Pending" value={pending} color="#ff9800" /></Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3} sx={{ mt: 3 }}>
          <Grid item xs={12} md={6}><HallUsageChart data={data} /></Grid>
          <Grid item xs={12} md={6}><MonthlyTrendChart data={data} /></Grid>

          <Grid item xs={12} md={6}><EventTypeChart data={data} /></Grid>
          <Grid item xs={12} md={6}><RequesterPieChart data={data} /></Grid>

          <Grid item xs={12}><HeatmapChart data={data} /></Grid>
        </Grid>
      </div>
    </>
  );
}

export default App;
