"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Inventory (FEFO, lots, expiry)" paths={[["Materials", "/api/v1/materials"], ["Stock Lots", "/api/v1/inventory/lots"], ["Movements", "/api/v1/inventory/moves"]]} />;
}
