import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function FraudTrendLineChart({ trend }) {
  const data = {
    labels: trend.map((t) => t.date.slice(5)),
    datasets: [
      {
        label: "Fraud Alerts",
        data: trend.map((t) => t.count),
        borderColor: "#0B3D91",
        backgroundColor: "rgba(11,61,145,0.15)",
        tension: 0.35,
        fill: true,
      },
    ],
  };
  return <Line data={data} options={{ responsive: true, plugins: { legend: { display: false } } }} />;
}
