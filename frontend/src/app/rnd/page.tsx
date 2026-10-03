"use client";
import { ModulePage } from "@/components/Module";
export default function P() {
  return <ModulePage title="R&D Management" paths={[["Projects", "/api/v1/rnd/projects"], ["Experiments", "/api/v1/rnd/experiments"], ["Milestones", "/api/v1/rnd/milestones"], ["Patents / IP", "/api/v1/rnd/patents"]]} />;
}
