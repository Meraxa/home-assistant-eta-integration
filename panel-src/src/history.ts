/** History rows from `history/history_during_period`, compressed or full. */

export type RawState = {
  s?: string;
  state?: string;
  lu?: number;
  lc?: number;
  last_changed?: string;
  last_updated?: string;
};

export type Point = { t: number; v: number };

export function numericPoints(rows: RawState[] | undefined): Point[] {
  const points: Point[] = [];
  for (const row of rows ?? []) {
    const sec = row.lc ?? row.lu;
    const t = sec !== undefined ? sec * 1000 : Date.parse(row.last_changed ?? row.last_updated ?? "");
    const v = Number.parseFloat(row.s ?? row.state ?? "");
    if (Number.isFinite(t) && Number.isFinite(v)) points.push({ t, v });
  }
  return points;
}

/** Mean per bucket so a 24 h line stays readable. */
export function bucketMean(points: Point[], stepMs: number): Point[] {
  const buckets = new Map<number, { sum: number; n: number }>();
  for (const point of points) {
    const key = Math.floor(point.t / stepMs) * stepMs;
    const bucket = buckets.get(key) ?? { sum: 0, n: 0 };
    bucket.sum += point.v;
    bucket.n += 1;
    buckets.set(key, bucket);
  }
  return [...buckets.entries()]
    .sort(([a], [b]) => a - b)
    .map(([t, bucket]) => ({ t, v: bucket.sum / bucket.n }));
}
