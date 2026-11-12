import { useState } from "react";
import { Outlet } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-surface-dim">
      {/* Desktop sidebar */}
      <div className="hidden lg:block">
        <Sidebar
          isCollapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
            <div className="lg:hidden z-50 fixed left-0 top-0">
              <Sidebar isCollapsed={false} onToggle={() => setMobileMenuOpen(false)} onNavigate={() => setMobileMenuOpen(false)} />
            </div>
          </>
        )}
      </AnimatePresence>

      {/* Main content — desktop only */}
      <motion.div
        animate={{ marginLeft: sidebarCollapsed ? 72 : 256 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="min-h-screen hidden lg:block"
      >
        <Topbar onMobileMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)} />
        <main className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
        <footer className="px-6 py-4 text-center text-xs text-muted border-t border-border/40">
          Designed & Built by Jake Huang &copy; {new Date().getFullYear()}
        </footer>
      </motion.div>

      {/* Mobile: no sidebar margin */}
      <div className="lg:hidden">
        <Topbar onMobileMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)} />
        <main className="p-4">
          <Outlet />
        </main>
        <footer className="px-4 py-4 text-center text-xs text-muted border-t border-border/40">
          Designed & Built by Jake Huang &copy; {new Date().getFullYear()}
        </footer>
      </div>
    </div>
  );
}
