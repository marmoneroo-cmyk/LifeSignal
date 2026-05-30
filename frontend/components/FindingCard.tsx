import { PriorityBadge } from "@/components/ui/badge";
import type { Finding } from "@/lib/types";

export function FindingCard({ finding }: { finding: Finding }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <h4 className="font-semibold text-slate-800">{finding.title}</h4>
        <PriorityBadge priority={finding.priority} />
      </div>
      {finding.plain_language && (
        <p className="mt-1.5 text-sm text-slate-700">{finding.plain_language}</p>
      )}
      <p className="mt-1 text-xs text-slate-400">{finding.detail}</p>
    </div>
  );
}
