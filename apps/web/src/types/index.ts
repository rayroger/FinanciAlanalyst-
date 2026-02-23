/**
 * Shared TypeScript types matching the backend Pydantic schemas.
 */

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Account {
  id: string;
  plaid_account_id: string;
  institution_name?: string;
  account_name?: string;
  account_type?: string;
  account_subtype?: string;
  created_at: string;
}

export interface Transaction {
  id: string;
  account_id: string;
  plaid_transaction_id: string;
  amount: number;
  is_credit: boolean;
  date: string;
  merchant_name?: string;
  name: string;
  category?: string;
  pending: boolean;
}

export interface AnomalyItem {
  category: string;
  current_month_spend: number;
  previous_month_spend: number;
  pct_change: number;
  description: string;
}

export interface InsightResult {
  monthly_summary: string;
  top_categories: { category: string; total: number }[];
  anomalies: AnomalyItem[];
  recurring_subscriptions: string[];
  generated_at: string;
}

export interface CashflowMonth {
  month: string;
  income: number;
  expenses: number;
}
