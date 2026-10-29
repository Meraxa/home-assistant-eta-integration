import { describe, expect, it } from "vitest";

import {
  buildRooms,
  entitiesByPath,
  folderPaths,
  heroEntity,
  isDetail,
  isSchedule,
  roomTitle,
  tabOf,
  type RawEntity,
} from "./catalog";
import { bucketMean, numericPoints } from "./history";

const entity = (path: string, domain = "sensor"): RawEntity => ({
  entity_id: `sensor.${path.length}`,
  domain,
  path,
  disabled: false,
});

describe("menu tree", () => {
  it("maps ETA menu roots onto cockpit tabs and keeps unknown points on Anlage", () => {
    expect(tabOf("Kessel.Kessel")).toBe("kessel");
    expect(tabOf("PufferFlex.Puffer.Erzeuger Kessel/Puffer.Puffer oben")).toBe("puffer");
    expect(tabOf("Wasser.Eingänge.Warmwasser")).toBe("wasser");
    expect(tabOf("Sys.Störmeldung")).toBe("anlage");
    expect(tabOf("active_errors")).toBe("anlage");
    expect(tabOf("/120/10101/0/0/12168")).toBe("anlage");
  });

  it("splits the wide Puffer and Heizkreis branches one level deeper", () => {
    expect(roomTitle("PufferFlex.Puffer.Warmwasserbereich.Soll Temperatur")).toBe("Warmwasserbereich");
    expect(roomTitle("Heizkreis.Heizkreis.Vorlauf")).toBe("Vorlauf");
    expect(roomTitle("Kessel.Ausgänge.Zündung")).toBe("Ausgänge");
    expect(roomTitle("Wasser.Warmwasser.Soll Temperatur")).toBe("Soll Temperatur");
  });

  it("hides menu folders and parks calibration, sensor health and week plans", () => {
    const paths = ["Kessel.Eingänge", "Kessel.Eingänge.Wärmemessung.Vorlauf", "Kessel.Kessel"];
    expect(folderPaths(paths)).toEqual(new Set(["Kessel.Eingänge"]));
    expect(isDetail("Wasser.Eingänge.Warmwasser.Kalibrierwert")).toBe(true);
    expect(isDetail("Wasser.Eingänge.Warmwasser.Zustand")).toBe(true);
    expect(isDetail("Kessel.Kessel")).toBe(false);
    expect(isSchedule("Heizkreis.Heizkreis.Heizzeiten.Montag.Zeitfenster 1")).toBe(true);
    expect(isSchedule("Heizkreis.Heizkreis.Vorlauf")).toBe(false);
  });

  it("builds rooms with switches kept separate from readings", () => {
    const rooms = buildRooms(
      [
        entity("Kessel.Eingänge"),
        entity("Kessel.Eingänge.Wärmemessung.Vorlauf"),
        entity("Kessel.Ausgänge.Zündung"),
        entity("Kessel.Sonstiges.Ein/Aus Taste", "switch"),
        entity("Kessel.Eingänge.Warmwasser.Kalibrierwert"),
      ],
      "kessel",
    );
    const outputs = rooms.find((room) => room.title === "Ausgänge");
    const controls = rooms.find((room) => room.title === "Sonstiges");
    expect(outputs?.tiles.map((item) => item.path)).toEqual(["Kessel.Ausgänge.Zündung"]);
    expect(controls?.switches).toHaveLength(1);
    expect(rooms.some((room) => room.title === "Eingänge" && room.tiles.length === 1)).toBe(true);
  });

  it("resolves hero points and falls back to a suffix on other installations", () => {
    const entities = [
      entity("Kessel.Kessel"),
      entity("PufferFlex.Puffer.Erzeuger Solar.Puffer oben"),
    ];
    expect(heroEntity(entities, "state")?.path).toBe("Kessel.Kessel");
    expect(heroEntity(entities, "bufferTop")?.path).toBe("PufferFlex.Puffer.Erzeuger Solar.Puffer oben");
    expect(entitiesByPath(entities, ["Kessel.Kessel", "missing"])).toHaveLength(1);
  });
});

describe("history", () => {
  it("reads compressed and full history rows", () => {
    expect(
      numericPoints([
        { s: "61.0", lu: 1_700_000_000 },
        { state: "xx", last_updated: "2026-01-01T00:00:00Z" },
        { state: "12.5", last_changed: "2026-01-01T00:05:00Z" },
      ]),
    ).toEqual([
      { t: 1_700_000_000_000, v: 61 },
      { t: Date.parse("2026-01-01T00:05:00Z"), v: 12.5 },
    ]);
  });

  it("averages points inside a bucket", () => {
    expect(
      bucketMean(
        [
          { t: 0, v: 10 },
          { t: 10, v: 30 },
          { t: 120, v: 5 },
        ],
        60,
      ),
    ).toEqual([
      { t: 0, v: 20 },
      { t: 120, v: 5 },
    ]);
  });
});
