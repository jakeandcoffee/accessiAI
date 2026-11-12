import { useNavigate } from "react-router-dom";
import { Radar } from "lucide-react";
import { Button } from "../common/Button";
import { useTriggerScan } from "../../hooks/useScans";

interface ScanButtonProps {
  websiteId: string;
}

export function ScanButton({ websiteId }: ScanButtonProps) {
  const { mutate, isPending } = useTriggerScan();
  const navigate = useNavigate();

  return (
    <Button
      size="sm"
      className="flex-1 relative overflow-hidden"
      onClick={() =>
        mutate(websiteId, {
          onSuccess: (scan) => {
            navigate(`/scans/${scan.id}`);
          },
        })
      }
      isLoading={isPending}
    >
      {isPending && (
        <span className="absolute inset-0 rounded-lg border-2 border-white/30 animate-pulse-ring" />
      )}
      <Radar className="w-4 h-4" />
      {isPending ? "Starting..." : "Scan"}
    </Button>
  );
}
