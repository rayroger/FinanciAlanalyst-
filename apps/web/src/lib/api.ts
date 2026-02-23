/**
 * Axios API client with JWT token injection.
 */

import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Inject JWT on every request
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// API methods
export const api = {
  getTransactions: (params?: {
    start_date?: string;
    end_date?: string;
    category?: string;
    limit?: number;
    offset?: number;
  }) => apiClient.get("/transactions", { params }),

  getInsights: () => apiClient.get("/insights"),

  createLinkToken: () => apiClient.post("/plaid/link-token"),

  exchangeToken: (public_token: string, institution_name?: string) =>
    apiClient.post("/plaid/exchange-token", { public_token, institution_name }),

  syncTransactions: () => apiClient.post("/plaid/sync"),
};
