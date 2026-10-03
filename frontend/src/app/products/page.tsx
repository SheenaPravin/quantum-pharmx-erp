"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Product & Formulation" paths={[["Products", "/api/v1/products"], ["Formulations / BOMs", "/api/v1/formulations"]]} />;
}
