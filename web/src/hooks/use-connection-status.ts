import { useEffect, useState } from "react"
import { checkHealth } from "@/services/api"
import type { ConnectionState } from "@/features/chat/connection-status"

const POLL_INTERVAL_MS = 15_000

/** Polls the backend's existing home route (GET /) for reachability. */
export function useConnectionStatus() {
  const [status, setStatus] = useState<ConnectionState>("checking")

  useEffect(() => {
    let cancelled = false

    const poll = async () => {
      const reachable = await checkHealth()
      if (!cancelled) setStatus(reachable ? "connected" : "disconnected")
    }

    void poll()
    const interval = setInterval(poll, POLL_INTERVAL_MS)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  return status
}
