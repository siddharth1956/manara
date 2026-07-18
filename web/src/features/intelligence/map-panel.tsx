import { useEffect, useMemo } from "react"
import {
  MapContainer,
  TileLayer,
  Rectangle,
  Marker,
  Popup,
  useMap,
} from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import type { RetrievedDocument, QueryEntities } from "@/types/api"
import { parseBBox, bboxCenter, type BBox } from "@/utils/parse-bbox"
import { lookupLocation } from "@/utils/uae-locations"
import { deriveDocumentTitle } from "@/utils/document-title"

// react-leaflet's default marker icon references image paths that
// don't resolve under Vite's bundling — a well-known upstream issue,
// not something specific to this app. Rebuilding the default icon
// from the actual bundled asset URLs fixes it project-wide, once.
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL("leaflet/dist/images/marker-icon-2x.png", import.meta.url).href,
  iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url).href,
  shadowUrl: new URL("leaflet/dist/images/marker-shadow.png", import.meta.url).href,
})

const SATELLITE_COLOR = "#0891b2"
const ROADS_COLOR = "#d97706"

interface MapPanelProps {
  sources: RetrievedDocument[]
  entities: QueryEntities | undefined
  /** True only once this panel's tab/sheet is actually visible — see
   * FitAndInvalidate below for why this matters. */
  isActive: boolean
}

/** Leaflet computes its tile grid from the container's size at the
 * moment it mounts. If that container is hidden (e.g. an inactive
 * shadcn/Radix Tabs panel, which stays mounted but display:none'd
 * rather than unmounted), the map initializes at zero size and tiles
 * render blank until told to re-measure. This also fits the view to
 * whatever markers/boxes are actually present, every time the visible
 * set changes. */
function FitAndInvalidate({ bounds, isActive }: { bounds: L.LatLngBoundsExpression | null; isActive: boolean }) {
  const map = useMap()

  useEffect(() => {
    if (!isActive) return
    const timer = setTimeout(() => {
      map.invalidateSize()
      if (bounds) map.fitBounds(bounds, { padding: [32, 32], maxZoom: 14 })
    }, 50)
    return () => clearTimeout(timer)
  }, [map, isActive, bounds])

  return null
}

export function MapPanel({ sources, entities, isActive }: MapPanelProps) {
  const boxed = useMemo(
    () =>
      sources
        .map((doc) => ({ doc, bbox: parseBBox(doc.bbox) }))
        .filter((x): x is { doc: RetrievedDocument; bbox: BBox } => x.bbox !== null),
    [sources],
  )

  const highlightedLocation = useMemo(
    () => lookupLocation(entities?.location),
    [entities?.location],
  )

  const bounds = useMemo<L.LatLngBoundsExpression | null>(() => {
    const points: [number, number][] = boxed.map(({ bbox }) => bboxCenter(bbox))
    boxed.forEach(({ bbox }) => {
      points.push([bbox[1], bbox[0]], [bbox[3], bbox[2]])
    })
    if (highlightedLocation) points.push([highlightedLocation.lat, highlightedLocation.lon])
    return points.length > 0 ? points : null
  }, [boxed, highlightedLocation])

  const hasNothingToShow = boxed.length === 0 && !highlightedLocation

  if (hasNothingToShow) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 p-6 text-center">
        <p className="text-sm font-medium text-foreground">No map data for this query</p>
        <p className="max-w-xs text-xs text-muted-foreground">
          Neither the retrieved documents nor the detected entities
          included location or bounding-box information to plot.
        </p>
      </div>
    )
  }

  const center = highlightedLocation
    ? ([highlightedLocation.lat, highlightedLocation.lon] as [number, number])
    : boxed.length > 0
      ? bboxCenter(boxed[0].bbox)
      : ([24.4667, 54.3667] as [number, number]) // UAE-wide fallback centroid

  return (
    <div className="relative h-full w-full">
      <MapContainer
        center={center}
        zoom={9}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitAndInvalidate bounds={bounds} isActive={isActive} />

        {highlightedLocation && (
          <Marker position={[highlightedLocation.lat, highlightedLocation.lon]}>
            <Popup>Detected location: {highlightedLocation.label}</Popup>
          </Marker>
        )}

        {boxed.map(({ doc, bbox }) => {
          const [minLon, minLat, maxLon, maxLat] = bbox
          const color = doc.type === "satellite" ? SATELLITE_COLOR : ROADS_COLOR
          return (
            <Rectangle
              key={doc.id}
              bounds={[
                [minLat, minLon],
                [maxLat, maxLon],
              ]}
              pathOptions={{ color, weight: 1.5, fillOpacity: 0.08 }}
            >
              <Popup>
                <span className="font-medium">{deriveDocumentTitle(doc)}</span>
                <br />
                Confidence: {doc.confidence.toFixed(1)}%
              </Popup>
            </Rectangle>
          )
        })}
      </MapContainer>

      <div className="pointer-events-none absolute bottom-3 left-3 z-[1000] flex flex-col gap-1 rounded-md border border-border/60 bg-card/90 px-2.5 py-1.5 text-[11px] backdrop-blur">
        {boxed.some((b) => b.doc.type === "satellite") && (
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-sm" style={{ backgroundColor: SATELLITE_COLOR }} />
            Satellite coverage
          </span>
        )}
        {boxed.some((b) => b.doc.type === "roads") && (
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-sm" style={{ backgroundColor: ROADS_COLOR }} />
            Road network
          </span>
        )}
        {highlightedLocation && (
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-primary" />
            Detected location
          </span>
        )}
      </div>
    </div>
  )
}
