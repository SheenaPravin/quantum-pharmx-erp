const raw = (process.env.NEXT_PUBLIC_API_URL || "").trim();
export const API = raw || "http://localhost:8000";

// True when the build was pointed at a real backend. On the public demo
// (GitHub Pages) this is empty, so API calls can't reach a backend.
export const BACKEND_CONFIGURED = raw !== "";

function cleanError(path: string, status: number, body: string): Error {
  if (/<\s*!doctype|<\s*html/i.test(body)) {
    return new Error(
      `${path}: ${status} — API not reachable from this demo site (no backend configured). ` +
        `Run the FastAPI backend and set NEXT_PUBLIC_API_URL to enable live data.`
    );
  }
  return new Error(`${path}: ${status} ${body.slice(0, 300)}`);
}

export function authHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const t = localStorage.getItem("pharmx_token");
  return t ? { Authorization: `Bearer ${t}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
}

export async function apiGet(path: string) {
  const r = await fetch(`${API}${path}`, { headers: authHeaders() });
  if (!r.ok) throw cleanError(path, r.status, await r.text());
  return r.json();
}

export async function apiPost(path: string, body: unknown) {
  const r = await fetch(`${API}${path}`, { method: "POST", headers: authHeaders(), body: JSON.stringify(body) });
  if (!r.ok) throw cleanError(path, r.status, await r.text());
  return r.json();
}

export const MODULES = [
  { href: "/", label: "Executive" },
  { href: "/rnd", label: "R&D" },
  { href: "/products", label: "Products" },
  { href: "/procurement", label: "Procurement" },
  { href: "/inventory", label: "Inventory" },
  { href: "/manufacturing", label: "Manufacturing" },
  { href: "/quality", label: "Quality" },
  { href: "/supply", label: "Supply Chain" },
  { href: "/sales", label: "Sales" },
  { href: "/regulatory", label: "Regulatory" },
  { href: "/costing", label: "Costing" },
  { href: "/botpharma", label: "BotPharma™" },
];
