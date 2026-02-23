"use client";

import clsx from "clsx";

interface Props {
  title: string;
  body: string;
  icon?: string;
  variant?: "default" | "warning";
}

export default function InsightCard({
  title,
  body,
  icon = "💡",
  variant = "default",
}: Props) {
  return (
    <div
      className={clsx(
        "rounded-2xl p-5 shadow-sm border",
        variant === "warning"
          ? "bg-amber-50 border-amber-200"
          : "bg-white border-slate-200"
      )}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h3 className="font-semibold text-slate-700 text-sm mb-1">{title}</h3>
          <p className="text-slate-600 text-sm leading-relaxed">{body}</p>
        </div>
      </div>
    </div>
  );
}
