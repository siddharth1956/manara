import type { Language } from "@/types/api"

/**
 * Mirrors app/services/language_detector.py exactly (same Unicode
 * range ؀-ۿ, same "any Arabic character wins" rule) so the
 * client-side preview (e.g. the input's live `dir` attribute) never
 * disagrees with what the backend will actually detect for the same
 * text. Verified byte-identical to the Python regex, not eyeballed.
 */
const ARABIC_RANGE = /[؀-ۿ]/

export function detectLanguage(text: string): Language {
  return ARABIC_RANGE.test(text) ? "arabic" : "english"
}
