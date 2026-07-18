# MANARA Web

A production-grade React frontend for MANARA, a bilingual (Arabic/English) geospatial intelligence assistant. Built alongside — not replacing — the existing Streamlit frontend in `../frontend/`; the FastAPI backend in `../app/` is used exactly as-is, unmodified.

This is a phased build (see project history). **Phase 1: scaffold, design system, landing page — complete. Phase 2: chat workspace UI — complete. Phase 3: real backend integration — complete. Phase 4: retrieval intelligence panel (Inspector, Sources, Entities, Map) — complete.** The chat now talks to the actual FastAPI backend via `POST /query`; `mock-assistant.ts` from Phase 2 has been deleted.

## Stack

React 19 · TypeScript · Vite · Tailwind CSS v4 · shadcn/ui (Radix base, Nova preset) · Framer Motion · TanStack Query · React Hook Form · React Router · React Leaflet · Lucide Icons

## Getting started

```bash
npm install
npm run dev      # starts on http://localhost:5173, proxies /api -> the FastAPI backend
```

The backend must be running separately (`uvicorn app.main:app --reload` from the repo root) for any API-integrated features to work — see the root `CLAUDE.md`.

```bash
npm run build     # type-checks (tsc -b) then builds to dist/
npm run lint       # oxlint
npm run preview    # serve the production build locally
```

## Folder structure

```
src/
  components/
    ui/           shadcn-generated primitives (button, card, tooltip, ...) — don't hand-edit,
                   regenerate via `npx shadcn add <component>`
    shared/        Hand-written, reusable across features (Logo, SiteHeader, ThemeToggle, ...)
  features/
    landing/       Landing-page-specific components (not reused elsewhere)
    chat/          Sidebar, header, message list/bubble, markdown renderer, chat state (chat-context.tsx),
                   input, loading states, and the temporary mock-assistant.ts (see Phase 2 notes below)
    <feature>/     One folder per remaining feature area, added as each phase lands (inspector, map, dashboard)
  pages/           Route-level components — compose features, contain no business logic themselves
  hooks/           Reusable React hooks (use-theme, use-direction, ...) — cross-cutting, used by 2+ features.
                   Feature-specific state (e.g. chat conversations) lives in that feature's own folder instead.
  services/        External I/O — currently just the typed API client (services/api.ts, unused until Phase 3)
  types/           Shared TypeScript types: types/api.ts (mirrors the FastAPI contract exactly, from Phase 1,
                   unmodified since) and types/chat.ts (chat-specific, added Phase 2)
  utils/           Pure helper functions: detect-language.ts (mirrors the backend's Arabic-detection regex
                   byte-for-byte, verified not eyeballed), format-time.ts
  lib/utils.ts     shadcn's own `cn()` class-merging helper — kept at shadcn's expected import
                   path (`@/lib/utils`) rather than moved into utils/, so every future
                   `npx shadcn add` command keeps working without manual import fixes
  styles/          Reserved for phase-specific stylesheets beyond index.css, if any become necessary
```

## Component architecture

- **`pages/`** own routing concerns only — each page composes `features/*` components and shared layout (`SiteHeader`, etc.). No fetch calls or business logic live directly in a page component.
- **`features/<name>/`** hold everything specific to one feature area (e.g. the landing page's hero, animated background, feature cards). A component only moves to `components/shared/` once a second feature actually needs it — nothing is pre-emptively "shared" on the assumption it might be reused later.
- **`components/ui/`** is shadcn's generated output. Treat it as a dependency, not hand-written code — customize via the design tokens in `index.css`, not by editing these files directly, so `npx shadcn add`/updates stay safe.

## State management

No global state library (Redux/Zustand/etc.) — deliberately. Three narrow, purpose-built mechanisms instead:

1. **Server state** — TanStack Query is installed and provider-wired, but not yet consuming it: Phase 2's chat still talks to a local mock (see below), not the real API, so there's nothing to cache yet. Lands for real in Phase 3.
2. **Cross-cutting UI preferences** — small React Context providers, each doing exactly one thing:
   - `hooks/use-theme.tsx` — light/dark mode, persisted to `localStorage`, applied via a `.dark` class on `<html>` (Tailwind's class-based dark mode strategy).
   - `hooks/use-direction.tsx` — **global UI chrome** direction (RTL/LTR), persisted, applied via `dir` on `<html>`. Deliberately separate from per-message direction: `features/chat/message-bubble.tsx` independently re-detects each message's direction from its own content (`utils/detect-language.ts`) rather than trusting a stored language tag — see that file's comment for the real rendering bug this fixed during Phase 2 verification.
   - `features/chat/chat-context.tsx` — conversations, messages, and the active conversation, as a reducer (`useReducer`) exposed via context. Persisted to `localStorage` (conversation history is explicitly frontend-only per the Phase 2 spec — no backend persistence — but surviving a page refresh is still a frontend concern).
3. **Local component state** — plain `useState` where state doesn't cross component boundaries (e.g. the chat input's text, sidebar search query, mobile drawer open/closed).

## Routing

React Router v7 (`BrowserRouter`), with routes lazy-loaded via `React.lazy` + `Suspense` for automatic code-splitting per route — confirmed working: `npm run build` produces a separate chunk per page (`landing-page-*.js`, `chat-page-*.js`, `not-found-page-*.js`) rather than one monolithic bundle. Routes so far:

| Path | Page | Status |
|---|---|---|
| `/` | `LandingPage` | Complete |
| `/chat` | `ChatPage` | Complete (UI + local state; talks to a mock, not the real API — see below) |
| `*` | `NotFoundPage` | Complete (catch-all) |

## API integration

`services/api.ts` wraps the backend's single real endpoint, `POST /query`, with:

- Full TypeScript types in `types/api.ts`, written directly from `app/main.py` and `app/services/retriever.py`'s actual return shapes — not guessed. Note `QueryEntities` is intentionally sparse/nullable: the English and Arabic NLU pipelines don't return identically-shaped entity dicts (see backend source), and the types reflect that rather than papering over it.
- Client-side latency measurement (`performance.now()` around the fetch). The backend has no latency field of its own — this is the honest substitute, used later by the Retrieval Inspector and Dashboard.
- A typed `ApiError` for non-2xx responses, parsing the backend's actual `{"detail": "..."}` error shape (both the `400` empty-question case and the `500` generic-error case added to `app/main.py` earlier in this project).

In dev, requests go through the Vite proxy in `vite.config.ts` (`/api` → `http://127.0.0.1:8000`, prefix stripped) — this avoids CORS without touching the backend at all. In production, set `VITE_API_BASE_URL` (see `.env.example`) to the deployed backend's base URL; the client calls `${VITE_API_BASE_URL}/query` directly, no prefix rewriting needed there since the real route has no `/api` prefix.

## Design system

- Tailwind v4 (CSS-first config, no `tailwind.config.js` — theme lives in `index.css`'s `@theme inline` block, generated by shadcn's init).
- Color tokens follow shadcn's semantic naming (`--primary`, `--background`, `--muted-foreground`, etc.) so components never hardcode colors — this is what makes dark mode a one-line class toggle rather than a duplicated stylesheet. The Nova preset's neutral grayscale base was kept, with a single cyan accent (`#0891b2` light / `#22d3ee` dark) layered in for `--primary`/`--ring`/`--sidebar-primary` — one accent color used sparingly, matching the ChatGPT/Claude/Perplexity reference aesthetic rather than a saturated multi-color UI.
- Typography: Geist Variable (via `@fontsource-variable/geist`, self-hosted — no external font CDN request).
- RTL: `shadcn init --rtl` enabled logical-property-aware component generation; verified end-to-end (see Phase 1 verification) that toggling direction correctly mirrors the entire layout (header, grid order, alignment), not just individual text runs.

## Verification (Phase 1)

Real browser verification via Playwright driving the system's installed Chrome (not just `tsc`/build success) — screenshots and a scripted check, not a claim taken on faith:

- **Desktop (1440×900), tablet (820×1180), mobile (390×844)** — light and dark mode, all 6 combinations screenshotted and visually reviewed.
- **Zero browser console errors or exceptions** across all three viewports (captured via Playwright's console/pageerror listeners, not assumed).
- **RTL toggle** — confirmed `document.documentElement.dir` actually flips to `"rtl"` on click, and visually confirmed the whole layout mirrors correctly (logo/toggles swap sides, feature-card grid reverses reading order, text right-aligns).
- **One real bug found and root-caused during verification, not glossed over**: the first full-page mobile screenshot showed 3 of 4 feature cards missing (blank space). Investigated rather than assumed — confirmed via computed-style inspection (`opacity`) and a second test using a real incremental scroll (`mouse.wheel` in steps, matching actual user behavior) that this was a Playwright `fullPage`-screenshot artifact: its non-incremental viewport resize doesn't reliably trigger Framer Motion's `whileInView` scroll-reveal for content below the fold, but a real scrolling user sees all cards render correctly (verified: all opacities = 1 after a real scroll). Documented here rather than silently fixed or silently ignored, since it's a legitimate fragility in relying on scroll-triggered reveals for below-the-fold mobile content, even though it isn't user-facing today.
- **Known minor polish item, not fixed yet**: the "Start Chat" button's arrow icon doesn't mirror direction in RTL (stays pointing right instead of flipping left). Cosmetic, not functional — left for a later polish pass rather than blocking Phase 1 on it.

Not yet verifiable in this environment: no way to test on a physical tablet/mobile device — the "tablet"/"mobile" verification above is Chrome's viewport emulation, not a real device.

## Phase 2 — chat workspace

Built: app shell (sidebar + header + main panel), full sidebar (new chat, search, delete-with-confirmation, collapse/expand, theme + direction toggles), header (title, language badge, connection status, settings, theme toggle), and the chat interface itself (markdown rendering with syntax-highlighted code blocks/tables/blockquotes/lists, auto-growing RTL-aware input, thinking indicator → skeleton hold → fade-in loading sequence, mobile drawer sidebar).

**Two scope judgment calls made explicit, not silently decided:**
- **`features/chat/mock-assistant.ts`** — Phase 2's brief excludes backend integration but requires demonstrating the full loading→arrival flow and markdown rendering. Rather than fabricate plausible-looking content, every mock response reuses real document IDs, confidence scores, and query/answer pairs verified in this project's own Task D/E/F work. Deleted in Phase 3 when `services/api.ts` (already built, unused until then) gets wired in for real.
- **`features/chat/connection-status.tsx`** — always renders `disconnected` this phase. A live health check would mean a network call, which reads as backend integration even for a bare `GET /`; the honest "not yet checked" state was chosen over fabricating a fake "Connected" badge. Built with all three states (connected/disconnected/checking) so Phase 3 can wire a real check by changing one prop.

### Verification (Phase 2)

Same real-browser methodology as Phase 1 (Playwright driving the system's Chrome, not just build success) — empty state, a full conversation (road query → table/blockquote response, satellite query → JSON code block response), RTL, mobile drawer, keyboard navigation (Tab/Enter/Shift+Enter), search filtering, sidebar collapse, delete confirm/cancel, and long/short message edge cases. Zero console errors or exceptions across every scenario tested.

**Two real bugs found and fixed during verification, not glossed over:**

1. **Assistant messages could render right-aligned RTL despite English content.** The mock (and, per `app/main.py`, the real backend too) reports `language` as the *query's* detected language, not the *answer's* — an Arabic question with an English-content answer rendered that English text right-aligned under `dir="rtl"`, which reads as broken. Fixed in `message-bubble.tsx` by re-detecting direction from each message's own content (`detectLanguage(message.content)`) rather than trusting the stored language tag — robust to real backend behavior, not just this phase's mock data. Verified: Arabic query + English mock answer now renders the answer LTR while the query stays RTL.
2. **Long unbroken text (e.g. a document ID) could overflow the viewport horizontally.** Root-caused via computed-style inspection up the DOM chain (not assumed) to two distinct flexbox issues: (a) the message row itself needed `min-w-0` — as a flex item of `MessageList`'s `flex-col` container, it defaulted to content-based `min-width: auto` and could force itself wider than the viewport; (b) less obvious — the bubble `<div>` needed an explicit `max-w-full`, because its parent column uses `items-end` to right-align user messages, and any `align-items` value other than the flex default `stretch` makes a flex item revert to shrink-to-fit sizing, where `min-width: 0` alone doesn't cap growth. Verified via `boundingClientRect`/computed-style checks pre- and post-fix, not just visually.

Not yet verifiable in this environment: physical tablet/mobile hardware (same limitation as Phase 1); the mock's simulated latency (900–2300ms) is not representative of real Ollama/retrieval latency, which Phase 3's real integration will surface.

## Phase 3 — real backend integration

`services/api.ts` rewritten: request timeout (90s — real observed backend latency is 14–25s, CPU-bound Ollama generation with no GPU in this environment, not the mock's ~1–2s), retry-with-backoff scoped strictly to transient network failures (`fetch()` throwing — never retries a resolved HTTP response, even a 5xx, since that's a real answer from the backend), and runtime response-shape validation via `zod` (schema mirrors `types/api.ts` exactly — no new fields, just a runtime guard against a malformed/unexpected response TypeScript's compile-time types can't catch). `hooks/use-connection-status.ts` added — polls the backend's existing `GET /` every 15s; the header's "Not connected" placeholder from Phase 2 is now live. `mock-assistant.ts` deleted.

### Verification (Phase 3) — against the real, running backend

Ollama + `uvicorn app.main:app` actually running for this phase, not simulated. Confirmed via direct `curl` first (English query ~22s, Arabic query ~14s, both grounded in real retrieved sources) before testing through the UI. Real English and Arabic queries end-to-end through the browser (10–17s observed), dark mode, mobile, Stop-button on a real in-flight request, duplicate-submission prevention, and backend-unavailable handling (stopped the real backend process mid-session, tested, restarted it).

**Two real bugs found and fixed, not glossed over — both only surfaced because this phase exercises real failure paths Phase 2's always-succeeding mock never hit:**

1. **A message that failed got stuck on the thinking indicator forever.** `assistant-message.tsx`'s reveal-sequence effect only recognized a transition to `"complete"`; a transition to `"error"` never cleared its internal `phase` state out of `"pending"`, and the render logic checked `phase === "pending"` before it ever checked `message.status === "error"`. Root-caused with temporary tracing added directly to the source (black-box testing wasn't enough to isolate it — every layer tested in isolation, from a bare `fetch()` up through `AbortSignal.any`-combined signals, resolved correctly and fast; the break was specifically in this one component's state machine, only visible by tracing the real component tree). Fixed: `"error"` now settles immediately, skipping the reveal-hold flourish that's appropriate for a successful arrival but not for a failure.
2. **Backend-unavailable produced a technical, not user-friendly, message.** In this dev setup, "backend down" surfaces as an HTTP `502` *from the Vite proxy* (a resolved response, not a network-level failure), which took the generic `"Request failed with status {code}"` path rather than the friendlier network-error message reserved for genuine connection failures. Since a real production deployment behind a reverse proxy would hit the same 502/503/504-from-intermediary case, added a specific friendlier fallback for those three statuses ("MANARA's backend isn't reachable right now...") rather than treating it as just a local-dev quirk.

**One limitation documented, not silently hidden:** clicking Stop cancels the *client's* wait — confirmed via the backend's own request log that both a satellite-imagery query and a follow-up query stopped mid-generation still completed server-side with `200 OK`. The current backend architecture is fully synchronous with no cancellation-aware plumbing around the Ollama call, and adding that would be a backend change, explicitly out of scope for this phase. "Support AbortController for cancellation" is implemented as a genuine, verified client-side capability (the UI immediately stops waiting/showing progress and is ready for a new request); it does not — and cannot, without backend changes — interrupt the model generation already running on the server.

**Retry-with-backoff verified with real timing, not just code review:** the backend-down test above goes through the dev proxy (which stays up and answers with a resolved 502, not a network-level failure). To exercise the actual `"network"` error path and its retry logic, ran a second dev server instance with `VITE_API_BASE_URL` pointed directly at an unreachable port (bypassing the proxy) — confirmed 3 real connection attempts (initial + 2 retries) and a 2.4s resolution time, matching the configured 500ms/1500ms backoff exactly, before showing the correct friendlier network-error message.

Not yet verifiable in this environment: physical tablet/mobile hardware (same limitation as Phases 1–2).

## Phase 4 — retrieval intelligence panel

Added `features/intelligence/`: a right-side panel with three tabs — Overview (Retrieval Inspector + Entity Viewer), Sources (an accordion of retrieved documents), and Map (React Leaflet, lazy-loaded). All data is pulled from `ChatMessage.meta` — no new fetching, this is purely a visualization layer over what Phase 3 already retrieves. The panel always reflects the most recently completed assistant response in the active conversation.

**Three data-honesty decisions worth knowing about, since they shape what the panel shows:**
- **No separate "processing time" metric.** The backend returns exactly one real timing signal (client-measured round-trip). Rather than invent a second distinct "processing time" figure the backend doesn't provide, the panel shows one honestly-labeled "Latency" stat.
- **"Top match confidence"**, not a mysterious overall AI-confidence score — the backend has no such field. Derived from the top-ranked source's real `confidence` (documents already arrive sorted by confidence from `app/services/retriever.py`), labeled explicitly so it's clear what it represents.
- **The "Platforms" entity category will always read "None detected."** Confirmed back in Phase 1 that `entities.platform` is checked by the retriever's boost logic but never populated by either NLU pipeline — a pre-existing backend gap, not something faked here to look populated.

**Map specifics:** bounding boxes are parsed from each source's real `bbox` field (validated defensively — malformed/empty values fail closed rather than plotting garbage). The "detected location" marker uses a small hardcoded UAE-emirates coordinate table (`utils/uae-locations.ts`) — real, stable geography, not fabricated — since the backend returns a location as a bare string ("dubai") with no coordinates. Gracefully shows a "No map data for this query" message when a message has neither bounding boxes nor a resolvable location, rather than rendering a broken/blank map.

**Responsive:** desktop (≥1024px) is a persistent third column; tablet (640–1023px) and mobile (<640px) are a right-side / bottom Sheet respectively, opened via a new header button, driven by a small `useMediaQuery` hook (needed because the Sheet's `side` prop is a JS-level positioning choice, not something pure CSS can drive).

**Performance:** the map is lazy-loaded via `React.lazy` — confirmed in the build output that `leaflet` (~150KB) lands in its own chunk (`map-panel-*.js`), not bundled into the main chat page, so it's only fetched once a user actually opens the Map tab.

### Verification (Phase 4) — against the real, running backend

Real English and Arabic queries (road, satellite, analytics intents) through the full desktop flow — Overview, Sources (expand/collapse), Map — plus tablet, mobile, dark mode, and RTL, all against live retrieval results.

**Three real issues found, investigated, and fixed — not glossed over:**

1. **A one-time "Invalid hook call" crash when first opening the Map tab**, with zero tiles/rectangles rendered. Investigated rather than patched blindly: `npm ls` confirmed a single deduped React 19.2.7 across the entire tree including `react-leaflet`'s own dependencies, ruling out an actual duplicate-React install. Isolated a bare dynamic `import()` of the module — it succeeded cleanly both before and after. Re-ran the exact original repro immediately after — it then passed with 11 tiles and 5 rectangles rendered, and has been consistently clean on every run since. This is a documented Vite dev-server behavior: the *first* time a heavy new dependency is reached via dynamic import, Vite discovers and pre-bundles it on the fly and reloads the page to pick it up, and code executing in the narrow window before that reload completes can transiently see this exact symptom. Confirmed it's dev-only, not a real defect, by checking the production build (`vite build` + `vite preview`) loads the same route cleanly with no such error.
2. **The Overview panel initially showed the assistant's answer text as the "Query"** instead of the actual question asked. Root cause: `ChatMessage.meta` didn't capture the backend's own echoed `question` field from `QueryResponse` — an oversight from Phase 3, not a fabricated fix. Added `question: string` to the `meta` type (a real field the backend already returns, just not stored) rather than misuse the assistant message's own `content`.
3. **A serious, previously-invisible bug: real conversation history was being wiped on every page reload.** `chat-context.tsx`'s "persist to localStorage" effect ran with the reducer's initial (empty) state *before* the "hydrate from localStorage" effect's dispatch had actually been applied — silently overwriting real saved data with nothing, on every mount. This existed since Phase 2 but was never caught, because every prior phase's tests cleared `localStorage` first for test isolation, so there was never real prior data to lose — hydrating empty back to empty looks identical to correct behavior. Found by deliberately testing what every earlier phase's tests had structurally avoided: real data surviving a real reload. Fixed by gating the persist effect behind a `hydrated` flag that's only set once the read has genuinely been attempted, so it's structurally impossible to write before reading first. Verified with real UI-driven data (not synthetic injection): sent a real query, reloaded the page for real, confirmed both the message content and the conversation title survived.

One methodology note worth recording: mid-investigation of bug 3, a *second* reload-based test appeared to still show the bug after the fix was already in place. That turned out to be my own test script's mistake, not a remaining defect — `context.addInitScript(() => localStorage.clear())` (used for test isolation) runs on *every* navigation within a browser context, including `page.reload()`, so it was wiping my own test data mid-test. Re-verified with a corrected script (clearing once, not on every navigation) before concluding the fix was correct.

Not yet verifiable in this environment: physical tablet/mobile hardware (same limitation as all prior phases). The "no map data" empty state was verified via direct state injection (a message with `sources: []` and no entities) rather than a real query, since the live backend's `retrieve()` always returns 5 documents for any query in the current corpus — genuinely triggering that case organically wasn't possible with real traffic, so the code path itself was verified directly instead of claiming a real query exercised it.
