import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter } from "react-router-dom"

import { ThemeProvider } from "@/hooks/use-theme"
import { DirectionProvider } from "@/hooks/use-direction"
import { Toaster } from "@/components/ui/sonner"
import { TooltipProvider } from "@/components/ui/tooltip"
import App from "./App.tsx"
import "./index.css"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <DirectionProvider>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider delayDuration={200}>
            <BrowserRouter>
              <App />
            </BrowserRouter>
            <Toaster />
          </TooltipProvider>
        </QueryClientProvider>
      </DirectionProvider>
    </ThemeProvider>
  </StrictMode>,
)
