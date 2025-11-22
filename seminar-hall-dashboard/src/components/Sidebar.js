import React from "react";
import "../index.css";

export default function Sidebar() {
  return (
    <div className="sidebar">
      <h2>📊 Dashboard</h2>

      <a href="#">Overview</a>
      <a href="#">Hall Insights</a>
      <a href="#">Trends</a>
      <a href="#">Event Types</a>
      <a href="#">Requester Types</a>
    </div>
  );
}
