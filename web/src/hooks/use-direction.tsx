import {
  createContext,
  use,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"

export type Direction = "ltr" | "rtl"

const STORAGE_KEY = "manara-direction"

interface DirectionContextValue {
  direction: Direction
  toggleDirection: () => void
  setDirection: (direction: Direction) => void
}

const DirectionContext = createContext<DirectionContextValue | null>(null)

function getInitialDirection(): Direction {
  if (typeof window === "undefined") return "ltr"

  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (stored === "ltr" || stored === "rtl") return stored

  // Respect the browser's language as a first-run default only —
  // after that, the explicit user choice (persisted above) wins.
  return navigator.language.toLowerCase().startsWith("ar") ? "rtl" : "ltr"
}

/**
 * Governs the direction of app CHROME (sidebar, nav, layout). This is
 * intentionally separate from per-message direction in the chat
 * feature: a bilingual conversation can mix Arabic and English
 * messages, and each message renders with its own detected-language
 * `dir`, independent of this global chrome preference.
 */
export function DirectionProvider({ children }: { children: ReactNode }) {
  const [direction, setDirectionState] = useState<Direction>(
    getInitialDirection,
  )

  useEffect(() => {
    document.documentElement.dir = direction
    window.localStorage.setItem(STORAGE_KEY, direction)
  }, [direction])

  const setDirection = useCallback(
    (next: Direction) => setDirectionState(next),
    [],
  )

  const toggleDirection = useCallback(() => {
    setDirectionState((prev) => (prev === "ltr" ? "rtl" : "ltr"))
  }, [])

  const value = useMemo(
    () => ({ direction, toggleDirection, setDirection }),
    [direction, toggleDirection, setDirection],
  )

  return <DirectionContext value={value}>{children}</DirectionContext>
}

export function useDirection() {
  const ctx = use(DirectionContext)
  if (!ctx)
    throw new Error("useDirection must be used within DirectionProvider")
  return ctx
}
