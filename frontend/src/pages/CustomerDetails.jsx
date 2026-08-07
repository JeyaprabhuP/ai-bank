import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, Typography, Paper, Grid, Chip, Divider, List, ListItem, ListItemText } from "@mui/material";
import api from "../services/api";

export default function CustomerDetails() {
  const { customerId } = useParams();
  const [customer, setCustomer] = useState(null);

  useEffect(() => {
    api.get(`/customer/${customerId}`).then((res) => setCustomer(res.data));
  }, [customerId]);

  if (!customer) return <Typography>Loading customer...</Typography>;

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>{customer.name}</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2.5 }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>Profile</Typography>
            <Typography variant="body2">Email: {customer.email}</Typography>
            <Typography variant="body2">Phone: {customer.phone}</Typography>
            <Typography variant="body2">Address: {customer.address}</Typography>
            <Typography variant="body2">Customer since: {customer.account_opened}</Typography>
            <Chip
              sx={{ mt: 1 }}
              label={`Risk profile: ${customer.risk_profile}`}
              color={customer.risk_profile === "high" ? "error" : customer.risk_profile === "medium" ? "warning" : "success"}
              size="small"
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2.5 }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>Accounts</Typography>
            <Divider sx={{ mb: 1 }} />
            <List dense>
              {customer.accounts.map((a) => (
                <ListItem key={a.account_id}>
                  <ListItemText
                    primary={`${a.account_type.toUpperCase()} — $${a.balance.toLocaleString()}`}
                    secondary={a.account_id}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
