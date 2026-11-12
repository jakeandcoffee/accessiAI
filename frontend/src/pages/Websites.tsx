import { useState } from "react";
import { motion } from "framer-motion";
import { Plus, Globe } from "lucide-react";
import { useWebsites, useDeleteWebsite } from "../hooks/useWebsites";
import { Button } from "../components/common/Button";
import { WebsiteCard } from "../components/websites/WebsiteCard";
import { AddWebsiteModal } from "../components/websites/AddWebsiteModal";
import { EmptyState } from "../components/common/EmptyState";
import { CardSkeleton } from "../components/common/Skeleton";

export function Websites() {
  const { data: websites, isLoading } = useWebsites();
  const deleteMutation = useDeleteWebsite();
  const [showAdd, setShowAdd] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h1 className="text-2xl font-bold text-ink">Websites</h1>
          <p className="text-sm text-muted mt-1">Manage and scan your websites</p>
        </motion.div>
        <Button onClick={() => setShowAdd(true)}>
          <Plus className="w-4 h-4" /> Add Website
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : websites && websites.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {websites.map((website, i) => (
            <WebsiteCard
              key={website.id}
              website={website}
              onDelete={(id) => deleteMutation.mutate(id)}
              index={i}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Globe}
          title="No websites yet"
          description="Add your first website to start scanning for accessibility issues."
          actionLabel="Add Website"
          onAction={() => setShowAdd(true)}
        />
      )}

      <AddWebsiteModal isOpen={showAdd} onClose={() => setShowAdd(false)} />
    </div>
  );
}
