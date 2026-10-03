"use client";
import { useQuery } from "@tanstack/react-query";
import { Typography, Card, CardContent, Grid } from "@mui/material";
import { apiGet } from "@/lib/api";

function List({ title, path }: { title: string; path: string }) {
  const { data } = useQuery({ queryKey: [path], queryFn: () => apiGet(path).catch(() => []) });
  const rows = Array.isArray(data) ? data.slice(0, 20) : [];
  return (
    <Card><CardContent>
      <Typography variant="h6">{title}</Typography>
      <Typography variant="body2" color="text.secondary">{rows.length} records</Typography>
      <pre style={{ maxHeight: 320, overflow: "auto", fontSize: 12 }}>{JSON.stringify(rows, null, 1)}</pre>
    </CardContent></Card>
  );
}

export function ModulePage({ title, paths }: { title: string; paths: [string, string][] }) {
  return (<>
    <Typography variant="h4" gutterBottom>{title}</Typography>
    <Grid container spacing={2}>
      {paths.map(([t, p]) => (<Grid item xs={12} md={6} key={p}><List title={t} path={p} /></Grid>))}
    </Grid>
  </>);
}
