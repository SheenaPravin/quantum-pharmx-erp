"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Manufacturing & Batches" paths={[["Work Orders", "/api/v1/manufacturing/orders"], ["Batches & Genealogy", "/api/v1/batches"]]} />;
}
