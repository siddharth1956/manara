/**
 * Real, stable geographic coordinates for the UAE emirates — not
 * backend data, but not fabricated either: these are the same seven
 * emirates app/services/location_mapper.py's LOCATION_MAP normalizes
 * Arabic place names to. The backend returns a location as a bare
 * string (e.g. "dubai"), never coordinates, so plotting "the detected
 * location" on the map requires a lookup like this on the client side.
 */
export const UAE_LOCATIONS: Record<string, { label: string; lat: number; lon: number }> = {
  dubai: { label: "Dubai", lat: 25.2048, lon: 55.2708 },
  "abu dhabi": { label: "Abu Dhabi", lat: 24.4539, lon: 54.3773 },
  sharjah: { label: "Sharjah", lat: 25.3463, lon: 55.4209 },
  ajman: { label: "Ajman", lat: 25.4052, lon: 55.5136 },
  "ras al khaimah": { label: "Ras Al Khaimah", lat: 25.7895, lon: 55.9432 },
  fujairah: { label: "Fujairah", lat: 25.1288, lon: 56.3265 },
  "umm al quwain": { label: "Umm Al Quwain", lat: 25.5647, lon: 55.5534 },
  "bur dubai": { label: "Bur Dubai", lat: 25.2582, lon: 55.2963 },
}

export function lookupLocation(name: string | null | undefined) {
  if (!name) return null
  return UAE_LOCATIONS[name.trim().toLowerCase()] ?? null
}
