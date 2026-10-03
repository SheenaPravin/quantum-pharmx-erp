"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Sales & Customers" paths={[["Customers", "/api/v1/customers"], ["Sales Orders", "/api/v1/sales/orders"]]} />;
}
