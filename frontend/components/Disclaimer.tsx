import { Info } from "lucide-react";

export function Disclaimer({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-500">
      <Info className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{text}</span>
    </div>
  );
}
