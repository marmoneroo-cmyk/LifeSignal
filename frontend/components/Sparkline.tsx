import type { TrendPoint } from "@/lib/types";

export function Sparkline({ points, stroke = "#0d9488" }: { points: TrendPoint[]; stroke?: string }) {
  if (points.length < 2) return <span className="text-xs text-slate-400">single reading</span>;
  const w = 120;
  const h = 36;
  const values = points.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const coords = points.map((p, i) => {
    const x = (i / (points.length - 1)) * w;
    const y = h - ((p.value - min) / span) * h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return (
    <svg width={w} height={h} className="overflow-visible">
      <polyline points={coords.join(" ")} fill="none" stroke={stroke} strokeWidth="2" />
      {coords.map((c, i) => {
        const [x, y] = c.split(",");
        return <circle key={i} cx={x} cy={y} r="2" fill={stroke} />;
      })}
    </svg>
  );
}
