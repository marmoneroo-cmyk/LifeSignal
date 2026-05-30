"use client";

import { cn } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import type { Priority } from "@/lib/types";

const PRIORITY_STYLES: Record<Priority, string> = {
  critical:      "bg-red-100 text-red-700 border-red-200",
  high:          "bg-orange-100 text-orange-700 border-orange-200",
  preventive:    "bg-teal-100 text-teal-700 border-teal-200",
  informational: "bg-slate-100 text-slate-600 border-slate-200",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  const { t } = useT();
  return (
    <span className={cn(
      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium shrink-0",
      PRIORITY_STYLES[priority],
    )}>
      {t(`priority.${priority}`)}
    </span>
  );
}

const STATUS_STYLES: Record<string, string> = {
  normal:     "bg-emerald-100 text-emerald-700",
  borderline: "bg-amber-100 text-amber-700",
  abnormal:   "bg-red-100 text-red-700",
};

export function StatusBadge({ status }: { status: string }) {
  const { t } = useT();
  return (
    <span className={cn(
      "rounded-full px-2 py-0.5 text-xs font-medium",
      STATUS_STYLES[status] ?? "bg-slate-100 text-slate-600",
    )}>
      {t(`status.${status}`) || status}
    </span>
  );
}
