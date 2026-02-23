"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Transaction, InsightResult, CashflowMonth } from "@/types";
import CashflowChart from "./CashflowChart";
import CategoryBreakdown from "./CategoryBreakdown";
import TransactionList from "./TransactionList";
import InsightCard from "./InsightCard";
import PlaidLink from "./PlaidLink";

interface Props {
  token: string;
  onLogout: () => void;
}

export default function Dashboard({ token, onLogout }: Props) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [insights, setInsights] = useState<InsightResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [txRes, insRes] = await Promise.all([
        api.getTransactions({ limit: 200 }),
        api.getInsights(),
      ]);
      setTransactions(txRes.data);
      setInsights(insRes.data);
    } catch {
      // silently handle — user may not have connected a bank yet
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await api.syncTransactions();
      await loadData();
    } finally {
      setSyncing(false);
    }
  };

  const cashflow = buildCashflow(transactions);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-brand-700">FinanciAlanalyst</h1>
        <div className="flex items-center gap-3">
          <PlaidLink onSuccess={handleSync} />
          <button
            onClick={handleSync}
            disabled={syncing}
            className="text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg disabled:opacity-50"
          >
            {syncing ? "Syncing…" : "Sync"}
          </button>
          <button
            onClick={onLogout}
            className="text-sm text-slate-500 hover:text-slate-700 px-3 py-1.5"
          >
            Sign Out
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {loading ? (
          <div className="flex items-center justify-center h-48 text-slate-400">
            Loading your financial data…
          </div>
        ) : (
          <>
            {/* AI Insights */}
            {insights && (
              <section>
                <h2 className="text-lg font-semibold text-slate-700 mb-4">AI Insights</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <InsightCard
                    title="Monthly Summary"
                    body={insights.monthly_summary}
                    icon="📊"
                  />
                  {insights.anomalies.map((a, i) => (
                    <InsightCard
                      key={i}
                      title={`Anomaly: ${a.category}`}
                      body={a.description}
                      icon="⚠️"
                      variant="warning"
                    />
                  ))}
                  {insights.recurring_subscriptions.length > 0 && (
                    <InsightCard
                      title="Recurring Subscriptions"
                      body={insights.recurring_subscriptions.join(", ")}
                      icon="🔄"
                    />
                  )}
                </div>
              </section>
            )}

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-slate-700 mb-4">
                  Cash Flow (Last 6 Months)
                </h2>
                <CashflowChart data={cashflow} />
              </div>
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-slate-700 mb-4">
                  Spending by Category
                </h2>
                <CategoryBreakdown
                  categories={insights?.top_categories ?? buildCategories(transactions)}
                />
              </div>
            </div>

            {/* Transactions */}
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-slate-700 mb-4">
                Recent Transactions
              </h2>
              <TransactionList transactions={transactions.slice(0, 50)} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function buildCashflow(transactions: Transaction[]): CashflowMonth[] {
  const map: Record<string, { income: number; expenses: number }> = {};
  const now = new Date();
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const key = d.toISOString().slice(0, 7);
    map[key] = { income: 0, expenses: 0 };
  }
  transactions.forEach((t) => {
    const key = t.date.slice(0, 7);
    if (!map[key]) return;
    if (t.is_credit) map[key].income += t.amount;
    else map[key].expenses += t.amount;
  });
  return Object.entries(map).map(([month, v]) => ({ month, ...v }));
}

function buildCategories(transactions: Transaction[]): { category: string; total: number }[] {
  const map: Record<string, number> = {};
  transactions
    .filter((t) => !t.is_credit)
    .forEach((t) => {
      const cat = t.category ?? "Other";
      map[cat] = (map[cat] ?? 0) + t.amount;
    });
  return Object.entries(map)
    .map(([category, total]) => ({ category, total }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 6);
}
