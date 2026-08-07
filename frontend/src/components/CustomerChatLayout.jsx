import React from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Box, AppBar, Toolbar, Typography, Avatar, Chip, IconButton, Stack } from "@mui/material";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import LogoutIcon from "@mui/icons-material/Logout";
import { logout, getCurrentUser } from "../services/authService";

/**
 * Layout for authenticated customers. Intentionally minimal: there is
 * no sidebar, no menu, and no navigation to any other feature — the AI
 * Assistant below is the entire application for this role. The only
 * account action available is logout (a normal session control, not a
 * way to remove or hide the assistant itself).
 */
export default function CustomerChatLayout() {
  const navigate = useNavigate();
  const user = getCurrentUser();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      <AppBar
        position="static"
        elevation={0}
        sx={{
          bgcolor: "rgba(6, 18, 31, 0.72)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <Toolbar sx={{ py: 1.2, gap: 1.5 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.2, flexGrow: 1, minWidth: 0 }}>
            <Avatar sx={{ bgcolor: "rgba(125, 211, 252, 0.16)", color: "primary.main", width: 36, height: 36 }}>
              <AccountBalanceIcon />
            </Avatar>
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="subtitle1" fontWeight={700} noWrap>
                Banking AI Assistant
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap sx={{ display: { xs: "none", sm: "block" } }}>
                Your secure banking support channel
              </Typography>
            </Box>
          </Box>

          <Stack direction="row" spacing={1.2} alignItems="center">
            {user && (
              <Chip
                label={user.username}
                size="small"
                sx={{ bgcolor: "rgba(255,255,255,0.08)", color: "text.primary", display: { xs: "none", sm: "flex" } }}
              />
            )}
            <IconButton
              color="inherit"
              onClick={handleLogout}
              title="Log out"
              sx={{ bgcolor: "rgba(255,255,255,0.06)" }}
            >
              <LogoutIcon />
            </IconButton>
          </Stack>
        </Toolbar>
      </AppBar>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
