"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Costing & Profitability" paths={[["Cost Records", "/api/v1/costing"]]} />;
}
