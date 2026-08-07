import React from "react";
import { Outlet } from "react-router-dom";
import { Box, Toolbar } from "@mui/material";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

const DRAWER_WIDTH = 240;

export default function AppLayout() {
  return (
    <Box sx={{ display: "flex", height: "100vh", overflow: "hidden", bgcolor: "transparent" }}>
      <Navbar drawerWidth={DRAWER_WIDTH} />
      <Sidebar drawerWidth={DRAWER_WIDTH} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: { xs: 0, sm: `${DRAWER_WIDTH}px` },
          p: { xs: 2, md: 3 },
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          height: "100vh",
          overflow: "hidden",
          bgcolor: "transparent",
        }}
      >
        <Toolbar />
        <Box
          sx={{
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 4,
            p: { xs: 2, md: 3 },
            background: "linear-gradient(135deg, rgba(15,23,42,0.92), rgba(8,15,28,0.9))",
            boxShadow: "inset 0 1px 0 rgba(255,255,255,0.06)",
            height: "calc(100vh - 96px)",
            overflowY: "auto",
            overflowX: "hidden",
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
