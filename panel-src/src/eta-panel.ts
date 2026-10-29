import { LitElement, html, nothing, type TemplateResult } from "lit";

import {
  CONFIRM,
  LIVE_CONTROLS,
  OPEN_ROOMS,
  TABS,
  buildRooms,
  entitiesByPath,
  heroEntity,
  isBurning,
  isTab,
  leafName,
  type RawEntity,
  type Room,
  type TabId,
} from "./catalog";
import { bucketMean, numericPoints, type Point, type RawState } from "./history";
import { styles } from "./styles";

const COLLAPSE_KEY = "eta-heating.groups.v1";
const DAY = 24 * 60 * 60 * 1000;
const FIVE_MIN = 5 * 60 * 1000;
const EMPTY = new Set(["", "xxx", "unknown", "unavailable", "none", "None"]);
const NO_ALARM = new Set(["", "0", "Aus", "Keine", "Nein", "xxx", "unknown", "unavailable", "none", "None"]);

type HassState = { state: string; attributes: Record<string, unknown> };
type Hass = {
  language?: string;
  states: Record<string, HassState | undefined>;
  themes?: { darkMode?: boolean };
  callWS: <T>(message: object) => Promise<T>;
  callService: (domain: string, service: string, data?: object) => Promise<unknown>;
};
type Payload = {
  entries: { entry_id: string; host?: string; port?: number; entities: RawEntity[] }[];
};

const copy = {
  de: {
    title: "ETA",
    tag: "Heizung",
    liveSub: "Zustand der Anlage, ohne automatische Regelung.",
    roomSub: "Messpunkte und Handschalter aus diesem Anlagenteil.",
    empty: "Keine ETA-Entitäten geladen. In den Integrationsoptionen Messpunkte auswählen, danach Home Assistant neu starten.",
    offline: "Die ETA ist nicht erreichbar. Angezeigte Werte können veraltet sein.",
    unavailable: (n: number) => `${n} Messpunkte sind nicht verfügbar.`,
    disabled: (n: number) => `${n} Messpunkte sind deaktiviert.`,
    fault: "Störmeldung",
    errors: (n: string) => `${n} aktive Fehler`,
    host: "Anlage",
    controls: "Handsteuerung",
    confirmTitle: "Schalter betätigen?",
    confirmBody: "Das schreibt den Zustand direkt an die ETA. Eine Regelung übernimmt das nicht wieder.",
    cancel: "Abbrechen",
    apply: "Übernehmen",
    history: "Letzte 24 Stunden",
    noHistory: "Für diesen Messpunkt liegen keine Zahlen im Recorder.",
    close: "Schließen",
    search: "Messpunkt suchen",
    details: "Kalibrierung und Sensorzustand",
    schedule: "Zeitprogramm",
    more: "weitere",
    stock: "Vorrat",
    outdoor: "Außen",
    flow: "Kessel Vorlauf",
    returnTemp: "Kessel Rücklauf",
    bufferTop: "Puffer oben",
    bufferBottom: "Puffer unten",
    dhw: "Warmwasser",
    hopper: "Pelletsbehälter",
    hkFlow: "Heizkreis Vorlauf",
    hkReturn: "Heizkreis Rücklauf",
    power: "Anforderung",
    fan: "Abgasgebläse",
    ignition: "Zündung",
    flowRate: "Durchfluss",
    energy: "Wärme gesamt",
    kessel: "Kessel",
    puffer: "Puffer",
    heizkreis: "Heizkreis",
    wasser: "Warmwasser",
  },
  en: {
    title: "ETA",
    tag: "Heating",
    liveSub: "Plant status. Nothing here runs a control loop.",
    roomSub: "Readings and manual switches for this part of the plant.",
    empty: "No ETA entities loaded. Choose data points in the integration options, then restart Home Assistant.",
    offline: "The ETA is unreachable. Shown values may be stale.",
    unavailable: (n: number) => `${n} data points are unavailable.`,
    disabled: (n: number) => `${n} data points are disabled.`,
    fault: "Fault",
    errors: (n: string) => `${n} active errors`,
    host: "Plant",
    controls: "Manual control",
    confirmTitle: "Send this switch?",
    confirmBody: "This writes the state straight to the ETA. No controller sets it back.",
    cancel: "Cancel",
    apply: "Apply",
    history: "Last 24 hours",
    noHistory: "The recorder has no numeric history for this point.",
    close: "Close",
    search: "Find a data point",
    details: "Calibration and sensor health",
    schedule: "Schedule",
    more: "more",
    stock: "Store",
    outdoor: "Outside",
    flow: "Boiler flow",
    returnTemp: "Boiler return",
    bufferTop: "Buffer top",
    bufferBottom: "Buffer bottom",
    dhw: "Hot water",
    hopper: "Pellet hopper",
    hkFlow: "Circuit flow",
    hkReturn: "Circuit return",
    power: "Demand",
    fan: "Flue fan",
    ignition: "Ignition",
    flowRate: "Flow",
    energy: "Heat total",
    kessel: "Boiler",
    puffer: "Buffer",
    heizkreis: "Circuit",
    wasser: "Hot water",
  },
} as const;

type Copy = { [K in keyof typeof copy.de]: (typeof copy.de)[K] extends (...args: infer A) => infer R ? (...args: A) => R : string };

const text = (lang: string | undefined): Copy => (lang?.toLowerCase().startsWith("en") ? copy.en : copy.de);

const display = (state: string | undefined, unit: string | undefined, lang: string): string => {
  if (state === undefined || EMPTY.has(state)) return "–";
  if (/^-?\d+(\.\d+)?$/.test(state)) {
    const value = Number(state);
    const digits = Number.isInteger(value) ? 0 : 1;
    const formatted = value.toLocaleString(lang, { maximumFractionDigits: digits });
    return unit ? `${formatted} ${unit}` : formatted;
  }
  return state;
};

const icon = (path: string) =>
  html`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d=${path} /></svg>`;

const ICONS: Record<TabId, string> = {
  live: "M12 3v3M12 18v3M3 12h3M18 12h3M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z",
  kessel: "M4 20V10h16v10M8 10V6h8v4M9 14h.01M12 14h.01M15 14h.01",
  puffer: "M7 3h10v18H7zM7 8h10M7 16h10",
  heizkreis: "M4 12h16M7 12a5 5 0 0 1 10 0",
  wasser: "M12 3s6 6.2 6 10a6 6 0 0 1-12 0c0-3.8 6-10 6-10z",
  lager: "M3 9 12 4l9 5-9 5-9-5zM3 14l9 5 9-5",
  anlage: "M12 3 4 7v6c0 5 3.4 7.6 8 8 4.6-.4 8-3 8-8V7l-8-4z",
};

const loadCollapsed = (): Set<string> | undefined => {
  const raw = localStorage.getItem(COLLAPSE_KEY);
  if (raw === null) return undefined;
  try {
    const parsed: unknown = JSON.parse(raw);
    return new Set(Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string") : []);
  } catch {
    return new Set();
  }
};

export class EtaPanel extends LitElement {
  static styles = styles;

  private _hass?: Hass;
  private _payload?: Payload;
  private _error?: string;
  private _screen: TabId = isTab(location.hash.slice(1)) ? (location.hash.slice(1) as TabId) : "live";
  private _query = "";
  private _collapsed = loadCollapsed();
  private _ids = new Set<string>();
  private _resolving = false;
  private _pending?: { entity: RawEntity; turnOn: boolean };
  private _chart?: { entity: RawEntity; points?: Point[]; failed?: boolean; loading?: boolean };
  private _chartToken = 0;

  set hass(hass: Hass) {
    const prev = this._hass;
    this._hass = hass;
    this._applyTheme(hass);
    if (!this._payload) void this._resolve();
    const changed =
      !prev ||
      prev.language !== hass.language ||
      [...this._ids].some((id) => prev.states[id]?.state !== hass.states[id]?.state);
    if (changed) this.requestUpdate();
  }

  get hass(): Hass | undefined {
    return this._hass;
  }

  override connectedCallback(): void {
    super.connectedCallback();
    window.addEventListener("hashchange", this._onHash);
    window.addEventListener("keydown", this._onKey);
  }

  override disconnectedCallback(): void {
    window.removeEventListener("hashchange", this._onHash);
    window.removeEventListener("keydown", this._onKey);
    super.disconnectedCallback();
  }

  private _onHash = (): void => {
    const next = location.hash.slice(1);
    if (isTab(next) && next !== this._screen) {
      this._screen = next;
      this._query = "";
      this.requestUpdate();
    }
  };

  private _onKey = (event: KeyboardEvent): void => {
    if (event.key !== "Escape") return;
    this._pending = undefined;
    this._chart = undefined;
    this.requestUpdate();
  };

  private _applyTheme(hass: Hass): void {
    const dark = hass.themes?.darkMode;
    const theme = typeof dark === "boolean" ? (dark ? "dark" : "classic") : "dark";
    if (this.getAttribute("theme") !== theme) this.setAttribute("theme", theme);
  }

  private async _resolve(): Promise<void> {
    if (!this._hass || this._resolving) return;
    this._resolving = true;
    try {
      this._payload = await this._hass.callWS<Payload>({ type: "eta_heating_technology/panel_entities" });
      this._ids = new Set(this._payload.entries.flatMap((entry) => entry.entities.map((entity) => entity.entity_id)));
      this._error = undefined;
    } catch (err) {
      this._error = err instanceof Error ? err.message : String(err);
    } finally {
      this._resolving = false;
      this.requestUpdate();
    }
  }

  private _lang(): string {
    return this._hass?.language ?? "de";
  }

  private _state(entity: RawEntity | undefined): HassState | undefined {
    if (!entity || !this._hass) return undefined;
    return this._hass.states[entity.entity_id];
  }

  private _value(entity: RawEntity | undefined): string {
    const state = this._state(entity);
    const unit = state?.attributes.unit_of_measurement;
    return display(state?.state, typeof unit === "string" ? unit : undefined, this._lang());
  }

  private _go(screen: TabId): void {
    location.hash = screen;
  }

  private _entities(): RawEntity[] {
    return this._payload?.entries[0]?.entities ?? [];
  }

  private _toggleRoom(room: Room): void {
    const entities = this._entities();
    if (!this._collapsed) {
      this._collapsed = new Set();
      for (const tab of TABS) {
        if (tab.id === "live") continue;
        for (const item of buildRooms(entities, tab.id)) {
          if (!OPEN_ROOMS.has(item.title)) this._collapsed.add(item.id);
        }
      }
    }
    if (this._collapsed.has(room.id)) this._collapsed.delete(room.id);
    else this._collapsed.add(room.id);
    localStorage.setItem(COLLAPSE_KEY, JSON.stringify([...this._collapsed]));
    this.requestUpdate();
  }

  private _open(room: Room): boolean {
    if (!this._collapsed) return OPEN_ROOMS.has(room.title);
    return !this._collapsed.has(room.id);
  }

  private async _setSwitch(entity: RawEntity, turnOn: boolean): Promise<void> {
    this._pending = undefined;
    await this._hass?.callService("switch", turnOn ? "turn_on" : "turn_off", { entity_id: entity.entity_id });
    this.requestUpdate();
  }

  private _ask(entity: RawEntity): void {
    const turnOn = this._state(entity)?.state !== "on";
    if (CONFIRM.has(entity.path)) {
      this._pending = { entity, turnOn };
      this.requestUpdate();
      return;
    }
    void this._setSwitch(entity, turnOn);
  }

  private async _openChart(entity: RawEntity): Promise<void> {
    const state = this._state(entity)?.state;
    if (entity.domain !== "sensor" || state === undefined || !/^-?\d+(\.\d+)?$/.test(state)) return;
    const token = ++this._chartToken;
    this._chart = { entity, loading: true };
    this.requestUpdate();
    try {
      const raw = await this._hass?.callWS<Record<string, RawState[]>>({
        type: "history/history_during_period",
        start_time: new Date(Date.now() - DAY).toISOString(),
        end_time: new Date().toISOString(),
        entity_ids: [entity.entity_id],
        minimal_response: true,
        no_attributes: true,
        significant_changes_only: true,
      });
      if (token !== this._chartToken) return;
      this._chart = { entity, points: bucketMean(numericPoints(raw?.[entity.entity_id]), FIVE_MIN) };
    } catch {
      if (token !== this._chartToken) return;
      this._chart = { entity, failed: true };
    }
    this.requestUpdate();
  }

  private _switchRow(entities: RawEntity[], label: string): TemplateResult | typeof nothing {
    if (!entities.length) return nothing;
    return html`
      <h2>${label}</h2>
      <div class="controls">
        ${entities.map(
          (entity) => html`
            <button class="switch" aria-pressed=${this._state(entity)?.state === "on"} @click=${() => this._ask(entity)}>
              <span class="name">${leafName(entity.path)}</span>
            </button>
          `,
        )}
      </div>
    `;
  }

  private _tile(entity: RawEntity): TemplateResult {
    return html`
      <button class="tile" @click=${() => this._openChart(entity)}>
        <span>${leafName(entity.path)}</span>
        <b>${this._value(entity)}</b>
      </button>
    `;
  }

  private _ratio(part: RawEntity | undefined, total: RawEntity | undefined): TemplateResult | typeof nothing {
    const value = Number(this._state(part)?.state);
    const max = Number(this._state(total)?.state);
    if (!Number.isFinite(value) || !Number.isFinite(max) || max <= 0) return nothing;
    const pct = Math.max(0, Math.min(100, (value / max) * 100));
    return html`<div class="bar"><i style=${`width:${pct}%`}></i></div>`;
  }

  private _live(i18n: Copy): TemplateResult {
    const entities = this._entities();
    const pick = (key: string) => heroEntity(entities, key);
    const state = pick("state");
    const stateText = this._state(state)?.state;
    const burning = isBurning(stateText);
    const fault = this._state(pick("fault"))?.state;
    const errors = this._state(pick("errors"))?.state;
    const showFault = !!fault && !NO_ALARM.has(fault);
    const showErrors = !!errors && !NO_ALARM.has(errors);
    const entry = this._payload?.entries[0];
    const line = (entity: RawEntity | undefined, label: string) =>
      entity ? html`<p>${label} <b>${this._value(entity)}</b></p>` : nothing;
    return html`
      ${showFault ? html`<div class="banner">${i18n.fault}: ${fault}</div>` : nothing}
      ${showErrors ? html`<div class="banner">${i18n.errors(errors ?? "")}</div>` : nothing}
      <section class="hero">
        <div class="hero-top">
          <div>
            <p class="state ${burning ? "burn" : ""} ${stateText === "Störung" ? "fault" : ""}">${display(stateText, undefined, this._lang())}</p>
            <p class="meta">${i18n.host} ${entry?.host ?? "–"}${entry?.port ? `:${entry.port}` : ""}</p>
          </div>
          <div class="meta">
            ${line(pick("power"), i18n.power)}
            ${line(pick("fan"), i18n.fan)}
            ${line(pick("ignition"), i18n.ignition)}
          </div>
        </div>
      </section>
      <div class="schematic">
        <div class="node kessel ${burning ? "burn" : ""}">
          <strong>${i18n.kessel}</strong>
          ${line(pick("flow"), i18n.flow)}
          ${line(pick("returnTemp"), i18n.returnTemp)}
          ${line(pick("hopper"), i18n.hopper)}
        </div>
        <div class="node puffer">
          <strong>${i18n.puffer}</strong>
          ${line(pick("bufferTop"), i18n.bufferTop)}
          ${line(pick("bufferBottom"), i18n.bufferBottom)}
        </div>
        <div class="node kreis">
          <strong>${i18n.heizkreis}</strong>
          ${line(pick("hkFlow"), i18n.hkFlow)}
          ${line(pick("hkReturn"), i18n.hkReturn)}
        </div>
        <div class="node wasser">
          <strong>${i18n.wasser}</strong>
          ${line(pick("dhw"), i18n.dhw)}
          ${line(pick("flowRate"), i18n.flowRate)}
        </div>
      </div>
      <div class="kpis">
        ${this._kpi(pick("outdoor"), i18n.outdoor)}
        ${this._kpi(pick("stock"), i18n.stock, pick("stockMax"))}
        ${this._kpi(pick("energy"), i18n.energy)}
        ${this._kpi(pick("dhwSet"), "Soll")}
        ${this._kpi(pick("bufferPump"), "Pufferpumpe")}
        ${this._kpi(pick("mixPump"), "Beimischpumpe")}
      </div>
      ${this._switchRow(entitiesByPath(entities, LIVE_CONTROLS), i18n.controls)}
    `;
  }

  private _kpi(entity: RawEntity | undefined, label: string, max?: RawEntity): TemplateResult | typeof nothing {
    if (!entity) return nothing;
    return html`
      <button class="tile" @click=${() => this._openChart(entity)}>
        <span>${label}</span>
        <b>${this._value(entity)}</b>
        ${this._ratio(entity, max)}
      </button>
    `;
  }

  private _rooms(i18n: Copy): TemplateResult {
    const query = this._query.trim().toLowerCase();
    const rooms = buildRooms(this._entities(), this._screen)
      .map((room) => ({
        ...room,
        switches: room.switches.filter((entity) => !query || entity.path.toLowerCase().includes(query)),
        tiles: room.tiles.filter((entity) => !query || entity.path.toLowerCase().includes(query)),
        details: room.details.filter((entity) => !query || entity.path.toLowerCase().includes(query)),
        schedule: room.schedule.filter((entity) => !query || entity.path.toLowerCase().includes(query)),
      }))
      .filter((room) => room.switches.length + room.tiles.length + room.details.length + room.schedule.length > 0);
    return html`
      <input class="search" type="search" placeholder=${i18n.search} .value=${this._query} @input=${(event: Event) => {
        this._query = (event.target as HTMLInputElement).value;
        this.requestUpdate();
      }} />
      ${rooms.map((room) => {
        const count = room.tiles.length + room.switches.length;
        const open = query.length > 0 || this._open(room);
        return html`
          <section class="room">
            <button class="room-head" aria-expanded=${open} @click=${() => this._toggleRoom(room)}>
              <b>${room.title}</b><span>${count}</span>
            </button>
            ${open
              ? html`
                  <div class="controls">
                    ${room.switches.map(
                      (entity) => html`
                        <button class="switch" aria-pressed=${this._state(entity)?.state === "on"} @click=${() => this._ask(entity)}>
                          <span class="name">${leafName(entity.path)}</span>
                        </button>
                      `,
                    )}
                  </div>
                  <div class="tiles">${room.tiles.map((entity) => this._tile(entity))}</div>
                  ${room.schedule.length
                    ? html`<details class="details"><summary>${i18n.schedule} (${room.schedule.length})</summary><div class="tiles">${room.schedule.map((entity) => this._tile(entity))}</div></details>`
                    : nothing}
                  ${room.details.length
                    ? html`<details class="details"><summary>${i18n.details} (${room.details.length})</summary><div class="tiles">${room.details.map((entity) => this._tile(entity))}</div></details>`
                    : nothing}
                `
              : nothing}
          </section>
        `;
      })}
    `;
  }

  private _chartSvg(points: Point[]): TemplateResult {
    const min = Math.min(...points.map((point) => point.v));
    const max = Math.max(...points.map((point) => point.v));
    const span = max - min || 1;
    const width = 720;
    const height = 200;
    const path = points
      .map((point, index) => {
        const x = (index / Math.max(points.length - 1, 1)) * width;
        const y = height - ((point.v - min) / span) * (height - 20) - 10;
        return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
    return html`<svg class="chart" viewBox="0 0 ${width} ${height}" role="img"><path d=${path} fill="none" stroke="#f59e0b" stroke-width="3" /></svg>`;
  }

  override render(): TemplateResult {
    const i18n = text(this._hass?.language);
    const entities = this._entities();
    const tab = TABS.find((item) => item.id === this._screen) ?? TABS[0];
    const unavailable = entities.filter((entity) => this._state(entity)?.state === "unavailable" && !entity.disabled);
    const offline = entities.length > 0 && unavailable.length === entities.filter((entity) => !entity.disabled).length;
    const disabled = entities.filter((entity) => entity.disabled).length;
    const nav = (extra: string) =>
      TABS.map(
        (item) => html`
          <button class=${extra} aria-current=${item.id === this._screen ? "page" : nothing} @click=${() => this._go(item.id)}>
            ${extra === "nav-btn" ? icon(ICONS[item.id]) : nothing}
            ${item.id === "live" ? item.label : item.label}
          </button>
        `,
      );
    return html`
      <div class="shell">
        <nav class="rail" aria-label="ETA">
          <div class="brand"><b>${i18n.title}</b><span>${i18n.tag}</span></div>
          ${nav("nav-btn")}
        </nav>
        <main class="main">
          <h1>${tab?.label}</h1>
          <p class="sub">${this._screen === "live" ? i18n.liveSub : i18n.roomSub}</p>
          ${this._error ? html`<div class="banner">${this._error}</div>` : nothing}
          ${offline ? html`<div class="banner">${i18n.offline}</div>` : nothing}
          ${!offline && unavailable.length ? html`<div class="banner warn">${i18n.unavailable(unavailable.length)}</div>` : nothing}
          ${disabled ? html`<div class="banner warn">${i18n.disabled(disabled)}</div>` : nothing}
          ${entities.length === 0 && this._payload ? html`<div class="banner warn">${i18n.empty}</div>` : nothing}
          ${this._screen === "live" ? this._live(i18n) : this._rooms(i18n)}
        </main>
        <nav class="bottom">${nav("")}</nav>
      </div>
      ${this._chart
        ? html`
            <div class="sheet" @click=${(event: Event) => {
              if (event.target === event.currentTarget) {
                this._chart = undefined;
                this.requestUpdate();
              }
            }}>
              <article>
                <h2>${leafName(this._chart.entity.path)}</h2>
                <p class="sub">${i18n.history} · ${this._value(this._chart.entity)}</p>
                ${this._chart.loading
                  ? html`<p class="sub">…</p>`
                  : this._chart.points && this._chart.points.length > 1
                    ? this._chartSvg(this._chart.points)
                    : html`<p>${i18n.noHistory}</p>`}
                <button class="text-btn" @click=${() => {
                  this._chart = undefined;
                  this.requestUpdate();
                }}>${i18n.close}</button>
              </article>
            </div>
          `
        : nothing}
      ${this._pending
        ? html`
            <div class="dialog">
              <article>
                <h2>${i18n.confirmTitle}</h2>
                <p>${leafName(this._pending.entity.path)}. ${i18n.confirmBody}</p>
                <div class="controls">
                  <button class="text-btn" @click=${() => {
                    this._pending = undefined;
                    this.requestUpdate();
                  }}>${i18n.cancel}</button>
                  <button class="switch" aria-pressed="true" @click=${() => this._pending && this._setSwitch(this._pending.entity, this._pending.turnOn)}>${i18n.apply}</button>
                </div>
              </article>
            </div>
          `
        : nothing}
    `;
  }
}

customElements.define("eta-heating-panel", EtaPanel);

declare global {
  interface HTMLElementTagNameMap {
    "eta-heating-panel": EtaPanel;
  }
}
