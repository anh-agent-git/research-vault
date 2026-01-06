"use client";

import { useEffect, useState } from "react";
import { getHealth, type HealthStatus } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Database,
  Server,
  Users,
  Activity,
} from "lucide-react";

function StatusBadge({ status }: { status: "ok" | "error" | "degraded" }) {
  const colors = {
    ok: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    error: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    degraded:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  };

  const icons = {
    ok: <CheckCircle className="h-4 w-4" />,
    error: <XCircle className="h-4 w-4" />,
    degraded: <AlertCircle className="h-4 w-4" />,
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium",
        colors[status]
      )}
    >
      {icons[status]}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

function ServiceStatus({
  name,
  status,
  icon: Icon,
}: {
  name: string;
  status: "ok" | "error";
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-4">
      <div className="flex items-center gap-3">
        <Icon className="h-5 w-5 text-muted-foreground" />
        <span className="font-medium">{name}</span>
      </div>
      <StatusBadge status={status} />
    </div>
  );
}

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const data = await getHealth();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch health status"
        );
        setHealth(null);
      } finally {
        setLoading(false);
      }
    }

    fetchHealth();
    // Refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Research Vault</h1>
        <p className="text-muted-foreground mb-8">
          AI-powered research pattern extraction and synthesis
        </p>

        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">System Health</h2>
            {loading ? (
              <span className="text-sm text-muted-foreground">Loading...</span>
            ) : health ? (
              <StatusBadge status={health.status} />
            ) : null}
          </div>

          {error ? (
            <div className="rounded-lg bg-destructive/10 p-4 text-destructive">
              <p className="font-medium">Connection Error</p>
              <p className="text-sm mt-1">{error}</p>
              <p className="text-sm mt-2 text-muted-foreground">
                Make sure the backend is running at{" "}
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              </p>
            </div>
          ) : health ? (
            <div className="space-y-3">
              <ServiceStatus
                name="Database"
                status={health.database}
                icon={Database}
              />
              <ServiceStatus
                name="Vector Store (Qdrant)"
                status={health.qdrant}
                icon={Server}
              />
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-muted-foreground" />
                  <span className="font-medium">Active Sessions</span>
                </div>
                <span className="text-lg font-semibold">{health.sessions}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-3">
                  <Activity className="h-5 w-5 text-muted-foreground" />
                  <span className="font-medium">Tracing</span>
                </div>
                <span
                  className={cn(
                    "text-sm font-medium",
                    health.tracing === "enabled"
                      ? "text-green-600 dark:text-green-400"
                      : "text-muted-foreground"
                  )}
                >
                  {health.tracing === "enabled" ? "Enabled" : "Disabled"}
                </span>
              </div>
            </div>
          ) : null}
        </div>

        <p className="text-sm text-muted-foreground mt-6 text-center">
          More features coming soon: Paper upload, Pattern review, Query
          interface
        </p>
      </div>
    </div>
  );
}
