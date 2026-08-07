import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Stack,
  Chip,
  Avatar,
  CircularProgress,
  Container,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import ShieldOutlinedIcon from "@mui/icons-material/ShieldOutlined";
import api from "../services/api";
import { getCurrentUser } from "../services/authService";

const SUGGESTIONS = [
  "What's my account balance?",
  "Show my recent transactions",
  "I noticed a suspicious transaction",
  "How do I dispute a charge?",
  "What are your overdraft fees?",
];

export default function CustomerChat() {
  const user = getCurrentUser();
  const firstName = user?.username ? user.username[0].toUpperCase() + user.username.slice(1) : "there";
  const sessionIdRef = useRef(`customer-session-${Date.now()}`);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: `Hi ${firstName}, I'm your AI banking assistant. I can help with balances, transactions, cards, fraud reports, and policy questions — ask me anything about your account.`,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text) => {
    const message = (text ?? input).trim();
    if (!message || loading) return;
    setMessages((m) => [...m, { role: "user", text: message }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.post("/chat", {
        message,
        customer_id: user?.customer_id,
        session_id: sessionIdRef.current,
      });
      const { reply, fraud_assessment, ticket, source } = res.data;
      setMessages((m) => [
        ...m,
        { role: "assistant", text: reply, meta: { fraud_assessment, ticket, source } },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Sorry, I couldn't process that right now. Please try again in a moment." },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column", overflow: "hidden", position: "relative" }}>
      <style>{`
        @keyframes ai-pulse-ring {
          0%   { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.55); }
          70%  { box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
          100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
        }
        .ai-status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #34d399;
          animation: ai-pulse-ring 2s infinite;
        }
      `}</style>

      {/* Ambient backdrop glow behind the whole conversation, echoing the app's existing radial gradient */}
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background:
            "radial-gradient(ellipse 70% 40% at 50% 0%, rgba(125, 211, 252, 0.10), transparent 60%)",
        }}
      />

      <Container maxWidth="md" sx={{ flexGrow: 1, display: "flex", flexDirection: "column", overflow: "hidden", py: { xs: 1.5, md: 3 } }}>
        {/* Header / status */}
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={1.5}
          alignItems={{ xs: "flex-start", sm: "center" }}
          justifyContent="space-between"
          sx={{ mb: 2 }}
        >
          <Box>
            <Typography variant="h5" fontWeight={700}>AI Banking Assistant</Typography>
            <Typography variant="body2" color="text.secondary">
              Ask about balances, transactions, cards, fraud, or policies — all in one place.
            </Typography>
          </Box>
          <Chip
            icon={<span className="ai-status-dot" style={{ marginLeft: 10 }} />}
            label="Always on"
            size="small"
            sx={{ bgcolor: "rgba(52, 211, 153, 0.14)", color: "success.main", fontWeight: 700 }}
          />
        </Stack>

        {/* Quick actions */}
        <Stack direction="row" spacing={1} sx={{ mb: 2 }} flexWrap="wrap" useFlexGap>
          {SUGGESTIONS.map((s) => (
            <Chip key={s} label={s} onClick={() => send(s)} variant="outlined" clickable disabled={loading} />
          ))}
        </Stack>

        {/* Conversation */}
        <Paper sx={{ flexGrow: 1, p: { xs: 1.5, md: 2.5 }, overflowY: "auto", mb: 2 }}>
          <Stack spacing={2}>
            {messages.map((m, i) => (
              <Stack
                key={i}
                direction="row"
                spacing={1.5}
                alignItems="flex-start"
                justifyContent={m.role === "user" ? "flex-end" : "flex-start"}
              >
                {m.role === "assistant" && (
                  <Avatar sx={{ bgcolor: "primary.main", width: 32, height: 32, flexShrink: 0 }}>
                    <SmartToyIcon fontSize="small" />
                  </Avatar>
                )}
                <Box
                  sx={{
                    maxWidth: { xs: "82%", sm: "70%" },
                    bgcolor: m.role === "user" ? "primary.main" : "rgba(255,255,255,0.06)",
                    color: m.role === "user" ? "primary.contrastText" : "text.primary",
                    px: 2,
                    py: 1.2,
                    borderRadius: 3,
                  }}
                >
                  <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>{m.text}</Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mt: m.meta ? 1 : 0 }}>
                    {m.meta?.fraud_assessment && (
                      <Chip
                        size="small"
                        icon={<ShieldOutlinedIcon fontSize="small" />}
                        label={`Risk: ${m.meta.fraud_assessment.risk_score}/100 · ${m.meta.fraud_assessment.priority}`}
                        color={m.meta.fraud_assessment.priority === "Critical" ? "error" : "warning"}
                      />
                    )}
                    {m.meta?.ticket && (
                      <Chip size="small" label={`Ticket ${m.meta.ticket.ticket_id} created`} color="info" />
                    )}
                    {m.meta?.source && (
                      <Chip size="small" variant="outlined" label={`Grounded in ${m.meta.source}`} />
                    )}
                  </Stack>
                </Box>
                {m.role === "user" && (
                  <Avatar sx={{ bgcolor: "secondary.main", width: 32, height: 32, flexShrink: 0 }}>
                    <PersonIcon fontSize="small" />
                  </Avatar>
                )}
              </Stack>
            ))}
            {loading && (
              <Stack direction="row" spacing={1.5} alignItems="center">
                <Avatar sx={{ bgcolor: "primary.main", width: 32, height: 32 }}>
                  <SmartToyIcon fontSize="small" />
                </Avatar>
                <CircularProgress size={18} />
              </Stack>
            )}
            <div ref={bottomRef} />
          </Stack>
        </Paper>

        {/* Input */}
        <Paper sx={{ p: 1, display: "flex", alignItems: "center", flexShrink: 0 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            autoFocus
            placeholder="Ask about your account, a transaction, or a policy..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
            variant="standard"
            InputProps={{ disableUnderline: true }}
            sx={{ px: 1 }}
          />
          <IconButton color="primary" onClick={() => send()} disabled={loading || !input.trim()}>
            <SendIcon />
          </IconButton>
        </Paper>
      </Container>
    </Box>
  );
}
