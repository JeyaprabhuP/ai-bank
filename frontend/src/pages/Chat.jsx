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
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import api from "../services/api";
import { getCurrentUser } from "../services/authService";

const SUGGESTIONS = [
  "I noticed a suspicious transaction.",
  "My card was used in another country.",
  "How do I dispute a charge?",
  "How is my fraud risk score calculated?",
];

export default function Chat() {
  const user = getCurrentUser();
  const sessionIdRef = useRef(`session-${Date.now()}`);
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! I'm your AI banking assistant. How can I help today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text) => {
    const message = (text ?? input).trim();
    if (!message) return;
    setMessages((m) => [...m, { role: "user", text: message }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.post("/chat", {
        message,
        customer_id: user?.customer_id,
        session_id: sessionIdRef.current,
      });
      const { reply, intent, fraud_assessment, ticket, agent_trace, execution_time_ms, source } = res.data;
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: reply,
          meta: { intent, fraud_assessment, ticket, agent_trace, execution_time_ms, source },
        },
      ]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: "Sorry, something went wrong processing that." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "calc(100vh - 120px)" }}>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>AI Banking Chat Assistant</Typography>

      <Stack direction="row" spacing={1} sx={{ mb: 2 }} flexWrap="wrap" useFlexGap>
        {SUGGESTIONS.map((s) => (
          <Chip key={s} label={s} onClick={() => send(s)} variant="outlined" clickable />
        ))}
      </Stack>

      <Paper sx={{ flexGrow: 1, p: 2, overflowY: "auto", mb: 2 }}>
        <Stack spacing={2}>
          {messages.map((m, i) => (
            <Stack key={i} direction="row" spacing={1.5} alignItems="flex-start" justifyContent={m.role === "user" ? "flex-end" : "flex-start"}>
              {m.role === "assistant" && (
                <Avatar sx={{ bgcolor: "primary.main", width: 32, height: 32 }}>
                  <SmartToyIcon fontSize="small" />
                </Avatar>
              )}
              <Box
                sx={{
                  maxWidth: "70%",
                  bgcolor: m.role === "user" ? "primary.main" : "grey.100",
                  color: m.role === "user" ? "white" : "text.primary",
                  px: 2,
                  py: 1.2,
                  borderRadius: 2,
                }}
              >
                <Typography variant="body2">{m.text}</Typography>
                {m.meta?.fraud_assessment && (
                  <Chip
                    size="small"
                    sx={{ mt: 1 }}
                    label={`Risk: ${m.meta.fraud_assessment.risk_score}/100 · ${m.meta.fraud_assessment.priority}`}
                    color={m.meta.fraud_assessment.priority === "Critical" ? "error" : "warning"}
                  />
                )}
                {m.meta?.ticket && (
                  <Chip size="small" sx={{ mt: 1, ml: 1 }} label={`Ticket ${m.meta.ticket.ticket_id} created`} color="info" />
                )}
                {m.meta?.execution_time_ms && (
                  <Typography variant="caption" display="block" sx={{ mt: 0.5, opacity: 0.7 }}>
                    Agents: {m.meta.agent_trace.map((t) => t.agent).filter(Boolean).join(" → ")} · {m.meta.execution_time_ms}ms
                    {m.meta?.source ? ` · Source: ${m.meta.source}` : ""}
                  </Typography>
                )}
              </Box>
              {m.role === "user" && (
                <Avatar sx={{ bgcolor: "secondary.main", width: 32, height: 32 }}>
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

      <Paper sx={{ p: 1, display: "flex", alignItems: "center" }}>
        <TextField
          fullWidth
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          variant="standard"
          InputProps={{ disableUnderline: true }}
          sx={{ px: 1 }}
        />
        <IconButton color="primary" onClick={() => send()} disabled={loading}>
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  );
}
