import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, CssBaseline } from "@mui/material";

import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import AppLayout from "./components/AppLayout";
import CustomerChatLayout from "./components/CustomerChatLayout";
import theme from "./theme";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import CustomerChat from "./pages/CustomerChat";
import FraudAlerts from "./pages/FraudAlerts";
import CustomerDetails from "./pages/CustomerDetails";
import Transactions from "./pages/Transactions";
import SupervisorDashboard from "./pages/SupervisorDashboard";
import Settings from "./pages/Settings";
import { isAuthenticated, getCurrentUser } from "./services/authService";

const isCustomer = (user) => user?.role === "customer";

// Sends any unauthenticated visitor to /login, and any authenticated
// visitor to the home appropriate for their role — the AI Assistant
// for customers, the staff dashboard for everyone else. Used for the
// root path and any unmatched URL, so there's no dead end or stray
// route a customer could land on outside the assistant.
function RoleAwareHome() {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  const user = getCurrentUser();
  return <Navigate to={isCustomer(user) ? "/customer/chat" : "/dashboard"} replace />;
}

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* Customer experience: the AI Assistant only. No sidebar, no
              other routes are reachable from here. */}
          <Route
            path="/customer"
            element={
              <ProtectedRoute>
                <RoleRoute block={(u) => !isCustomer(u)} redirectTo="/dashboard">
                  <CustomerChatLayout />
                </RoleRoute>
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="chat" replace />} />
            <Route path="chat" element={<CustomerChat />} />
            {/* Any other path under /customer also resolves to the assistant. */}
            <Route path="*" element={<Navigate to="chat" replace />} />
          </Route>

          {/* Staff experience: full dashboard, unavailable to customers. */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <RoleRoute block={isCustomer} redirectTo="/customer/chat">
                  <AppLayout />
                </RoleRoute>
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

          <Route path="*" element={<RoleAwareHome />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
