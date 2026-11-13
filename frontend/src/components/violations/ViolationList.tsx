import { useState, useMemo } from "react";
import {
  Database, Accessibility, Search, LayoutDashboard, BarChart3, Target, FileText,
} from "lucide-react";
import { ViolationCard } from "./ViolationCard";
import { ViolationFilters } from "./ViolationFilters";
import type { Violation } from "../../types";

interface ViolationListProps {
  violations: Violation[];
  /** When set, violations are grouped into one section per page, in this order. */
  pageOrder?: string[];
  defaultPageUrl?: string;
}

const CATEGORY_CONFIG: Record<string, { label: string; icon: typeof Database; color: string }> = {
  "accessibility": { label: "Phase 2: Accessibility (WCAG 2.2 AA + Section 508)", icon: Accessibility, color: "text-red-400" },
  "data-quality": { label: "Phase 1: Data Quality & Measurement", icon: Database, color: "text-orange-400" },
  "geo": { label: "Phase 3: GEO (Generative Engine Optimization)", icon: Search, color: "text-purple-400" },
  "ux-performance": { label: "Phase 4: UX & Performance", icon: LayoutDashboard, color: "text-blue-400" },
  "seo": { label: "Phase 5: SEO & Discoverability", icon: BarChart3, color: "text-green-400" },
  "baseline": { label: "Phase 6: Baseline & Measurement", icon: Target, color: "text-cyan-400" },
};

const CATEGORY_ORDER = ["data-quality", "accessibility", "geo", "ux-performance", "seo", "baseline"];

function groupByCategory(violations: Violation[]) {
  const groups: Record<string, Violation[]> = {};
  for (const v of violations) {
    const cat = v.category || "accessibility";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(v);
  }
  const extra = Object.keys(groups).filter((cat) => !CATEGORY_ORDER.includes(cat)).sort();
  return [...CATEGORY_ORDER, ...extra]
    .filter((cat) => groups[cat]?.length > 0)
    .map((cat) => ({ category: cat, violations: groups[cat] }));
}

export function ViolationList({ violations, pageOrder, defaultPageUrl = "" }: ViolationListProps) {
  const [search, setSearch] = useState("");
  const [impactFilter, setImpactFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const filtered = useMemo(() => {
    return violations.filter((v) => {
      const matchesSearch =
        !search ||
        v.rule_id.toLowerCase().includes(search.toLowerCase()) ||
        v.description.toLowerCase().includes(search.toLowerCase());
      const matchesImpact = !impactFilter || v.impact === impactFilter;
      const matchesStatus = !statusFilter || v.status === statusFilter;
      return matchesSearch && matchesImpact && matchesStatus;
    });
  }, [violations, search, impactFilter, statusFilter]);

  const pageGroups = useMemo(() => {
    if (!pageOrder) {
      return [{ pageUrl: null as string | null, categories: groupByCategory(filtered) }];
    }
    const byPage: Record<string, Violation[]> = {};
    for (const v of filtered) {
      const page = v.page_url || defaultPageUrl;
      if (!byPage[page]) byPage[page] = [];
      byPage[page].push(v);
    }
    const extra = Object.keys(byPage).filter((p) => !pageOrder.includes(p));
    return [...pageOrder, ...extra]
      .filter((page) => byPage[page]?.length > 0)
      .map((page) => ({ pageUrl: page as string | null, categories: groupByCategory(byPage[page]) }));
  }, [filtered, pageOrder, defaultPageUrl]);

  return (
    <div>
      <ViolationFilters
        search={search}
        onSearchChange={setSearch}
        impactFilter={impactFilter}
        onImpactChange={setImpactFilter}
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
      />

      {filtered.length > 0 ? (
        <div className="space-y-8">
          {pageGroups.map(({ pageUrl, categories }) => (
            <section key={pageUrl ?? "all"} aria-label={pageUrl ? `Findings for ${pageUrl}` : undefined}>
              {pageUrl && (
                <div className="flex items-center gap-2 mb-4 rounded-lg border border-brand/30 bg-brand/[0.06] px-3 py-2">
                  <FileText className="w-4 h-4 text-brand shrink-0" />
                  <h3 className="text-sm font-semibold text-ink font-mono truncate">{pageUrl}</h3>
                  <span className="ml-auto text-xs text-muted bg-white/[0.06] px-2 py-0.5 rounded-full whitespace-nowrap">
                    {categories.reduce((n, c) => n + c.violations.length, 0)} issues
                  </span>
                </div>
              )}
              <div className="space-y-6">
                {categories.map(({ category, violations: catViolations }) => {
                  const config = CATEGORY_CONFIG[category] || {
                    label: category,
                    icon: Database,
                    color: "text-muted",
                  };
                  const Icon = config.icon;

                  return (
                    <div key={category}>
                      <div className="flex items-center gap-2 mb-3">
                        <Icon className={`w-4 h-4 ${config.color}`} />
                        <h3 className={`text-sm font-bold uppercase tracking-wider ${config.color}`}>
                          {config.label}
                        </h3>
                        <span className="text-xs text-muted bg-white/[0.06] px-2 py-0.5 rounded-full">
                          {catViolations.length}
                        </span>
                        <div className="flex-1 h-px bg-white/[0.06]" />
                      </div>
                      <div className="space-y-3">
                        {catViolations.map((violation, i) => (
                          <ViolationCard key={violation.id} violation={violation} index={i} />
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      ) : (
        <p className="text-center text-muted py-8 text-sm">No violations match your filters.</p>
      )}
    </div>
  );
}
