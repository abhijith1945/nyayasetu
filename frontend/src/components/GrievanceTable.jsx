import React, { useState } from "react";
import UrgencyBadge from "./UrgencyBadge";
import LoadingSpinner from "./LoadingSpinner";

const STATUS_STYLES = {
  open: "bg-blue-100 text-blue-700",
  resolved: "bg-green-100 text-green-700",
  breached: "bg-red-100 text-red-700",
  reopened: "bg-orange-100 text-orange-700",
  closed: "bg-gray-100 text-gray-600",
};

const SORTABLE_KEYS = ["urgency", "category", "ward", "status"];

export default function GrievanceTable({
  grievances = [],
  onResolve,
  loading = false,
}) {
  const [sortKey, setSortKey] = useState("urgency");
  const [sortAsc, setSortAsc] = useState(false); // default descending for urgency
  const [filterCategory, setFilterCategory] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  /* ── Derive unique values for filter dropdowns ── */
  const categories = [
    ...new Set(grievances.map((g) => g?.category).filter(Boolean)),
  ];
  const statuses = [
    ...new Set(grievances.map((g) => g?.status).filter(Boolean)),
  ];

  /* ── Filter ── */
  let filtered = grievances.filter((g) => {
    if (filterCategory && g?.category !== filterCategory) return false;
    if (filterStatus && g?.status !== filterStatus) return false;
    return true;
  });

  /* ── Sort ── */
  filtered = [...filtered].sort((a, b) => {
    const aVal = a?.[sortKey] ?? "";
    const bVal = b?.[sortKey] ?? "";
    if (typeof aVal === "number" && typeof bVal === "number") {
      return sortAsc ? aVal - bVal : bVal - aVal;
    }
    const cmp = String(aVal).localeCompare(String(bVal));
    return sortAsc ? cmp : -cmp;
  });

  /* ── Sort toggle handler ── */
  const handleSort = (key) => {
    if (sortKey === key) {
      setSortAsc((prev) => !prev);
    } else {
      setSortKey(key);
      setSortAsc(key !== "urgency"); // urgency defaults descending
    }
  };

  const sortIndicator = (key) => {
    if (sortKey !== key) return "";
    return sortAsc ? " \u25B2" : " \u25BC";
  };

  const canResolve = (status) =>
    status === "open" || status === "breached" || status === "reopened";

  if (loading) {
    return <LoadingSpinner message="Loading grievances..." />;
  }

  return (
    <div className="space-y-3">
      {/* ── Filter bar ── */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-body text-gray-700 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-body text-gray-700 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
        >
          <option value="">All Statuses</option>
          {statuses.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <span className="ml-auto text-xs text-gray-400 font-body">
          {filtered.length} grievance{filtered.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* ── Table ── */}
      <div className="table-scroll rounded-lg border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-sm font-body">
          <thead className="bg-gray-50">
            <tr>
              {[
                { key: "urgency", label: "Urgency" },
                { key: "category", label: "Category" },
                { key: "ward", label: "Ward" },
                { key: null, label: "Summary" },
                { key: "status", label: "Status" },
                { key: null, label: "Actions" },
              ].map(({ key, label }, idx) => (
                <th
                  key={idx}
                  className={`whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 ${
                    key ? "cursor-pointer select-none hover:text-navy" : ""
                  }`}
                  onClick={key ? () => handleSort(key) : undefined}
                >
                  {label}
                  {key ? sortIndicator(key) : ""}
                </th>
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-100">
            {filtered.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-gray-400"
                >
                  No grievances found.
                </td>
              </tr>
            ) : (
              filtered.map((g, idx) => {
                const status = g?.status || "open";
                const statusStyle =
                  STATUS_STYLES[status] || STATUS_STYLES.open;

                return (
                  <tr
                    key={g?.id || idx}
                    className="transition-colors hover:bg-gray-50"
                  >
                    {/* Urgency */}
                    <td className="whitespace-nowrap px-4 py-3">
                      <UrgencyBadge level={g?.urgency} />
                    </td>

                    {/* Category */}
                    <td className="whitespace-nowrap px-4 py-3 text-gray-700">
                      {g?.category || "--"}
                    </td>

                    {/* Ward */}
                    <td className="whitespace-nowrap px-4 py-3 text-gray-700">
                      {g?.ward ?? "--"}
                    </td>

                    {/* Summary */}
                    <td className="max-w-xs truncate px-4 py-3 text-gray-600">
                      {g?.summary || g?.description || "--"}
                    </td>

                    {/* Status */}
                    <td className="whitespace-nowrap px-4 py-3">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${statusStyle}`}
                      >
                        {status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="whitespace-nowrap px-4 py-3">
                      {canResolve(status) && onResolve ? (
                        <button
                          onClick={() => onResolve(g?.id)}
                          className="rounded-md bg-accent px-3 py-1 text-xs font-semibold text-white transition-colors hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-1"
                        >
                          Resolve
                        </button>
                      ) : (
                        <span className="text-xs text-gray-400">--</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
