import { Search } from "lucide-react";

interface ViolationFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  impactFilter: string;
  onImpactChange: (value: string) => void;
  statusFilter: string;
  onStatusChange: (value: string) => void;
}

export function ViolationFilters({
  search,
  onSearchChange,
  impactFilter,
  onImpactChange,
  statusFilter,
  onStatusChange,
}: ViolationFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-3 mb-4">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
        <input
          type="search"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by rule ID or description..."
          className="w-full rounded-lg border border-white/10 bg-white/[0.04] pl-9 pr-3 py-2 text-sm text-ink placeholder:text-muted/50 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand/50"
          aria-label="Search violations"
        />
      </div>
      <select
        value={impactFilter}
        onChange={(e) => onImpactChange(e.target.value)}
        className="rounded-lg border border-white/10 bg-white/[0.04] text-ink px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
        aria-label="Filter by impact"
      >
        <option value="">All Severities</option>
        <option value="critical">Critical</option>
        <option value="serious">Serious</option>
        <option value="moderate">Moderate</option>
        <option value="minor">Minor</option>
      </select>
      <select
        value={statusFilter}
        onChange={(e) => onStatusChange(e.target.value)}
        className="rounded-lg border border-white/10 bg-white/[0.04] text-ink px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
        aria-label="Filter by status"
      >
        <option value="">All Statuses</option>
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="resolved">Resolved</option>
        <option value="ignored">Ignored</option>
      </select>
    </div>
  );
}
