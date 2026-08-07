import React from "react";
import { Drawer, Toolbar, List, ListItemButton, ListItemIcon, ListItemText, Box, Typography, Avatar, Stack, Chip } from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ChatIcon from "@mui/icons-material/Chat";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import SupervisorAccountIcon from "@mui/icons-material/SupervisorAccount";
import SettingsIcon from "@mui/icons-material/Settings";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import { useNavigate, useLocation } from "react-router-dom";

const items = [
  { text: "Dashboard", icon: <DashboardIcon />, path: "/dashboard" },
  { text: "Chat Assistant", icon: <ChatIcon />, path: "/chat" },
  { text: "Fraud Alerts", icon: <WarningAmberIcon />, path: "/fraud-alerts" },
  { text: "Transactions", icon: <ReceiptLongIcon />, path: "/transactions" },
  { text: "Supervisor Dashboard", icon: <SupervisorAccountIcon />, path: "/supervisor" },
  { text: "Settings", icon: <SettingsIcon />, path: "/settings" },
];

export default function Sidebar({ drawerWidth }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: drawerWidth,
          boxSizing: "border-box",
          bgcolor: "rgba(6, 18, 31, 0.88)",
          borderRight: "1px solid rgba(255,255,255,0.08)",
          backgroundImage: "linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(7, 13, 24, 0.96))",
          backdropFilter: "blur(20px)",
        },
      }}
    >
      <Toolbar />
      <Box sx={{ px: 2, py: 2 }}>
        <Stack direction="row" spacing={1.2} alignItems="center" sx={{ mb: 2 }}>
          <Avatar sx={{ bgcolor: "rgba(125, 211, 252, 0.16)", color: "primary.main" }}>
            <SmartToyIcon />
          </Avatar>
          <Box>
            <Typography variant="subtitle2" fontWeight={700}>AI Control Center</Typography>
            <Typography variant="caption" color="text.secondary">Multi-agent oversight</Typography>
          </Box>
        </Stack>
        <Chip label="Live monitoring" color="success" size="small" sx={{ width: "fit-content" }} />
      </Box>
      <List sx={{ px: 1 }}>
        {items.map((item) => {
          const active = location.pathname === item.path;
          return (
            <ListItemButton
              key={item.text}
              selected={active}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 3,
                mb: 0.6,
                minHeight: 48,
                color: active ? "primary.main" : "text.secondary",
                "&.Mui-selected": {
                  bgcolor: "rgba(125, 211, 252, 0.16)",
                  color: "primary.main",
                  boxShadow: "inset 0 0 0 1px rgba(125, 211, 252, 0.2)",
                  "& .MuiListItemIcon-root": { color: "primary.main" },
                },
                "&:hover": { bgcolor: "rgba(255,255,255,0.06)" },
              }}
            >
              <ListItemIcon sx={{ minWidth: 42 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          );
        })}
      </List>
    </Drawer>
  );
}
