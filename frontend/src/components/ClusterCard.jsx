import React, { useState } from "react";

export default function ClusterCard({ cluster }) {
  const [expanded, setExpanded] = useState(false);

  const category = cluster?.category || "Unknown";
  const ward = cluster?.ward ?? "--";
  const count = cluster?.count ?? 0;
  const summary = cluster?.summary || "No summary available.";
  const members = cluster?.members || [];

  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md">
      {/* ── Header ── */}
      <div className="flex items-start gap-4 p-5">
        {/* Category icon / tag */}
        <span className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/10 text-lg">
          {getCategoryIcon(category)}
        </span>

        <div className="min-w-0 flex-1">
          {/* Category & Ward row */}
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-navy/10 px-2.5 py-0.5 text-xs font-semibold text-navy font-body">
              {category}
            </span>
            <span className="text-xs text-gray-400 font-body">
              Ward {ward}
            </span>
          </div>

          {/* Count */}
          <p className="mb-1 font-heading text-lg font-bold text-navy">
            {count} complaint{count !== 1 ? "s" : ""}
          </p>

          {/* Summary */}
          <p className="text-sm text-gray-600 font-body leading-relaxed">
            {summary}
          </p>
        </div>
      </div>

      {/* ── Expandable members section ── */}
      {members.length > 0 && (
        <div className="border-t border-gray-100">
          <button
            onClick={() => setExpanded((prev) => !prev)}
            className="flex w-full items-center justify-between px-5 py-3 text-sm font-medium text-accent font-body hover:bg-gray-50 transition-colors focus:outline-none"
            aria-expanded={expanded}
          >
            <span>
              View Members ({members.length})
            </span>
            <svg
              className={`h-4 w-4 transform transition-transform ${
                expanded ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          {expanded && (
            <ul className="divide-y divide-gray-50 px-5 pb-4">
              {members.map((member, idx) => {
                const memberId = member?.id || member;
                const memberSummary =
                  member?.summary || member?.description || String(memberId);

                return (
                  <li
                    key={memberId || idx}
                    className="flex items-start gap-2 py-2 text-sm font-body"
                  >
                    <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                    <span className="text-gray-600">
                      {typeof memberId === "string" && memberId.length > 8 ? (
                        <span className="mr-1 font-mono text-xs text-gray-400">
                          {memberId.slice(0, 8)}
                        </span>
                      ) : null}
                      {memberSummary}
                    </span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

/* ── Helper: Map category names to emoji icons ── */
function getCategoryIcon(category) {
  const lower = (category || "").toLowerCase();
  if (lower.includes("water") || lower.includes("sanitation")) return "\uD83D\uDCA7";
  if (lower.includes("road") || lower.includes("transport")) return "\uD83D\uDEE3\uFE0F";
  if (lower.includes("electric") || lower.includes("power") || lower.includes("energy")) return "\u26A1";
  if (lower.includes("health") || lower.includes("hospital")) return "\uD83C\uDFE5";
  if (lower.includes("education") || lower.includes("school")) return "\uD83C\uDF93";
  if (lower.includes("corruption") || lower.includes("bribe")) return "\uD83D\uDEA8";
  if (lower.includes("housing") || lower.includes("shelter")) return "\uD83C\uDFE0";
  if (lower.includes("law") || lower.includes("police") || lower.includes("crime")) return "\u2696\uFE0F";
  if (lower.includes("environment") || lower.includes("pollution")) return "\uD83C\uDF3F";
  return "\uD83D\uDCCB";
}
