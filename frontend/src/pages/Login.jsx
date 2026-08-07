import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  Stack,
  Divider,
} from "@mui/material";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import { login } from "../services/authService";

export default function Login() {
  const { register, handleSubmit } = useForm();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    setError("");
    setLoading(true);
    try {
      const result = await login(data.username, data.password);
      // Customers land directly in the AI Assistant — their only
      // available feature. Everyone else goes to the staff dashboard.
      navigate(result.role === "customer" ? "/customer/chat" : "/dashboard");
    } catch (e) {
      setError(e.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (username, password) => {
    document.getElementById("username").value = username;
    document.getElementById("password").value = password;
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #0B3D91 0%, #1E88E5 100%)",
      }}
    >
      <Paper elevation={6} sx={{ p: 4, width: 380 }}>
        <Stack alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 40 }} />
          <Typography variant="h5" fontWeight={700}>Banking AI Platform</Typography>
          <Typography variant="body2" color="text.secondary">
            Multi-Agent Customer Service &amp; Fraud Detection
          </Typography>
        </Stack>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <Stack spacing={2}>
            <TextField
              id="username"
              label="Username"
              fullWidth
              defaultValue="admin"
              {...register("username", { required: true })}
            />
            <TextField
              id="password"
              label="Password"
              type="password"
              fullWidth
              defaultValue="admin123"
              {...register("password", { required: true })}
            />
            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </Stack>
        </form>

        <Divider sx={{ my: 2 }} />
        <Typography variant="caption" color="text.secondary">Demo credentials</Typography>
        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          <Button size="small" variant="outlined" onClick={() => fillDemo("admin", "admin123")}>
            Supervisor: admin / admin123
          </Button>
        </Stack>
        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          <Button size="small" variant="outlined" onClick={() => fillDemo("customer", "customer123")}>
            Customer: customer / customer123
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
