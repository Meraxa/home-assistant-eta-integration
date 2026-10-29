import { css } from "lit";

export const styles = css`
  :host {
    --bg: #100c09;
    --text: #f6efe6;
    --muted: #b5a89a;
    --faint: #7d7268;
    --stroke: rgba(255, 236, 214, 0.1);
    --stroke-strong: rgba(255, 236, 214, 0.18);
    --card: linear-gradient(180deg, rgba(255, 244, 230, 0.07), rgba(255, 244, 230, 0.03));
    --rail: rgba(16, 12, 9, 0.88);
    --accent: #f59e0b;
    --ember: #fb7185;
    --water: #67e8f9;
    --buffer: #c4b5fd;
    --ok: #34d399;
    --field: rgba(0, 0, 0, 0.28);
    --shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
    color-scheme: dark;
    display: block;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    color: var(--text);
    font-family: Inter, system-ui, sans-serif;
    background:
      radial-gradient(900px 420px at 0% -10%, rgba(245, 158, 11, 0.18), transparent 60%),
      radial-gradient(700px 420px at 100% 0%, rgba(251, 113, 133, 0.12), transparent 55%),
      var(--bg);
  }
  :host([theme="classic"]) {
    color-scheme: light;
    --bg: #f4efe8;
    --text: #2a2118;
    --muted: #6d5e51;
    --faint: #97887a;
    --stroke: rgba(42, 33, 24, 0.1);
    --stroke-strong: rgba(42, 33, 24, 0.16);
    --card: linear-gradient(180deg, #fffdf9, #f7f1e8);
    --rail: rgba(255, 252, 247, 0.94);
    --field: #fff;
    --shadow: 0 14px 30px rgba(42, 33, 24, 0.08);
    background:
      radial-gradient(900px 420px at 0% -10%, rgba(245, 158, 11, 0.2), transparent 60%),
      var(--bg);
  }
  * { box-sizing: border-box; }
  button, input { font: inherit; color: inherit; }
  button { cursor: pointer; }
  .shell { display: flex; height: 100%; }
  .rail {
    width: 220px;
    flex: none;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 22px 14px;
    border-right: 1px solid var(--stroke);
    background: var(--rail);
    backdrop-filter: blur(16px);
  }
  .brand { padding: 4px 10px 16px; }
  .brand b { display: block; font-size: 18px; letter-spacing: -0.03em; }
  .brand span { color: var(--muted); font-size: 12px; }
  .nav-btn, .room-head, .tile, .switch, .text-btn {
    border: 1px solid transparent;
    background: transparent;
    text-align: left;
  }
  .nav-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    border-radius: 12px;
    padding: 10px 12px;
    color: var(--muted);
  }
  .nav-btn[aria-current="page"] { background: rgba(245, 158, 11, 0.14); color: var(--text); }
  .nav-btn svg { width: 18px; height: 18px; flex: none; }
  .main { flex: 1; overflow: auto; padding: 28px 32px 48px; }
  h1 { margin: 0 0 4px; font-size: 28px; letter-spacing: -0.04em; }
  h2 { margin: 18px 0 8px; font-size: 15px; font-weight: 650; }
  .sub { margin: 0 0 18px; color: var(--muted); }
  .banner {
    margin-bottom: 16px;
    padding: 12px 14px;
    border-radius: 14px;
    border: 1px solid rgba(251, 113, 133, 0.4);
    background: rgba(251, 113, 133, 0.12);
  }
  .banner.warn { border-color: rgba(245, 158, 11, 0.45); background: rgba(245, 158, 11, 0.12); }
  .hero, .card {
    border: 1px solid var(--stroke);
    border-radius: 20px;
    background: var(--card);
    box-shadow: var(--shadow);
  }
  .hero { padding: 22px; margin-bottom: 16px; }
  .hero-top { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
  .state { font-size: 34px; letter-spacing: -0.04em; margin: 0; }
  .state.burn { color: var(--accent); }
  .state.fault { color: var(--ember); }
  .meta { color: var(--muted); font-size: 13px; }
  .kpis, .tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(168px, 1fr)); gap: 10px; }
  .tile {
    border-color: var(--stroke);
    border-radius: 16px;
    padding: 12px 14px;
    background: rgba(255, 255, 255, 0.03);
  }
  :host([theme="classic"]) .tile { background: rgba(255, 255, 255, 0.7); }
  .tile b { display: block; font-size: 22px; letter-spacing: -0.03em; font-weight: 620; }
  .tile span, .switch span.name { display: block; color: var(--muted); font-size: 12px; }
  .bar { height: 6px; border-radius: 99px; background: rgba(255, 255, 255, 0.08); margin-top: 8px; overflow: hidden; }
  .bar i { display: block; height: 100%; background: var(--accent); }
  .schematic { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 16px 0; }
  .node { padding: 14px; border-radius: 16px; border: 1px solid var(--stroke); min-height: 112px; }
  .node.kessel { background: rgba(245, 158, 11, 0.1); }
  .node.puffer { background: rgba(196, 181, 253, 0.1); }
  .node.kreis { background: rgba(251, 113, 133, 0.08); }
  .node.wasser { background: rgba(103, 232, 249, 0.08); }
  .node strong { display: block; margin-bottom: 8px; }
  .node p { margin: 2px 0; font-size: 13px; color: var(--muted); }
  .node p b { color: var(--text); font-weight: 600; }
  .node.burn { box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.7); }
  .controls { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 18px; }
  .switch, .text-btn {
    border-color: var(--stroke-strong);
    border-radius: 999px;
    padding: 8px 12px;
    background: var(--field);
  }
  .switch[aria-pressed="true"] { border-color: rgba(245, 158, 11, 0.8); background: rgba(245, 158, 11, 0.16); }
  .room { margin-bottom: 12px; }
  .room-head {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 12px 4px;
    border-bottom: 1px solid var(--stroke);
  }
  .room-head span { color: var(--faint); }
  .search {
    width: min(420px, 100%);
    margin-bottom: 14px;
    border-radius: 12px;
    border: 1px solid var(--stroke-strong);
    background: var(--field);
    padding: 10px 12px;
  }
  .details { margin-top: 8px; }
  .details summary { color: var(--muted); cursor: pointer; }
  .sheet, .dialog {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: flex-end;
    justify-content: center;
    z-index: 20;
  }
  .sheet article, .dialog article {
    width: min(760px, 100%);
    background: var(--rail);
    border-radius: 20px 20px 0 0;
    padding: 18px 18px 28px;
    border: 1px solid var(--stroke);
  }
  .dialog { align-items: center; }
  .dialog article { width: min(420px, calc(100% - 32px)); border-radius: 20px; }
  svg.chart { width: 100%; height: 220px; }
  .bottom { display: none; }
  @media (max-width: 960px) {
    .rail { display: none; }
    .main { padding: 18px 16px 96px; }
    .schematic { grid-template-columns: 1fr 1fr; }
    .bottom {
      display: flex;
      position: fixed;
      left: 0; right: 0; bottom: 0;
      gap: 2px;
      padding: 6px 6px calc(8px + env(safe-area-inset-bottom));
      background: var(--rail);
      border-top: 1px solid var(--stroke);
      z-index: 10;
    }
    .bottom button {
      flex: 1;
      border: 0;
      background: transparent;
      color: var(--faint);
      font-size: 10px;
      padding: 6px 0;
    }
    .bottom button[aria-current="page"] { color: var(--accent); }
  }
`;
