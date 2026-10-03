"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Supply Chain (MRP, FEFO)" paths={[["MRP", "/api/v1/supply/mrp"], ["Customers", "/api/v1/customers"], ["Sales Orders", "/api/v1/sales/orders"]]} />;
}
