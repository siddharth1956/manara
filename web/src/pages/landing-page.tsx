import { SiteHeader } from "@/components/shared/site-header"
import { HeroSection } from "@/features/landing/hero-section"
import { FeatureCards } from "@/features/landing/feature-cards"

export function LandingPage() {
  return (
    <div className="relative flex min-h-svh flex-col">
      <SiteHeader />

      <main className="flex-1">
        <HeroSection />

        <section className="mx-auto max-w-6xl px-4 pb-24 sm:px-6">
          <FeatureCards />
        </section>
      </main>

      <footer className="border-t border-border/60 py-8 text-center text-sm text-muted-foreground">
        MANARA — Arabic Geospatial Intelligence Assistant
      </footer>
    </div>
  )
}
