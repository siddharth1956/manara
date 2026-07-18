import { z } from "zod"
import type { ApiErrorBody, QueryContext, QueryResponse } from "@/types/api"

/**
 * In dev, requests go through the Vite proxy configured in
 * vite.config.ts (`/api` -> http://127.0.0.1:8000, prefix stripped),
 * which avoids CORS entirely without touching the backend (confirmed:
 * app/main.py has no CORS middleware). In production, point
 * VITE_API_BASE_URL at the deployed FastAPI host directly — the
 * backend's real route is `/query` with no `/api` prefix, so no
 * rewriting is needed there.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api"

const TIMEOUT_MS = 90_000 // real backend latency observed at 14-25s for a single query
// (CPU-bound Ollama generation, no GPU in this environment) — generous
// headroom above that, not the mock's 900-2300ms simulated delay.
const MAX_RETRIES = 2
const RETRY_DELAYS_MS = [500, 1500]

export type ApiErrorKind = "http" | "network" | "timeout" | "invalid_response"

export class ApiError extends Error {
  status: number
  kind: ApiErrorKind

  constructor(message: string, status: number, kind: ApiErrorKind) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.kind = kind
  }
}

// Mirrors types/api.ts's QueryResponse exactly, for runtime validation
// only — no new fields invented, nothing here the backend doesn't
// already return. Catches "unexpected response shape" (a field
// missing, or of the wrong type) that TypeScript's compile-time types
// can't guard against, since the actual bytes over the wire are
// untyped as far as the runtime is concerned.
const queryEntitiesSchema = z.object({
  location: z.string().nullable().optional(),
  satellite: z.string().nullable().optional(),
  metric: z.string().nullable().optional(),
  date: z.string().nullable().optional(),
})

const retrievedDocumentSchema = z.object({
  id: z.string(),
  type: z.string(),
  platform: z.string(),
  constellation: z.string(),
  datetime: z.string(),
  cloud_cover: z.number().nullable(),
  bbox: z.string(),
  confidence: z.number(),
  distance: z.number(),
  text: z.string(),
})

const queryResponseSchema = z.object({
  question: z.string(),
  language: z.enum(["english", "arabic"]),
  intent: z.enum([
    "analytics",
    "satellite_search",
    "road_search",
    "comparison",
    "map",
    "general",
  ]),
  entities: queryEntitiesSchema,
  answer: z.string(),
  sources: z.array(retrievedDocumentSchema),
})

export interface QueryResult {
  data: QueryResponse
  /** Client-measured round-trip time. The backend does not return its
   * own latency figure, so this is the honest, measurable substitute
   * used by the Retrieval Inspector and Dashboard. */
  latencyMs: number
}

/** Abort-aware sleep — without this, clicking Stop during a retry's
 * backoff window wouldn't take effect until the next fetch attempt. */
function sleep(ms: number, signal?: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException("Aborted", "AbortError"))
      return
    }

    const timer = setTimeout(resolve, ms)

    signal?.addEventListener(
      "abort",
      () => {
        clearTimeout(timer)
        reject(new DOMException("Aborted", "AbortError"))
      },
      { once: true },
    )
  })
}

/**
 * fetch() wrapped with:
 *  - a request timeout, independent of any caller-supplied signal
 *  - retry with backoff, but ONLY for transient network failures
 *    (fetch() throwing — DNS/connection-refused/offline) — never for
 *    a resolved HTTP response, even a 5xx, since that's a real
 *    application answer from the backend, not a transient blip
 *  - the caller's own AbortSignal (e.g. the chat UI's Stop button)
 *    still cancels immediately and is never retried
 */
async function robustFetch(url: string, init: RequestInit, callerSignal?: AbortSignal): Promise<Response> {
  const timeoutController = new AbortController()
  const timeoutId = setTimeout(() => timeoutController.abort(), TIMEOUT_MS)

  const combinedSignal = callerSignal
    ? AbortSignal.any([callerSignal, timeoutController.signal])
    : timeoutController.signal

  try {
    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        return await fetch(url, { ...init, signal: combinedSignal })
      } catch (error) {
        // Caller cancelled (e.g. Stop button) — propagate immediately, no retry.
        if (callerSignal?.aborted) throw error

        // Our own timeout fired — stop retrying, a slow backend won't
        // get faster by hammering it again.
        if (timeoutController.signal.aborted) {
          throw new ApiError(
            "The request took too long to respond.",
            0,
            "timeout",
          )
        }

        // Genuine transient network failure — worth a retry, up to
        // MAX_RETRIES, before falling through to the network ApiError
        // below. The underlying TypeError isn't surfaced directly —
        // the goal is a message a user can act on.
        if (attempt < MAX_RETRIES) {
          try {
            await sleep(RETRY_DELAYS_MS[attempt] ?? 1500, callerSignal)
          } catch {
            throw error // caller aborted mid-backoff — propagate the original abort
          }
        }
      }
    }

    throw new ApiError(
      "Unable to reach MANARA. Check your connection and try again.",
      0,
      "network",
    )
  } finally {
    clearTimeout(timeoutId)
  }
}

export async function queryManara(
  question: string,
  signal?: AbortSignal,
  context?: QueryContext,
): Promise<QueryResult> {
  const start = performance.now()

  const response = await robustFetch(
    `${API_BASE_URL}/query`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(context ? { question, context } : { question }),
    },
    signal,
  )

  const latencyMs = performance.now() - start

  if (!response.ok) {
    // Gateway-type statuses (502/503/504) mean an intermediary — a
    // reverse proxy in front of the real deployment, or the Vite dev
    // proxy used for local testing — couldn't reach the backend at
    // all, so there's no FastAPI JSON body to read; a generic
    // "status 502" is accurate but not the kind of message a user
    // can act on. FastAPI's own HTTPException responses (400/500,
    // real `{"detail": "..."}` bodies from app/main.py) are already
    // user-facing text and take priority below when present.
    let detail =
      response.status === 502 || response.status === 503 || response.status === 504
        ? "MANARA's backend isn't reachable right now. Please try again shortly."
        : `Request failed with status ${response.status}`

    try {
      const body = (await response.json()) as ApiErrorBody
      if (body.detail) detail = body.detail
    } catch {
      // Response body wasn't JSON (e.g. the gateway cases above) —
      // keep the fallback message already selected.
    }

    throw new ApiError(detail, response.status, "http")
  }

  let raw: unknown

  try {
    raw = await response.json()
  } catch {
    throw new ApiError(
      "MANARA sent back a response that couldn't be read.",
      response.status,
      "invalid_response",
    )
  }

  const parsed = queryResponseSchema.safeParse(raw)

  if (!parsed.success) {
    throw new ApiError(
      "MANARA sent back an unexpected response shape.",
      response.status,
      "invalid_response",
    )
  }

  return { data: parsed.data, latencyMs }
}

/** Used by useConnectionStatus — a bare reachability check against the
 * backend's existing home route, not a new endpoint. */
export async function checkHealth(signal?: AbortSignal): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/`, { signal })
    return response.ok
  } catch {
    return false
  }
}
