import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, CssBaseline } from "@mui/material";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./components/AppLayout";
import theme from "./theme";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import FraudAlerts from "./pages/FraudAlerts";
import CustomerDetails from "./pages/CustomerDetails";
import Transactions from "./pages/Transactions";
import SupervisorDashboard from "./pages/SupervisorDashboard";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="chat" element={<Chat />} />
            <Route path="fraud-alerts" element={<FraudAlerts />} />
            <Route path="customers/:customerId" element={<CustomerDetails />} />
            <Route path="transactions" element={<Transactions />} />
            <Route path="supervisor" element={<SupervisorDashboard />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
