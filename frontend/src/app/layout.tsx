"use client";
import { createTheme, ThemeProvider, CssBaseline, AppBar, Toolbar, Typography, Box, Button, Container } from "@mui/material";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Link from "next/link";
import { MODULES } from "@/lib/api";
import Login from "@/components/Login";
import { useState } from "react";

const theme = createTheme({ palette: { mode: "light", primary: { main: "#0b3d62" }, secondary: { main: "#079992" } } });
const qc = new QueryClient();

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [q] = useState(() => qc);
  return (
    <html lang="en">
      <body>
        <ThemeProvider theme={theme}>
          <QueryClientProvider client={q}>
            <CssBaseline />
            <AppBar position="static">
              <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>Quantum PharmX™ BI</Typography>
                {MODULES.slice(0, 6).map((m) => (
                  <Button key={m.href} color="inherit" component={Link} href={m.href}>{m.label}</Button>
                ))}
                <Button color="inherit" component={Link} href="/botpharma">BotPharma™</Button>
                <Login />
              </Toolbar>
            </AppBar>
            <Container maxWidth="lg"><Box py={3}>{children}</Box></Container>
          </QueryClientProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
