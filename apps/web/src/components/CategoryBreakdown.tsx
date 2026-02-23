"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface CategoryData {
  category: string;
  total: number;
}

interface Props {
  categories: CategoryData[];
}

const COLORS = [
  "#0ea5e9",
  "#f97316",
  "#22c55e",
  "#a855f7",
  "#f59e0b",
  "#ef4444",
  "#14b8a6",
];

const formatDollar = (value: number) => `$${value.toFixed(0)}`;

export default function CategoryBreakdown({ categories }: Props) {
  if (!categories.length) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400">
        No category data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={categories}
          dataKey="total"
          nameKey="category"
          cx="50%"
          cy="50%"
          outerRadius={90}
          innerRadius={50}
          paddingAngle={3}
        >
          {categories.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => formatDollar(value)} />
        <Legend
          formatter={(value) => (
            <span className="text-xs text-slate-600">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
