"use client";

import type { Transaction } from "@/types";
import clsx from "clsx";

interface Props {
  transactions: Transaction[];
}

const CATEGORY_COLORS: Record<string, string> = {
  "Food & Dining": "bg-orange-100 text-orange-700",
  Groceries: "bg-green-100 text-green-700",
  Transport: "bg-blue-100 text-blue-700",
  Shopping: "bg-purple-100 text-purple-700",
  Subscriptions: "bg-pink-100 text-pink-700",
  "Gas & Fuel": "bg-yellow-100 text-yellow-700",
  Utilities: "bg-slate-100 text-slate-700",
  Income: "bg-emerald-100 text-emerald-700",
};

export default function TransactionList({ transactions }: Props) {
  if (!transactions.length) {
    return (
      <p className="text-slate-400 text-sm py-8 text-center">
        No transactions yet. Connect a bank account to get started.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b border-slate-100">
            <th className="pb-2 font-medium">Date</th>
            <th className="pb-2 font-medium">Name</th>
            <th className="pb-2 font-medium">Category</th>
            <th className="pb-2 font-medium text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((txn) => (
            <tr key={txn.id} className="border-b border-slate-50 hover:bg-slate-50">
              <td className="py-2.5 text-slate-500 whitespace-nowrap">
                {new Date(txn.date).toLocaleDateString()}
              </td>
              <td className="py-2.5 font-medium truncate max-w-[200px]">
                {txn.merchant_name || txn.name}
              </td>
              <td className="py-2.5">
                {txn.category && (
                  <span
                    className={clsx(
                      "text-xs px-2 py-0.5 rounded-full font-medium",
                      CATEGORY_COLORS[txn.category] ?? "bg-slate-100 text-slate-600"
                    )}
                  >
                    {txn.category}
                  </span>
                )}
              </td>
              <td
                className={clsx(
                  "py-2.5 text-right font-mono font-medium",
                  txn.is_credit ? "text-green-600" : "text-slate-800"
                )}
              >
                {txn.is_credit ? "+" : "-"}${txn.amount.toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
