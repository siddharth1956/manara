import { Logo } from "@/components/shared/logo"
import { ThemeToggle } from "@/components/shared/theme-toggle"
import { DirectionToggle } from "@/components/shared/direction-toggle"

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Logo withWordmark />
        <div className="flex items-center gap-1">
          <DirectionToggle />
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
