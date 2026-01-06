/**
 * API client for Research Vault backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Health check response from backend.
 */
export interface HealthStatus {
  status: "ok" | "degraded" | "error";
  database: "ok" | "error";
  qdrant: "ok" | "error";
  sessions: number;
  tracing: "enabled" | "disabled";
}

/**
 * Fetch health status from backend.
 */
export async function getHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}
