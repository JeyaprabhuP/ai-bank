import React, { useEffect, useMemo, useState } from "react";
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
  Button,
  TextField,
  FormControl,
  InputLabel,
  TableContainer,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Alert,
} from "@mui/material";
import { useLocation } from "react-router-dom";
import api from "../services/api";
import { getCurrentUser } from "../services/authService";

const PRIORITY_COLOR = { Critical: "error", High: "warning", Medium: "info", Low: "success" };

export default function FraudAlerts() {
  const user = getCurrentUser();
  const isSupervisor = user?.role === "supervisor";
  const location = useLocation();

  const query = new URLSearchParams(location.search);
  const queryStatus = query.get("status") || "";
  const queryResolvedBy = query.get("resolved_by") || "";

  const [alerts, setAlerts] = useState([]);
  const [priority, setPriority] = useState("");
  const [status, setStatus] = useState("");
  const [alertId, setAlertId] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [resolvedBy, setResolvedBy] = useState(queryResolvedBy);
  const [initiatingId, setInitiatingId] = useState(null);
  const [detailAlertId, setDetailAlertId] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");

  const load = () => {
    api.get("/fraud-alerts", {
      params: {
        priority: priority || undefined,
        status: status || undefined,
        alert_id: alertId || undefined,
        customer_id: customerId || undefined,
        customer_name: customerName || undefined,
        resolved_by: resolvedBy || undefined,
      },
    }).then((res) => setAlerts(res.data));
  };

  useEffect(load, [priority, status, alertId, customerId, customerName, resolvedBy]);

  useEffect(() => {
    setStatus(queryStatus);
    setResolvedBy(queryResolvedBy);
  }, [queryStatus, queryResolvedBy]);

  const hasFilters = useMemo(
    () =>
      [priority, status, alertId, customerId, customerName].some((value) => value !== ""),
    [priority, status, alertId, customerId, customerName, resolvedBy]
  );

  const clearFilters = () => {
    setPriority("");
    setStatus("");
    setAlertId("");
    setCustomerId("");
    setCustomerName("");
    setResolvedBy("");
  };

  const canInitiateChat = (alert) => {
    const status = (alert.status || "").toLowerCase();
    const prio = (alert.priority || "").toLowerCase();
    return ["open", "investigating"].includes(status) && ["critical", "high"].includes(prio) && !alert.chat_initiated;
  };

  const initiateChat = async (alert) => {
    setInitiatingId(alert.alert_id);
    try {
      await api.post(`/fraud-alerts/${alert.alert_id}/initiate-chat`, {
        initiated_by: user?.username || "supervisor",
        note: "Chat initiated from Fraud Alerts page",
      });
      load();
    } finally {
      setInitiatingId(null);
    }
  };

  const openDetails = async (alertId) => {
    setDetailAlertId(alertId);
    setDetailLoading(true);
    setDetailError("");
    try {
      const res = await api.get(`/fraud-alerts/${alertId}`);
      setDetailData(res.data);
    } catch (e) {
      setDetailData(null);
      setDetailError("Unable to load alert details. Please try again in a few seconds.");
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetails = () => {
    setDetailAlertId(null);
    setDetailData(null);
    setDetailLoading(false);
    setDetailError("");
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: 0, height: "100%" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2, flexShrink: 0 }}>
        <Typography variant="h5" fontWeight={700}>Fraud Alerts</Typography>
      </Stack>

      <Paper sx={{ p: 2, mb: 2, borderRadius: 3, flexShrink: 0, overflowX: "auto" }}>
        <Stack direction="row" spacing={1.5} useFlexGap flexWrap="nowrap" sx={{ minWidth: 0, alignItems: "center" }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Priority</InputLabel>
            <Select value={priority} label="Priority" onChange={(e) => setPriority(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="Critical">Critical</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="Low">Low</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select value={status} label="Status" onChange={(e) => setStatus(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="open">Open</MenuItem>
              <MenuItem value="investigating">Investigating</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
            </Select>
          </FormControl>
          <TextField size="small" label="Alert ID" value={alertId} onChange={(e) => setAlertId(e.target.value)} />
          <TextField size="small" label="Customer ID" value={customerId} onChange={(e) => setCustomerId(e.target.value)} />
          <TextField size="small" label="Customer Name" value={customerName} onChange={(e) => setCustomerName(e.target.value)} />
          <FormControl size="small" sx={{ minWidth: 170 }}>
            <InputLabel>Resolved By</InputLabel>
            <Select value={resolvedBy} label="Resolved By" onChange={(e) => setResolvedBy(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              <MenuItem value="ai">AI</MenuItem>
              <MenuItem value="manual">Manual</MenuItem>
            </Select>
          </FormControl>
          <Button variant="outlined" onClick={clearFilters} disabled={!hasFilters}>
            Clear Filters
          </Button>
        </Stack>
      </Paper>

      <Paper sx={{ flexGrow: 1, overflow: "hidden", borderRadius: 3, minHeight: 0 }}>
        <TableContainer sx={{ height: "100%", overflow: "auto", scrollbarGutter: "stable", WebkitMaskImage: "-webkit-radial-gradient(white, black)" }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Alert ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Risk Score</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Recommended Action</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell sx={{ whiteSpace: "nowrap", minWidth: 130 }}>Details</TableCell>
              {isSupervisor && <TableCell>Chat</TableCell>}
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
                <TableCell sx={{ whiteSpace: "nowrap" }}>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => openDetails(a.alert_id)}
                    sx={{ whiteSpace: "nowrap", minWidth: 110 }}
                  >
                    View Details
                  </Button>
                </TableCell>
                {isSupervisor && (
                  <TableCell>
                    {a.chat_initiated ? (
                      <Chip label="Chat Initiated" size="small" color="info" variant="outlined" />
                    ) : (
                      <Button
                        size="small"
                        variant="contained"
                        disabled={!canInitiateChat(a) || initiatingId === a.alert_id}
                        onClick={() => initiateChat(a)}
                      >
                        {initiatingId === a.alert_id ? "Starting..." : "Initiate Chat"}
                      </Button>
                    )}
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
        </TableContainer>
      </Paper>

      <Dialog open={Boolean(detailAlertId)} onClose={closeDetails} maxWidth="md" fullWidth>
        <DialogTitle>Alert Details {detailData?.alert?.alert_id ? `· ${detailData.alert.alert_id}` : ""}</DialogTitle>
        <DialogContent dividers>
          {detailLoading && <Typography color="text.secondary">Loading alert detail...</Typography>}
          {!detailLoading && detailError && <Alert severity="error">{detailError}</Alert>}
          {!detailLoading && detailData && (
            <Stack spacing={2}>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Stack direction={{ xs: "column", md: "row" }} spacing={2} useFlexGap flexWrap="wrap">
                  <Box><Typography variant="caption" color="text.secondary">Customer</Typography><Typography fontWeight={700}>{detailData.alert.customer_name}</Typography></Box>
                  <Box><Typography variant="caption" color="text.secondary">Customer ID</Typography><Typography fontWeight={700}>{detailData.alert.customer_id}</Typography></Box>
                  <Box><Typography variant="caption" color="text.secondary">Priority</Typography><Typography fontWeight={700}>{detailData.alert.priority}</Typography></Box>
                  <Box><Typography variant="caption" color="text.secondary">Risk Score</Typography><Typography fontWeight={700}>{detailData.alert.risk_score}</Typography></Box>
                  <Box><Typography variant="caption" color="text.secondary">Status</Typography><Typography fontWeight={700}>{detailData.alert.status}</Typography></Box>
                  <Box><Typography variant="caption" color="text.secondary">Recommended Action</Typography><Typography fontWeight={700}>{detailData.alert.recommended_action}</Typography></Box>
                </Stack>
              </Paper>

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Resolution Insight</Typography>
                <Stack spacing={0.5}>
                  <Typography variant="body2" color="text.secondary">
                    Resolved By: <Typography component="span" color="text.primary" fontWeight={600}>{detailData.alert.resolved_by || "unknown"}</Typography>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Resolution Reason: <Typography component="span" color="text.primary" fontWeight={600}>{detailData.alert.ai_resolution_reason || detailData.alert.supervisor_note || "No explicit reason recorded."}</Typography>
                  </Typography>
                </Stack>
              </Paper>

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Decision Trail</Typography>
                <List dense disablePadding>
                  {detailData.decision_trail.map((step, index) => (
                    <ListItem key={`${step.actor}-${index}`} disableGutters sx={{ py: 0.75 }}>
                      <ListItemText
                        primary={`${step.actor} · ${step.decision}`}
                        secondary={`${step.summary}${step.timestamp ? ` · ${new Date(step.timestamp).toLocaleString()}` : ""}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Factors</Typography>
                <Typography variant="body2" color="text.secondary">
                  {JSON.stringify(detailData.alert.factors, null, 2)}
                </Typography>
              </Paper>

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Related Tickets</Typography>
                <List dense disablePadding>
                  {detailData.related_tickets.map((ticket) => (
                    <ListItem key={ticket.ticket_id} disableGutters sx={{ py: 0.75 }}>
                      <ListItemText
                        primary={`${ticket.ticket_id} · ${ticket.subject}`}
                        secondary={`${ticket.status} · ${ticket.resolution_action || "No resolution yet"}`}
                      />
                    </ListItem>
                  ))}
                  {detailData.related_tickets.length === 0 && (
                    <Typography variant="body2" color="text.secondary">No related tickets found.</Typography>
                  )}
                </List>
              </Paper>

              {(detailData.alert.customer_interaction || detailData.alert.admin_interaction) && (
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                  <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Customer and Admin Interaction</Typography>
                  {detailData.alert.customer_interaction && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.8 }}>
                      Customer: {detailData.alert.customer_interaction.channel || "n/a"} · {detailData.alert.customer_interaction.customer_confirmation || "n/a"} · {detailData.alert.customer_interaction.summary || "n/a"}
                    </Typography>
                  )}
                  {detailData.alert.admin_interaction && (
                    <Typography variant="body2" color="text.secondary">
                      Admin: {detailData.alert.admin_interaction.admin_id || "n/a"} · {detailData.alert.admin_interaction.review_outcome || detailData.alert.admin_interaction.final_note || detailData.alert.admin_interaction.notes || "n/a"}
                    </Typography>
                  )}
                </Paper>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
