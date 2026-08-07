import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#7dd3fc", contrastText: "#06121f" },
    secondary: { main: "#a78bfa" },
    success: { main: "#34d399" },
    warning: { main: "#fbbf24" },
    error: { main: "#fb7185" },
    info: { main: "#60a5fa" },
    background: { default: "#06121f", paper: "#0f172a" },
    text: { primary: "#f8fafc", secondary: "#9fb0ca" },
  },
  shape: { borderRadius: 18 },
  typography: {
    fontFamily: 'Inter, "Segoe UI", Roboto, sans-serif',
    h1: { fontWeight: 700 },
    h2: { fontWeight: 700 },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 700 },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        html: {
          height: "100%",
          overflow: "hidden",
        },
        body: {
          margin: 0,
          background: "radial-gradient(circle at top left, rgba(125, 211, 252, 0.16), transparent 30%), linear-gradient(135deg, #06121f 0%, #0b1220 45%, #111827 100%)",
          minHeight: "100vh",
          height: "100%",
          overflow: "hidden",
          color: "#f8fafc",
        },
        "#root": {
          height: "100%",
        },
        "*": { boxSizing: "border-box" },
        a: { color: "inherit", textDecoration: "none" },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04))",
          backdropFilter: "blur(18px)",
          border: "1px solid rgba(255,255,255,0.08)",
          boxShadow: "0 24px 60px rgba(2, 8, 23, 0.28)",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          textTransform: "none",
          fontWeight: 700,
          boxShadow: "none",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          border: "1px solid rgba(255,255,255,0.12)",
          fontWeight: 600,
        },
      },
    },
    MuiTextField: {
      defaultProps: { variant: "outlined" },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          color: "#9fb0ca",
          fontWeight: 700,
          borderBottom: "1px solid rgba(255,255,255,0.10)",
        },
        body: {
          borderBottom: "1px solid rgba(255,255,255,0.06)",
        },
      },
    },
  },
});

export default theme;
