"use client";
import { useQuery } from "@tanstack/react-query";
import { Grid, Card, CardContent, Typography, TextField, Button, Box } from "@mui/material";
import ReactECharts from "echarts-for-react";
import { apiGet, apiPost } from "@/lib/api";
import { useState } from "react";

export default function Home() {
  const { data: kpis } = useQuery({ queryKey: ["kpis"], queryFn: () => apiGet("/api/v1/analytics/kpis").catch(() => null) });
  const [msg, setMsg] = useState("Summarize stock-out and OOS risks");
  const [answer, setAnswer] = useState("");
  const ask = async () => {
    try { setAnswer((await apiPost("/api/v1/botpharma/chat", { message: msg })).answer); }
    catch { setAnswer("Start the API (make api) and log in first. Demo: admin@pharmx.local / Admin123!"); }
  };
  const k = kpis ?? { projects: 1, products: 1, batches: 1, oos_results: 1, open_deviations: 1, avg_yield_pct: 96 };
  return (
    <>
      <Typography variant="h4" gutterBottom>Executive Dashboard</Typography>
      <Grid container spacing={2}>
        {[
          ["R&D projects", k.projects], ["Products", k.products], ["Batches", k.batches],
          ["OOS results", k.oos_results], ["Open deviations", k.open_deviations], ["Avg yield %", k.avg_yield_pct],
        ].map(([label, v]) => (
          <Grid item xs={6} md={2} key={label as string}>
            <Card><CardContent><Typography variant="caption">{label}</Typography>
              <Typography variant="h5">{String(v)}</Typography></CardContent></Card>
          </Grid>
        ))}
      </Grid>
      <ReactECharts style={{ height: 300, marginTop: 16 }} option={{
        title: { text: "Yield vs Quality signals" },
        xAxis: { type: "category", data: ["Yield%", "OOS", "Deviations"] },
        yAxis: { type: "value" },
        series: [{ type: "bar", data: [k.avg_yield_pct, k.oos_results, k.open_deviations] }],
      }} />
      <Card sx={{ mt: 2 }}><CardContent>
        <Typography variant="h6">BotPharma™ quick ask</Typography>
        <Box display="flex" gap={1} mt={1}>
          <TextField fullWidth value={msg} onChange={(e) => setMsg(e.target.value)} />
          <Button variant="contained" onClick={ask}>Ask</Button>
        </Box>
        {answer && <Typography mt={2}>{answer}</Typography>}
      </CardContent></Card>
    </>
  );
}
