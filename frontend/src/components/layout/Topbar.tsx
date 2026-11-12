import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Bell, LogOut, User, Menu, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import api from "../../services/api";
import type { Scan } from "../../types";

interface TopbarProps {
  onMobileMenuToggle: () => void;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export function Topbar({ onMobileMenuToggle }: TopbarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const [showNotifs, setShowNotifs] = useState(false);
  const [dismissed, setDismissed] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem("accessiai_dismissed_notifs");
      return stored ? new Set(JSON.parse(stored)) : new Set();
    } catch {
      return new Set();
    }
  });
  const menuRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);

  const { data: scans } = useQuery({
    queryKey: ["recent-scans-notifs"],
    queryFn: async () => {
      const { data } = await api.get<Scan[]>("/api/scans");
      return data.slice(0, 10);
    },
    refetchInterval: 15000,
  });

  const unreadCount = scans?.filter((s) => !dismissed.has(s.id)).length ?? 0;

  function markAllRead() {
    if (!scans) return;
    const ids = new Set([...dismissed, ...scans.map((s) => s.id)]);
    setDismissed(ids);
    localStorage.setItem("accessiai_dismissed_notifs", JSON.stringify([...ids]));
  }

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowMenu(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotifs(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <header className="sticky top-0 z-20 bg-black/30 backdrop-blur-xl border-b border-white/[0.06]">
      <div className="flex items-center justify-between h-16 px-6">
        <button
          onClick={onMobileMenuToggle}
          className="lg:hidden rounded-lg p-2 text-muted hover:bg-white/5"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex-1" />

        <div className="flex items-center gap-3">
          <div className="relative" ref={notifRef}>
            <button
              onClick={() => setShowNotifs(!showNotifs)}
              className="relative rounded-lg p-2 text-muted hover:bg-white/5 transition-colors"
              aria-label="Notifications"
              aria-expanded={showNotifs}
              aria-haspopup="true"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 min-w-[18px] h-[18px] rounded-full bg-brand text-[10px] font-bold text-white flex items-center justify-center px-1">
                  {unreadCount}
                </span>
              )}
            </button>

            {showNotifs && (
              <div className="absolute right-0 top-full mt-2 w-80 rounded-xl border border-white/10 bg-black/80 backdrop-blur-xl shadow-2xl z-50 overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
                  <p className="text-sm font-semibold text-ink">Notifications</p>
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllRead}
                      className="text-xs text-brand hover:text-brand-light transition-colors"
                    >
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {scans && scans.length > 0 ? (
                    scans.map((scan) => {
                      const isUnread = !dismissed.has(scan.id);
                      return (
                        <button
                          key={scan.id}
                          onClick={() => {
                            navigate(`/scans/${scan.id}`);
                            setShowNotifs(false);
                          }}
                          className={`w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-white/5 transition-colors border-b border-white/[0.04] last:border-0 ${isUnread ? "bg-white/[0.03]" : ""}`}
                        >
                          <div className="mt-0.5">
                            {scan.status === "completed" ? (
                              <CheckCircle className="w-4 h-4 text-green-400" />
                            ) : scan.status === "failed" ? (
                              <XCircle className="w-4 h-4 text-red-400" />
                            ) : (
                              <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm truncate ${isUnread ? "text-ink font-medium" : "text-muted"}`}>
                              {scan.website_name || "Scan"}{" "}
                              <span className="text-muted font-normal">
                                — {scan.status === "completed" ? `Score: ${Math.round(scan.accessibility_score ?? 0)}` : scan.status}
                              </span>
                            </p>
                            <p className="text-xs text-muted mt-0.5">
                              {scan.total_violations} violations · {timeAgo(scan.scan_started_at)}
                            </p>
                          </div>
                          {isUnread && (
                            <span className="mt-1.5 w-2 h-2 rounded-full bg-brand flex-shrink-0" />
                          )}
                        </button>
                      );
                    })
                  ) : (
                    <div className="px-4 py-8 text-center">
                      <Bell className="w-8 h-8 text-muted/40 mx-auto mb-2" />
                      <p className="text-sm text-muted">No notifications yet</p>
                      <p className="text-xs text-muted/60 mt-1">Scan a website to get started</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="flex items-center gap-2 rounded-lg px-3 py-1.5 hover:bg-white/5 transition-colors"
              aria-expanded={showMenu}
              aria-haspopup="true"
            >
              <div className="w-8 h-8 rounded-full bg-brand/20 border border-brand/30 flex items-center justify-center">
                <User className="w-4 h-4 text-brand" />
              </div>
              <span className="text-sm font-medium text-ink hidden sm:block">
                {user?.full_name}
              </span>
            </button>

            {showMenu && (
              <div className="absolute right-0 top-full mt-2 w-48 rounded-xl border border-white/10 bg-black/60 backdrop-blur-xl shadow-2xl py-1 z-50">
                <div className="px-4 py-2 border-b border-white/[0.06]">
                  <p className="text-sm font-medium text-ink">{user?.full_name}</p>
                  <p className="text-xs text-muted truncate">{user?.email}</p>
                </div>
                <button
                  onClick={logout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-white/5 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
