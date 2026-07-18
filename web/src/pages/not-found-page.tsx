import { Link } from "react-router-dom"
import { Compass } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Logo } from "@/components/shared/logo"

export function NotFoundPage() {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-6 px-6 text-center">
      <Logo />
      <div className="flex items-center gap-3 text-muted-foreground">
        <Compass className="size-8" strokeWidth={1.5} />
        <span className="font-heading text-6xl font-semibold tracking-tight text-foreground">
          404
        </span>
      </div>
      <div className="space-y-1.5">
        <h1 className="text-xl font-semibold text-foreground">
          This page hasn't been charted yet
        </h1>
        <p className="max-w-md text-sm text-muted-foreground">
          The page you're looking for doesn't exist, or isn't built yet.
        </p>
      </div>
      <Button asChild>
        <Link to="/">Back to home</Link>
      </Button>
    </main>
  )
}
