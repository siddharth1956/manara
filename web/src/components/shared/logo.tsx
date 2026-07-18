interface LogoProps {
  className?: string
  /** Include the "MANARA" wordmark next to the mark. */
  withWordmark?: boolean
}

/**
 * MANARA's brand mark — a beacon, echoing the word's Arabic meaning
 * ("lighthouse" / "beacon"). Pure currentColor SVG so it adapts to
 * theme and accent changes without a separate light/dark asset.
 */
export function Logo({ className, withWordmark = false }: LogoProps) {
  return (
    <span className={`inline-flex items-center gap-2 ${className ?? ""}`}>
      <svg
        viewBox="0 0 32 32"
        className="size-7 shrink-0 text-primary"
        aria-hidden="true"
      >
        <path d="M16 6 L21 24 H11 Z" fill="currentColor" />
        <path
          d="M16 6 L18.5 24 H13.5 Z"
          fill="currentColor"
          opacity="0.55"
        />
        <circle cx="16" cy="9" r="1.4" fill="var(--background)" />
        <path
          d="M9 12c1.5-3 4.2-5 7-5s5.5 2 7 5"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
          fill="none"
          opacity="0.55"
        />
        <path
          d="M6.5 9c2-4.2 5.8-7 9.5-7s7.5 2.8 9.5 7"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
          fill="none"
          opacity="0.3"
        />
      </svg>
      {withWordmark && (
        <span className="font-heading text-lg font-semibold tracking-tight text-foreground">
          MANARA
        </span>
      )}
    </span>
  )
}
