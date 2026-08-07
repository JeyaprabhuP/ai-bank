import React from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function AlertPriorityPieChart({ breakdown }) {
  const labels = Object.keys(breakdown);
  const data = {
    labels,
    datasets: [
      {
        data: labels.map((l) => breakdown[l]),
        backgroundColor: ["#D32F2F", "#F57C00", "#FBC02D", "#43A047"],
      },
    ],
  };
  return <Pie data={data} options={{ responsive: true }} />;
}
