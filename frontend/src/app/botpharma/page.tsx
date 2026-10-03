"use client";
import { useState } from "react";
import { Typography, Card, CardContent, TextField, Button, Box } from "@mui/material";
import { apiPost } from "@/lib/api";

export default function Bot() {
  const [msg, setMsg] = useState("What are our supply risks?");
  const [log, setLog] = useState<{ q: string; a: string }[]>([]);
  const send = async () => {
    const r = await apiPost("/api/v1/botpharma/chat", { message: msg }).catch((e) => ({ answer: String(e) }));
    setLog((l) => [...l, { q: msg, a: r.answer }]);
  };
  return (<>
    <Typography variant="h4" gutterBottom>BotPharma™</Typography>
    <Typography color="text.secondary">Role-aware, source-grounded, approval-gated enterprise agent interface.</Typography>
    <Card sx={{ mt: 2 }}><CardContent>
      <Box display="flex" gap={1}>
        <TextField fullWidth value={msg} onChange={(e) => setMsg(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} />
        <Button variant="contained" onClick={send}>Send</Button>
      </Box>
      {log.map((m, i) => (
        <Box key={i} mt={2}><Typography variant="subtitle2">You: {m.q}</Typography><Typography>BotPharma™: {m.a}</Typography></Box>
      ))}
    </CardContent></Card>
  </>);
}
