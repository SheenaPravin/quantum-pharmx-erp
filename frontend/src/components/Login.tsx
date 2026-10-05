"use client";
import { useEffect, useState } from "react";
import { Button, TextField, Box, Typography } from "@mui/material";
import { API } from "@/lib/api";

export default function Login() {
  const [email, setEmail] = useState("admin@pharmx.local");
  const [password, setPassword] = useState("");
  const [who, setWho] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem("pharmx_token");
    const u = localStorage.getItem("pharmx_user");
    if (t && u) setWho(u);
  }, []);

  const login = async () => {
    const r = await fetch(`${API}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: email, password }),
    });
    if (!r.ok) return alert("Login failed — check credentials");
    const j = await r.json();
    localStorage.setItem("pharmx_token", j.access_token);
    localStorage.setItem("pharmx_user", email);
    setWho(email);
    setOpen(false);
    location.reload();
  };

  const logout = () => {
    localStorage.removeItem("pharmx_token");
    localStorage.removeItem("pharmx_user");
    setWho(null);
    location.reload();
  };

  if (who) return (<>
    <Typography variant="body2" sx={{ mr: 1 }}>{who}</Typography>
    <Button color="inherit" onClick={logout}>Logout</Button>
  </>);
  return (<>
    {!open ? (
      <Button color="inherit" onClick={() => setOpen(true)}>Login</Button>
    ) : (
      <Box display="flex" gap={1} alignItems="center">
        <TextField size="small" sx={{ bgcolor: "white", borderRadius: 1 }} value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" />
        <TextField size="small" type="password" sx={{ bgcolor: "white", borderRadius: 1 }} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" onKeyDown={(e) => e.key === "Enter" && login()} />
        <Button color="inherit" variant="outlined" onClick={login}>Go</Button>
      </Box>
    )}
  </>);
}
