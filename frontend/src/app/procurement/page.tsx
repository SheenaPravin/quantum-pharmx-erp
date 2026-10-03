"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Procurement" paths={[["Suppliers", "/api/v1/suppliers"], ["Requisitions", "/api/v1/procurement/requisitions"], ["Purchase Orders", "/api/v1/procurement/orders"], ["Goods Receipts", "/api/v1/procurement/receipts"]]} />;
}
