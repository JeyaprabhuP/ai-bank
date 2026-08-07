import React, { useEffect, useState } from "react";
import {
  Box, Typography, Paper, Table, TableHead, TableBody, TableRow, TableCell, Chip, Grid,
} from "@mui/material";
import api from "../services/api";

export default function SupervisorDashboard() {
  const [tickets, setTickets] = useState([]);
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    api.get("/tickets").then((res) => setTickets(res.data));
    api.get("/dashboard").then((res) => setDashboard(res.data));
  }, []);

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>Supervisor Dashboard</Typography>

      {dashboard && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {dashboard.agent_status.map((a) => (
            <Grid item xs={12} sm={6} md={3} key={a.name}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="body2" color="text.secondary">{a.name}</Typography>
                <Chip label={a.status} color="success" size="small" sx={{ mt: 1 }} />
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      <Paper>
        <Typography variant="subtitle1" fontWeight={600} sx={{ p: 2 }}>Support Tickets</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Ticket ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Subject</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Assigned Agent</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets.map((t) => (
              <TableRow key={t.ticket_id} hover>
                <TableCell>{t.ticket_id}</TableCell>
                <TableCell>{t.customer_id}</TableCell>
                <TableCell>{t.subject}</TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    label={t.priority}
                    color={t.priority === "Critical" ? "error" : t.priority === "High" ? "warning" : "default"}
                  />
                </TableCell>
                <TableCell>{t.status}</TableCell>
                <TableCell>{t.assigned_agent}</TableCell>
                <TableCell>{new Date(t.created_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
