"use client";

import { useState } from "react";
import Dashboard from "@/components/Dashboard";

export default function Home() {
  const [token, setToken] = useState<string | null>(
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null
  );

  if (!token) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-brand-700 mb-2">
            FinanciAlanalyst
          </h1>
          <p className="text-slate-500 text-lg">
            AI-powered personal finance insights
          </p>
        </div>
        <LoginForm onLogin={setToken} />
      </main>
    );
  }

  return <Dashboard token={token} onLogout={() => { localStorage.removeItem("access_token"); setToken(null); }} />;
}

function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"login" | "register">("login");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (mode === "register") {
        const res = await fetch("/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Registration failed");
        }
      }
      const form = new URLSearchParams();
      form.append("username", email);
      form.append("password", password);
      const res = await fetch("/api/v1/auth/token", { method: "POST", body: form });
      if (!res.ok) throw new Error("Invalid credentials");
      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      onLogin(data.access_token);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-sm bg-white rounded-2xl shadow-md p-8">
      <h2 className="text-xl font-semibold mb-6 text-center">
        {mode === "login" ? "Sign In" : "Create Account"}
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="bg-brand-600 hover:bg-brand-700 text-white font-medium py-2 rounded-lg disabled:opacity-50"
        >
          {loading ? "Loading..." : mode === "login" ? "Sign In" : "Create Account"}
        </button>
      </form>
      <p className="text-center text-sm text-slate-500 mt-4">
        {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
        <button
          className="text-brand-600 hover:underline"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "Register" : "Sign In"}
        </button>
      </p>
    </div>
  );
}
