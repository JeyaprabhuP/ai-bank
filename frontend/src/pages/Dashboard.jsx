import React, { useEffect, useState } from "react";
import { Grid, Paper, Typography, Box, Chip, Stack, Avatar, List, ListItem, ListItemText } from "@mui/material";
import { useNavigate } from "react-router-dom";
import ForumIcon from "@mui/icons-material/Forum";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import ConfirmationNumberOutlinedIcon from "@mui/icons-material/ConfirmationNumberOutlined";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import SpeedOutlinedIcon from "@mui/icons-material/SpeedOutlined";
import api from "../services/api";
import FraudTrendLineChart from "../charts/FraudTrendLineChart";
import AlertPriorityPieChart from "../charts/AlertPriorityPieChart";
import TopRiskBarChart from "../charts/TopRiskBarChart";

function StatCard({ label, value, color, subtitle, icon, trend, onClick }) {
  return (
    <Paper
      onClick={onClick}
      sx={{
        p: 2.4,
        height: "100%",
        position: "relative",
        overflow: "hidden",
        cursor: onClick ? "pointer" : "default",
        transition: "transform 0.15s ease, box-shadow 0.15s ease",
        "&:hover": onClick ? { transform: "translateY(-1px)", boxShadow: 3 } : undefined,
      }}
    >
      <Box sx={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(125,211,252,0.10), transparent 65%)" }} />
      <Stack direction="row" spacing={1.5} alignItems="flex-start" sx={{ position: "relative", zIndex: 1 }}>
        <Avatar sx={{ bgcolor: `${color}.main` || "primary.main", color: "white", width: 40, height: 40 }}>
          {icon}
        </Avatar>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="body2" color="text.secondary">{label}</Typography>
          <Typography variant="h4" fontWeight={700} color={color ? `${color}.main` : "text.primary"} sx={{ mt: 0.4 }}>
            {value}
          </Typography>
          {(subtitle || trend) && (
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.7 }}>
              {trend && <Chip label={trend} size="small" color="success" />}
              {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
            </Stack>
          )}
        </Box>
      </Stack>
    </Paper>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/dashboard").then((res) => setData(res.data));
  }, []);

  if (!data) {
    return (
      <Box>
        <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>Command Center</Typography>
        <Paper sx={{ p: 3, textAlign: "center" }}>
          <Typography color="text.secondary">Loading executive intelligence feed...</Typography>
        </Paper>
      </Box>
    );
  }

  return (
    <Box>
      <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ xs: "flex-start", md: "center" }} spacing={2} sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>Command Center</Typography>
          <Typography variant="body1" color="text.secondary">Live overview of customer care, fraud posture, and AI assistance quality.</Typography>
        </Box>
        <Chip label="Real-time monitoring" color="info" sx={{ px: 1, py: 0.8 }} />
      </Stack>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Active Chats" value={data.active_chats} icon={<ForumIcon />} color="primary" subtitle="Live conversations" trend="+12%" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Critical Alerts" value={data.critical_alerts} icon={<ErrorOutlineIcon />} color="error" subtitle="Priority review" trend="Urgent" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Open Tickets" value={data.open_tickets} icon={<ConfirmationNumberOutlinedIcon />} color="warning" subtitle="Needs follow-up" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Avg AI Response" value={`${data.avg_ai_response_time_ms} ms`} icon={<SpeedOutlinedIcon />} color="info" subtitle="Fast and stable" />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <StatCard
            label="AI Resolutions"
            value={data.ai_resolution_count}
            icon={<CheckCircleOutlineIcon />}
            color="success"
            subtitle="Problems resolved by AI"
            onClick={() => navigate("/fraud-alerts?status=resolved&resolved_by=ai")}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            label="Manual Resolution"
            value={data.manual_resolution_count}
            icon={<ConfirmationNumberOutlinedIcon />}
            color="warning"
            subtitle="Problems resolved manually"
            onClick={() => navigate("/fraud-alerts?status=resolved&resolved_by=manual")}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2.5, height: "100%" }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>Fraud Trend (14 days)</Typography>
            <FraudTrendLineChart trend={data.fraud_trend} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2.5, height: "100%" }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>Alert Priority</Typography>
            <AlertPriorityPieChart breakdown={data.alert_priority_breakdown} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2.5, height: "100%" }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>Top Customers by Risk</Typography>
            <TopRiskBarChart customers={data.top_risk_customers} />
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2.5 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle1" fontWeight={600}>Recent AI Resolutions</Typography>
              <Chip label={`${data.ai_resolution_count || 0} items`} color="success" size="small" variant="outlined" />
            </Stack>
            <List dense disablePadding>
              {(data.recent_resolutions || []).map((item) => (
                <ListItem key={`${item.kind}-${item.id}`} disableGutters sx={{ py: 0.8 }}>
                  <ListItemText
                    primary={`${item.kind === "ticket" ? "Ticket" : "Alert"} ${item.id} · ${item.title}`}
                    secondary={`${item.customer_id} · ${item.resolution_action || "Updated by AI"} · Why: ${item.resolution_reason || "AI policy confidence exceeded threshold for automatic closure."} · ${new Date(item.timestamp).toLocaleString()}`}
                  />
                  <Chip
                    label={item.status}
                    size="small"
                    color={item.status === "resolved" ? "success" : "info"}
                    variant="outlined"
                  />
                </ListItem>
              ))}
              {(data.recent_resolutions || []).length === 0 && (
                <Typography variant="body2" color="text.secondary">No recent AI resolutions yet.</Typography>
              )}
            </List>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2.5 }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>System Health</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {Object.entries(data.system_health).map(([k, v]) => (
                <Chip key={k} label={`${k}: ${v}`} color={v === "healthy" ? "success" : "error"} size="small" />
              ))}
            </Stack>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2.5 }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>Agent Status</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {data.agent_status.map((a) => (
                <Chip key={a.name} label={`${a.name}: ${a.status}`} color="primary" variant="outlined" size="small" />
              ))}
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
