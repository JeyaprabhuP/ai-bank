import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  MenuItem,
  Select,
  Stack,
} from "@mui/material";
import api from "../services/api";

const PRIORITY_COLOR = { Critical: "error", High: "warning", Medium: "info", Low: "success" };

export default function FraudAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [priority, setPriority] = useState("");

  const load = () => {
    api.get("/fraud-alerts", { params: { priority: priority || undefined } }).then((res) => setAlerts(res.data));
  };

  useEffect(load, [priority]);

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h5" fontWeight={700}>Fraud Alerts</Typography>
        <Select size="small" value={priority} displayEmpty onChange={(e) => setPriority(e.target.value)} sx={{ minWidth: 160 }}>
          <MenuItem value="">All priorities</MenuItem>
          <MenuItem value="Critical">Critical</MenuItem>
          <MenuItem value="High">High</MenuItem>
          <MenuItem value="Medium">Medium</MenuItem>
          <MenuItem value="Low">Low</MenuItem>
        </Select>
      </Stack>

      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Alert ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Risk Score</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Recommended Action</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {alerts.map((a) => (
              <TableRow key={a.alert_id} hover>
                <TableCell>{a.alert_id}</TableCell>
                <TableCell>{a.customer_name}</TableCell>
                <TableCell>{a.risk_score}</TableCell>
                <TableCell>
                  <Chip label={a.priority} color={PRIORITY_COLOR[a.priority]} size="small" />
                </TableCell>
                <TableCell>{a.recommended_action}</TableCell>
                <TableCell>{a.status}</TableCell>
                <TableCell>{new Date(a.created_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
