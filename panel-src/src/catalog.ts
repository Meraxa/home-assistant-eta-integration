/** Menu-path grouping for the ETA cockpit. The device names the tree; tabs only fold it. */

export type RawEntity = {
  entity_id: string;
  domain: string;
  path: string;
  disabled: boolean;
};

export type TabId = "live" | "kessel" | "puffer" | "heizkreis" | "wasser" | "lager" | "anlage";

export const TABS: { id: TabId; label: string }[] = [
  { id: "live", label: "Live" },
  { id: "kessel", label: "Kessel" },
  { id: "puffer", label: "Puffer" },
  { id: "heizkreis", label: "Heizkreis" },
  { id: "wasser", label: "Warmwasser" },
  { id: "lager", label: "Lager" },
  { id: "anlage", label: "Anlage" },
];

const TAB_ROOT: Record<string, TabId> = {
  Kessel: "kessel",
  PufferFlex: "puffer",
  Heizkreis: "heizkreis",
  Wasser: "wasser",
  Lager: "lager",
  Sys: "anlage",
};

/** Second path segment is too wide; split these one level deeper. */
const DEEP = new Set(["PufferFlex.Puffer", "Heizkreis.Heizkreis", "Wasser.Warmwasser", "Wasser.Zirkulation"]);

const DAYS = new Set(["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]);
const DETAIL_LEAF = new Set(["Kalibrierwert", "Sensor Typ", "Fixwert", "Extrapol", "Impulse pro Liter", "Zustand"]);

export type Room = {
  id: string;
  title: string;
  switches: RawEntity[];
  tiles: RawEntity[];
  details: RawEntity[];
  schedule: RawEntity[];
};

export type HeroSpec = { key: string; path: string; fallback?: string };

export const HERO: HeroSpec[] = [
  { key: "state", path: "Kessel.Kessel" },
  { key: "fault", path: "Sys.Störmeldung" },
  { key: "boilerFault", path: "Kessel.Kessel.Kesselstörmeldung" },
  { key: "errors", path: "active_errors" },
  { key: "outdoor", path: "Sys.Außentemperatur.Außentemperaturfühler" },
  { key: "flow", path: "Kessel.Eingänge.Wärmemessung.Vorlauf" },
  { key: "returnTemp", path: "Kessel.Ausgänge.Rücklaufmischer.Ist Temperatur" },
  { key: "bufferTop", path: "PufferFlex.Puffer.Erzeuger Kessel/Puffer.Puffer oben", fallback: ".Puffer oben" },
  { key: "bufferBottom", path: "PufferFlex.Puffer.Erzeuger Kessel/Puffer.Puffer unten", fallback: ".Puffer unten" },
  { key: "dhw", path: "Wasser.Eingänge.Warmwasser" },
  { key: "dhwSet", path: "Wasser.Warmwasser.Soll Temperatur" },
  { key: "hopper", path: "Kessel.Kessel.Pelletsbehälter.Inhalt Pelletsbehälter" },
  { key: "stock", path: "Lager.Vorrat" },
  { key: "stockMax", path: "Lager.Vorrat.Maximaler Vorrat" },
  { key: "energy", path: "Kessel.Zählerstände.Wärmemessung.Energie" },
  { key: "fan", path: "Kessel.Ausgänge.Abgasgebläse" },
  { key: "ignition", path: "Kessel.Ausgänge.Zündung" },
  { key: "power", path: "Kessel.Kessel.Vorlauf.Angeforderte Leistung" },
  { key: "hkFlow", path: "Heizkreis.Heizkreis.Vorlauf", fallback: ".Vorlauf" },
  { key: "hkReturn", path: "Heizkreis.Heizkreis.Rücklauf" },
  { key: "hkSet", path: "Heizkreis.Ausgänge.Heizkreismischer.Soll Temperatur" },
  { key: "primaryFlow", path: "Wasser.Eingänge.Primär Vorlauf" },
  { key: "flowRate", path: "Wasser.Warmwasser.Sekundär Durchfluss" },
  { key: "bufferPump", path: "Wasser.Ausgänge.Pufferpumpe.Ausgang" },
  { key: "mixPump", path: "Wasser.Ausgänge.Beimischpumpe.Ausgang" },
];

export const LIVE_CONTROLS = [
  "Kessel.Sonstiges.Ein/Aus Taste",
  "Heizkreis.Sonstiges.Heizen Taste",
  "Heizkreis.Sonstiges.Auto Taste",
  "Heizkreis.Sonstiges.Absenken Taste",
  "Heizkreis.Sonstiges.Kommen Taste",
  "Heizkreis.Sonstiges.Gehen Taste",
  "Heizkreis.Sonstiges.Ein/Aus Taste",
  "PufferFlex.Puffer.Erzeuger Kessel/Puffer.Starten nach zusätzlichen Kriterien.Extra laden.Sofort laden",
  "PufferFlex.Puffer.Warmwasserbereich.Warmwasser sofort laden",
  "Wasser.Sonstiges.Ein/Aus Taste",
];

/** Actions that stop heat or start a long program. The panel asks first. */
export const CONFIRM = new Set([
  "Kessel.Sonstiges.Ein/Aus Taste",
  "Heizkreis.Sonstiges.Ein/Aus Taste",
  "Wasser.Sonstiges.Ein/Aus Taste",
  "Heizkreis.Heizkreis.Estrich.Start Estrich ausheizen",
]);

export const OPEN_ROOMS = new Set([
  "Eingänge",
  "Ausgänge",
  "Kessel",
  "Vorrat",
  "Außentemperatur",
  "Störmeldung",
  "Vorlauf",
  "Rücklauf",
]);

const BURNING = new Set(["Heizversuch", "Zünden", "Heizen", "Glutabbrand", "Glutabbrand wegen Entaschung", "Füllen", "Entaschen", "Stoker leeren"]);

export const isBurning = (state: string | undefined): boolean => !!state && BURNING.has(state);

export function splitPath(path: string): string[] {
  if (path.startsWith("/")) return ["Weitere", path];
  return path.split(".").filter((part) => part.length > 0);
}

export function tabOf(path: string): TabId {
  return TAB_ROOT[splitPath(path)[0] ?? ""] ?? "anlage";
}

export function roomTitle(path: string): string {
  const parts = splitPath(path);
  if (parts[0] === "Weitere" || parts[0] === "active_errors") return parts[0] === "active_errors" ? "Störung" : "Weitere";
  const head = parts.slice(0, 2).join(".");
  if (DEEP.has(head) && parts[2]) return parts[2];
  return parts[1] ?? parts[0] ?? "Allgemein";
}

export function leafName(path: string): string {
  const parts = splitPath(path);
  return parts[parts.length - 1] ?? path;
}

export function isSchedule(path: string): boolean {
  return splitPath(path).some((part) => DAYS.has(part) || part.startsWith("Zeitfenster") || part.startsWith("Wert außerhalb"));
}

export function isDetail(path: string): boolean {
  const parts = splitPath(path);
  const leaf = parts[parts.length - 1] ?? "";
  if (DETAIL_LEAF.has(leaf)) return true;
  return parts.some((part) => /^Lin [xy]\d*$/.test(part) || /^Lag [xy]$/.test(part));
}

export function folderPaths(paths: readonly string[]): Set<string> {
  const folders = new Set<string>();
  for (const path of paths) {
    if (path.startsWith("/")) continue;
    const prefix = `${path}.`;
    if (paths.some((other) => other.startsWith(prefix))) folders.add(path);
  }
  return folders;
}

const byPath = (a: RawEntity, b: RawEntity) => a.path.localeCompare(b.path, "de");

export function buildRooms(entities: readonly RawEntity[], tab: TabId): Room[] {
  const folders = folderPaths(entities.map((entity) => entity.path));
  const rooms = new Map<string, Room>();
  for (const entity of entities) {
    if (entity.disabled || tabOf(entity.path) !== tab || folders.has(entity.path)) continue;
    const title = roomTitle(entity.path);
    const id = `${tab}/${title}`;
    let room = rooms.get(id);
    if (!room) {
      room = { id, title, switches: [], tiles: [], details: [], schedule: [] };
      rooms.set(id, room);
    }
    if (entity.domain === "switch") room.switches.push(entity);
    else if (isSchedule(entity.path)) room.schedule.push(entity);
    else if (isDetail(entity.path)) room.details.push(entity);
    else room.tiles.push(entity);
  }
  for (const room of rooms.values()) {
    room.switches.sort(byPath);
    room.tiles.sort(byPath);
    room.details.sort(byPath);
    room.schedule.sort(byPath);
  }
  return [...rooms.values()].sort((a, b) => a.title.localeCompare(b.title, "de"));
}

export function indexByPath(entities: readonly RawEntity[]): Map<string, RawEntity> {
  const map = new Map<string, RawEntity>();
  for (const entity of entities) {
    if (!entity.disabled && !map.has(entity.path)) map.set(entity.path, entity);
  }
  return map;
}

export function heroEntity(entities: readonly RawEntity[], key: string): RawEntity | undefined {
  const spec = HERO.find((item) => item.key === key);
  if (!spec) return undefined;
  const map = indexByPath(entities);
  const exact = map.get(spec.path);
  if (exact) return exact;
  if (!spec.fallback) return undefined;
  return entities.find((entity) => !entity.disabled && !entity.path.startsWith("/") && entity.path.endsWith(spec.fallback ?? ""));
}

export function entitiesByPath(entities: readonly RawEntity[], paths: readonly string[]): RawEntity[] {
  const map = indexByPath(entities);
  return paths.flatMap((path) => {
    const entity = map.get(path);
    return entity ? [entity] : [];
  });
}

export function isTab(value: string): value is TabId {
  return TABS.some((tab) => tab.id === value);
}
