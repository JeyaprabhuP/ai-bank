import React, { useEffect, useState } from "react";
import {
  Box, Typography, Paper, Table, TableHead, TableBody, TableRow, TableCell, Chip,
} from "@mui/material";
import api from "../services/api";

export default function Transactions() {
  const [txns, setTxns] = useState([]);

  useEffect(() => {
    api.get("/transactions", { params: { limit: 100 } }).then((res) => setTxns(res.data));
  }, []);

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>Transactions</Typography>
      <Paper sx={{ maxHeight: "75vh", overflow: "auto" }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Transaction ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Device</TableCell>
              <TableCell>Timestamp</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {txns.map((t) => (
              <TableRow key={t.transaction_id} hover>
                <TableCell>{t.transaction_id}</TableCell>
                <TableCell>{t.customer_id}</TableCell>
                <TableCell>${Number(t.amount).toFixed(2)}</TableCell>
                <TableCell>{t.merchant_category}</TableCell>
                <TableCell>
                  {t.location} {t.is_foreign === "True" || t.is_foreign === true ? <Chip label="foreign" size="small" color="warning" sx={{ ml: 0.5 }} /> : null}
                </TableCell>
                <TableCell>{t.device}</TableCell>
                <TableCell>{new Date(t.timestamp).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
