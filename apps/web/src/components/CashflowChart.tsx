"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { CashflowMonth } from "@/types";

interface Props {
  data: CashflowMonth[];
}

const formatMonth = (value: string) => {
  const [year, month] = value.split("-");
  return new Date(parseInt(year), parseInt(month) - 1).toLocaleString("default", {
    month: "short",
    year: "2-digit",
  });
};

const formatDollar = (value: number) => `$${value.toFixed(0)}`;

export default function CashflowChart({ data }: Props) {
  if (!data.length) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400">
        No cashflow data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          dataKey="month"
          tickFormatter={formatMonth}
          tick={{ fontSize: 12, fill: "#64748b" }}
        />
        <YAxis tickFormatter={formatDollar} tick={{ fontSize: 12, fill: "#64748b" }} />
        <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
        <Legend />
        <Bar dataKey="income" name="Income" fill="#22c55e" radius={[4, 4, 0, 0]} />
        <Bar dataKey="expenses" name="Expenses" fill="#f97316" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
