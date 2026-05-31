"use client";

import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, ReferenceArea, ReferenceLine, CartesianGrid,
} from "recharts";
import type { TrendPoint } from "@/lib/types";

interface MarkerChartProps {
  label: string;
  unit: string;
  points: TrendPoint[];
  status: string;
  /** Optional normal range — drawn as a green band so context is visible at a glance. */
  refLow?: number | null;
  refHigh?: number | null;
}

const STROKE_BY_STATUS: Record<string, string> = {
  normal:     "#0d9488",  // brand teal
  borderline: "#d97706",  // amber
  abnormal:   "#dc2626",  // red
};

export function MarkerChart({ label, unit, points, status, refLow, refHigh }: MarkerChartProps) {
  if (points.length === 0) return null;
  if (points.length === 1) {
    return (
      <div className="rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500">
        קריאה בודדת: {points[0].value} {unit} ({points[0].taken_on})
      </div>
    );
  }

  const stroke = STROKE_BY_STATUS[status] ?? "#0d9488";
  const data = points.map((p) => ({
    date: p.taken_on,
    value: p.value,
  }));

  // Compute Y axis padding so the reference band has room above/below.
  const values = points.map((p) => p.value);
  const dataMin = Math.min(...values, refLow ?? Infinity);
  const dataMax = Math.max(...values, refHigh ?? -Infinity);
  const padding = (dataMax - dataMin) * 0.15 || 1;

  return (
    <div className="h-44 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10, fill: "#94a3b8" }}
            tickLine={false}
            axisLine={{ stroke: "#e2e8f0" }}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "#94a3b8" }}
            tickLine={false}
            axisLine={{ stroke: "#e2e8f0" }}
            domain={[Math.floor(dataMin - padding), Math.ceil(dataMax + padding)]}
            width={36}
          />
          <Tooltip
            contentStyle={{
              fontSize: 12,
              borderRadius: 8,
              border: "1px solid #e2e8f0",
              boxShadow: "0 4px 6px rgba(0,0,0,0.05)",
            }}
            labelStyle={{ color: "#64748b", fontSize: 11 }}
            formatter={(v) => [`${v} ${unit}`, label]}
          />
          {/* Normal-range band */}
          {refLow !== null && refLow !== undefined && refHigh !== null && refHigh !== undefined && (
            <ReferenceArea y1={refLow} y2={refHigh} fill="#10b981" fillOpacity={0.07} stroke="none" />
          )}
          {refLow !== null && refLow !== undefined && (
            <ReferenceLine y={refLow} stroke="#10b981" strokeDasharray="3 3" strokeWidth={1} />
          )}
          {refHigh !== null && refHigh !== undefined && (
            <ReferenceLine y={refHigh} stroke="#10b981" strokeDasharray="3 3" strokeWidth={1} />
          )}
          <Line
            type="monotone"
            dataKey="value"
            stroke={stroke}
            strokeWidth={2.5}
            dot={{ r: 3.5, fill: stroke }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
