"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Regulatory" paths={[["Registrations", "/api/v1/regulatory/registrations"], ["Submissions", "/api/v1/regulatory/submissions"]]} />;
}
