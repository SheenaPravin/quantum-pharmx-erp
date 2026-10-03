"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="Quality (QC, OOS, Deviations, CAPA)" paths={[["Specifications", "/api/v1/quality/specs"], ["QC Results", "/api/v1/quality/results"], ["Deviations", "/api/v1/quality/deviations"], ["CAPAs", "/api/v1/quality/capas"]]} />;
}
