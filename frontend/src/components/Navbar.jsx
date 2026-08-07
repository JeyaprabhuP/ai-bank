import React from "react";
import { AppBar, Toolbar, Typography, IconButton, Box, Chip, Stack, Avatar } from "@mui/material";
import LogoutIcon from "@mui/icons-material/Logout";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import ShieldOutlinedIcon from "@mui/icons-material/ShieldOutlined";
import { useNavigate } from "react-router-dom";
import { logout, getCurrentUser } from "../services/authService";

export default function Navbar({ drawerWidth }) {
  const navigate = useNavigate();
  const user = getCurrentUser();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        width: { sm: `calc(100% - ${drawerWidth}px)` },
        ml: { sm: `${drawerWidth}px` },
        bgcolor: "rgba(6, 18, 31, 0.72)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <Toolbar sx={{ py: 1.2, gap: 1.5 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.2, flexGrow: 1 }}>
          <Avatar sx={{ bgcolor: "rgba(125, 211, 252, 0.16)", color: "primary.main", width: 36, height: 36 }}>
            <AccountBalanceIcon />
          </Avatar>
          <Box>
            <Typography variant="subtitle1" fontWeight={700}>Banking AI Platform</Typography>
            <Typography variant="caption" color="text.secondary">Secure intelligence operations / private banking portal</Typography>
          </Box>
        </Box>

        <Stack direction="row" spacing={1.2} alignItems="center">
          <Chip icon={<ShieldOutlinedIcon fontSize="small" />} label="Enterprise grade" color="info" sx={{ bgcolor: "rgba(125, 211, 252, 0.15)", color: "primary.main" }} />
          {user && (
            <Chip label={`${user.username} · ${user.role}`} size="small" sx={{ bgcolor: "rgba(255,255,255,0.08)", color: "text.primary" }} />
          )}
          <IconButton color="inherit" onClick={handleLogout} title="Log out" sx={{ bgcolor: "rgba(255,255,255,0.06)" }}>
            <LogoutIcon />
          </IconButton>
        </Stack>
      </Toolbar>
    </AppBar>
  );
}
