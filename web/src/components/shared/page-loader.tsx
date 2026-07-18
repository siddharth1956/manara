import { Logo } from "@/components/shared/logo"

/** Suspense fallback shown while a lazy-loaded route chunk downloads. */
export function PageLoader() {
  return (
    <div className="flex min-h-svh items-center justify-center" role="status" aria-live="polite">
      <div className="animate-pulse">
        <Logo />
      </div>
      <span className="sr-only">Loading…</span>
    </div>
  )
}
