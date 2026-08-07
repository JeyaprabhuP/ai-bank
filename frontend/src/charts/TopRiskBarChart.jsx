import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const RISK_VALUE = { low: 1, medium: 2, high: 3 };

export default function TopRiskBarChart({ customers }) {
  const data = {
    labels: customers.map((c) => c.name.split(" ")[0]),
    datasets: [
      {
        label: "Risk Level",
        data: customers.map((c) => RISK_VALUE[c.risk_profile] || 1),
        backgroundColor: "#1E88E5",
      },
    ],
  };
  return (
    <Bar
      data={data}
      options={{
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { ticks: { stepSize: 1, callback: (v) => ["", "Low", "Med", "High"][v] } } },
      }}
    />
  );
}
