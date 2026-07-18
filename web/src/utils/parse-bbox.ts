export type BBox = [minLon: number, minLat: number, maxLon: number, maxLat: number]

/**
 * Parses the backend's stringified bbox field (e.g.
 * "[54.9, 24.8, 55.5, 25.2]", written by app/services/retriever.py
 * via Python's str(list)) into real numbers. Returns null for
 * anything that isn't a well-formed 4-number box — some documents
 * (e.g. road docs with no computed extent) can have an empty or
 * malformed bbox string, and this must fail closed, not throw or
 * silently plot garbage coordinates.
 */
export function parseBBox(raw: string | null | undefined): BBox | null {
  if (!raw) return null

  try {
    const parsed: unknown = JSON.parse(raw)

    if (
      !Array.isArray(parsed) ||
      parsed.length !== 4 ||
      !parsed.every((n) => typeof n === "number" && Number.isFinite(n))
    ) {
      return null
    }

    const [minLon, minLat, maxLon, maxLat] = parsed as number[]

    if (minLon > maxLon || minLat > maxLat) return null
    if (Math.abs(minLon) > 180 || Math.abs(maxLon) > 180) return null
    if (Math.abs(minLat) > 90 || Math.abs(maxLat) > 90) return null

    return [minLon, minLat, maxLon, maxLat]
  } catch {
    return null
  }
}

export function bboxCenter(bbox: BBox): [lat: number, lon: number] {
  const [minLon, minLat, maxLon, maxLat] = bbox
  return [(minLat + maxLat) / 2, (minLon + maxLon) / 2]
}
