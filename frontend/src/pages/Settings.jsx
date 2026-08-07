import React from "react";
import { Box, Typography, Paper, Stack, Chip } from "@mui/material";
import { getCurrentUser } from "../services/authService";

export default function Settings() {
  const user = getCurrentUser();

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>Settings</Typography>
      <Paper sx={{ p: 2.5, maxWidth: 480 }}>
        <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>Account</Typography>
        <Stack spacing={1}>
          <Typography variant="body2">Username: {user?.username}</Typography>
          <Typography variant="body2">Role: {user?.role}</Typography>
          {user?.customer_id && <Typography variant="body2">Customer ID: {user.customer_id}</Typography>}
        </Stack>
        <Typography variant="subtitle1" fontWeight={600} sx={{ mt: 3, mb: 1 }}>LLM Backend</Typography>
        <Chip label="Configured via backend .env (LLM_BACKEND)" size="small" />
        <Typography variant="caption" display="block" sx={{ mt: 1 }} color="text.secondary">
          Defaults to a mock, offline-friendly responder. Set OPENAI_API_KEY to enable live LLM calls,
          or LLM_BACKEND=ollama for a local model.
        </Typography>
      </Paper>
    </Box>
  );
}
