/* utils.js — formatadores e constantes compartilhadas entre modulos.
 * Exposto como window.GO40 (namespace global; mantem vanilla sem ES modules).
 */

(function (root) {
  "use strict";

  const ANO_MIN = 1985;
  const ANO_MAX = 2024;
  const TOTAL_ANOS = ANO_MAX - ANO_MIN;

  const fmtPct = v => (v == null ? "—" : (v * 100).toFixed(1).replace(".", ",") + "%");
  const fmtPctBar = v => (v * 100).toFixed(1).replace(".", ",") + "%";
  const fmtPp = v => {
    if (v == null) return "";
    return Math.abs(v).toFixed(1).replace(".", ",") + " pp";
  };
  const fmtNum = (v, d = 0) => {
    if (v == null) return "—";
    return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: d }).format(v);
  };
  const fmtBilhao = v => v == null ? "—" : "R$ " + (v / 1e9).toFixed(1).replace(".", ",") + " bi";
  const fmtMilhao = v => v == null ? "—" : (v / 1e6).toFixed(2).replace(".", ",") + " Mha";

  const yearToPct = ano => ((ano - ANO_MIN) / TOTAL_ANOS) * 100;
  const clampAno = a => Math.max(ANO_MIN, Math.min(ANO_MAX, a));

  // Atos territoriais — definicao canonica (espelha index.html).
  // Cada ato delimita uma faixa contigua de anos (inclusivo).
  const ATOS = [
    { id: "heranca",        titulo: "I. Pastagem como herança",   anoInicio: 1985, anoFim: 1993, cor: "#8b3a1d" },
    { id: "soja-sudoeste",  titulo: "II. Soja no sudoeste",        anoInicio: 1994, anoFim: 2002, cor: "#a85234" },
    { id: "boom-commodity", titulo: "III. Boom de commodities",    anoInicio: 2003, anoFim: 2011, cor: "#c97052" },
    { id: "intensificacao", titulo: "IV. Código Florestal",        anoInicio: 2012, anoFim: 2017, cor: "#5c8a6f" },
    { id: "reorganizacao",  titulo: "V. Reorganização",            anoInicio: 2018, anoFim: 2024, cor: "#2d5a3d" }
  ];

  function eraDoAno(ano) {
    return ATOS.find(a => ano >= a.anoInicio && ano <= a.anoFim) || null;
  }

  // Anos-marco (politicos) — usado para destacar miniaturas no Atlas.
  const ANOS_MARCO = new Set([1985, 1994, 1996, 2002, 2003, 2012, 2018, 2024]);

  // Pinos-dado (inicio sistematico de algum dado) — visualmente distintos.
  const ANOS_DADO = [
    { ano: 2013, rotulo: "SICOR sistemático" },
    { ano: 2017, rotulo: "Censo Agropecuário" },
    { ano: 2020, rotulo: "Pandemia" }
  ];

  // Variaveis do Atlas — espelha o toggle de toolbar.
  const VARIAVEIS_ATLAS = [
    { id: "lulc",        rotulo: "LULC",          n: 40, prontoMVP: true,  pasta: "img/mapas_gee",   prefixo: "cobertura_",  ext: "webp" },
    { id: "fogo",        rotulo: "Fogo",          n: 40, prontoMVP: true,  pasta: "img/mapas_fogo",  prefixo: "fogo_",       ext: "webp" },
    { id: "transicoes",  rotulo: "Transições",    n: 5,  prontoMVP: true,  pasta: "img/mapas_transicoes", prefixo: "transicao_", ext: "webp" },
    { id: "delta",       rotulo: "Δ vs. 1985",    n: 40, prontoMVP: true,  pasta: "img/mapas_delta", prefixo: "delta_",      ext: "webp" }
  ];

  // -------------------- delta inline --------------------
  // direcao "boa": para 'veg' subir = bom (verde); para 'pasto'/'soja' subir = expansao (terracota).
  function classeDelta(cls, dpp) {
    if (Math.abs(dpp) < 0.05) return "delta--flat";
    const subindo = dpp > 0;
    if (cls === "veg") return subindo ? "delta--up-good" : "delta--down-bad";
    return subindo ? "delta--up-bad" : "delta--down-good";
  }

  function formatDelta(curr, prev, cls) {
    if (curr == null || prev == null) return "";
    const dpp = (curr - prev) * 100;
    const klass = classeDelta(cls, dpp);
    if (klass === "delta--flat") {
      return `<span class="delta delta--flat">~ 0,0 pp</span>`;
    }
    const seta = dpp > 0 ? "▲" : "▼";
    return `<span class="delta ${klass}">${seta} ${fmtPp(dpp)}</span>`;
  }

  root.GO40 = root.GO40 || {};
  Object.assign(root.GO40, {
    ANO_MIN, ANO_MAX, TOTAL_ANOS,
    ATOS, ANOS_MARCO, ANOS_DADO, VARIAVEIS_ATLAS,
    fmt: { pct: fmtPct, pctBar: fmtPctBar, pp: fmtPp, num: fmtNum, bilhao: fmtBilhao, milhao: fmtMilhao },
    yearToPct, clampAno, eraDoAno,
    classeDelta, formatDelta
  });

})(typeof window !== "undefined" ? window : this);
