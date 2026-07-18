import { lazy, Suspense } from "react"
import { Routes, Route } from "react-router-dom"
import { PageLoader } from "@/components/shared/page-loader"

const LandingPage = lazy(() =>
  import("@/pages/landing-page").then((m) => ({ default: m.LandingPage })),
)
const ChatPage = lazy(() =>
  import("@/pages/chat-page").then((m) => ({ default: m.ChatPage })),
)
const NotFoundPage = lazy(() =>
  import("@/pages/not-found-page").then((m) => ({ default: m.NotFoundPage })),
)

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  )
}

export default App
