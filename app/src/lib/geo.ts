import type { GeoCollection, GeoFeature } from "../types";

export interface BBox {
  minLon: number;
  minLat: number;
  maxLon: number;
  maxLat: number;
}

export interface Pt {
  x: number;
  y: number;
}

type Ring = number[][];
type Poly = Ring[];

function asPolys(feature: GeoFeature): Poly[] {
  const g = feature.geometry;
  if (g.type === "Polygon") return [g.coordinates as Poly];
  return g.coordinates as Poly[];
}

function walkCoords(feature: GeoFeature, fn: (lon: number, lat: number) => void) {
  for (const poly of asPolys(feature)) {
    for (const ring of poly) {
      for (const c of ring) fn(c[0], c[1]);
    }
  }
}

export function featuresBBox(features: GeoFeature[]): BBox {
  let minLon = Infinity,
    minLat = Infinity,
    maxLon = -Infinity,
    maxLat = -Infinity;
  for (const f of features) {
    walkCoords(f, (lon, lat) => {
      if (lon < minLon) minLon = lon;
      if (lat < minLat) minLat = lat;
      if (lon > maxLon) maxLon = lon;
      if (lat > maxLat) maxLat = lat;
    });
  }
  return { minLon, minLat, maxLon, maxLat };
}

export function makeProjector(bbox: BBox, width: number, height: number, pad = 8) {
  const midLat = (bbox.minLat + bbox.maxLat) / 2;
  const cos = Math.cos((midLat * Math.PI) / 180);
  const dx = (bbox.maxLon - bbox.minLon) * cos || 1;
  const dy = bbox.maxLat - bbox.minLat || 1;
  const innerW = width - pad * 2;
  const innerH = height - pad * 2;
  const scale = Math.min(innerW / dx, innerH / dy);
  const usedW = dx * scale;
  const usedH = dy * scale;
  const ox = (width - usedW) / 2;
  const oy = (height - usedH) / 2;
  return (lon: number, lat: number): Pt => ({
    x: ox + (lon - bbox.minLon) * cos * scale,
    y: oy + (bbox.maxLat - lat) * scale,
  });
}

export function featurePath(feature: GeoFeature, project: (lon: number, lat: number) => Pt): string {
  const parts: string[] = [];
  for (const poly of asPolys(feature)) {
    for (const ring of poly) {
      const d = ring
        .map((c, i) => {
          const p = project(c[0], c[1]);
          return `${i === 0 ? "M" : "L"}${p.x.toFixed(2)} ${p.y.toFixed(2)}`;
        })
        .join(" ");
      parts.push(d + " Z");
    }
  }
  return parts.join(" ");
}

export function featureCentroid(feature: GeoFeature): { lon: number; lat: number } {
  // Average of the largest outer ring (sufficient for labels on a simplified map).
  let best: Ring = [];
  let bestLen = -1;
  for (const poly of asPolys(feature)) {
    const outer = poly[0];
    if (outer && outer.length > bestLen) {
      best = outer;
      bestLen = outer.length;
    }
  }
  let lon = 0,
    lat = 0,
    n = 0;
  for (const c of best) {
    lon += c[0];
    lat += c[1];
    n += 1;
  }
  return { lon: lon / (n || 1), lat: lat / (n || 1) };
}

export const UUSIMAA_IDS = new Set(["01", "02", "03", "04", "90"]);

export function byId(geo: GeoCollection): Map<string, GeoFeature> {
  return new Map(geo.features.map((f) => [f.properties.id, f]));
}
