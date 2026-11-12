import { motion } from "framer-motion";
import { User, Mail, Shield } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { Card } from "../components/common/Card";

export function SettingsPage() {
  const { user } = useAuth();

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-6">
        <h1 className="text-2xl font-bold text-ink">Settings</h1>
        <p className="text-sm text-muted mt-1">Manage your account</p>
      </motion.div>

      <div className="max-w-2xl space-y-6">
        <Card hoverable={false}>
          <h2 className="text-lg font-bold text-ink mb-4">Profile</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-4 p-4 rounded-lg bg-white/[0.03] border border-white/[0.06]">
              <div className="w-12 h-12 rounded-full bg-brand/10 border border-brand/20 flex items-center justify-center">
                <User className="w-6 h-6 text-brand" />
              </div>
              <div>
                <p className="font-medium text-ink">{user?.full_name}</p>
                <p className="text-sm text-muted flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5" /> {user?.email}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 rounded-lg bg-white/[0.03] border border-white/[0.06]">
              <Shield className="w-5 h-5 text-muted" />
              <div>
                <p className="text-sm font-medium text-ink">Role</p>
                <p className="text-sm text-muted capitalize">{user?.role}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 rounded-lg bg-white/[0.03] border border-white/[0.06]">
              <div>
                <p className="text-sm font-medium text-ink">Member since</p>
                <p className="text-sm text-muted">
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })
                    : "—"}
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
