/* inventario.js — Vitrine do painel (§ 3).
 * Le painel_goias.json e injeta cards tematicos com mini-sparkline,
 * valores extremos, cobertura temporal e fonte por serie.
 */
(function (root) {
  "use strict";

  const fmtNum = (v, d = 0) =>
    new Intl.NumberFormat("pt-BR", {
      minimumFractionDigits: d,
      maximumFractionDigits: d
    }).format(v);

  // Formatadores de unidade (cada um aceita o valor bruto do painel).
  const fmtMha    = v => v == null ? "—" : fmtNum(v / 1e6, 2) + " Mha";
  const fmtKha    = v => v == null ? "—" : fmtNum(v / 1e3, 0) + " kha";
  const fmtMt     = v => v == null ? "—" : fmtNum(v / 1e6, 2) + " Mt";
  const fmtKt     = v => v == null ? "—" : fmtNum(v / 1e3, 0) + " kt";
  const fmtMcab   = v => v == null ? "—" : fmtNum(v / 1e6, 2) + " M cab";
  const fmtMhab   = v => v == null ? "—" : fmtNum(v / 1e6, 2) + " Mi hab";
  const fmtUA     = v => v == null ? "—" : fmtNum(v, 2) + " UA/ha";
  const fmtBiRs   = v => v == null ? "—" : "R$ " + fmtNum(v / 1e9, 1) + " bi";
  const fmtBiL    = v => v == null ? "—" : fmtNum(v / 1e6, 2) + " Bi L";  // mil_litros → Bi L
  const fmtMhaPlt = v => v == null ? "—" : fmtNum(v / 1e6, 2) + " Mha";   // ha_plantada → Mha

  // Manifest dos temas e series. Cobertura é texto livre (a logica abaixo
  // verifica a janela real de valores nao-nulos e exibe os extremos).
  const TEMAS = [
    {
      id: "lulc",
      rotulo: "Uso e cobertura da terra · MapBiomas",
      series: [
        { campo: "lulc_vegetacao_nativa_ha", nome: "Vegetação natural",          format: fmtMha, fonte: "MapBiomas Coleção 10.1 (Pipeline #11)" },
        { campo: "lulc_pastagem_ha",          nome: "Pastagem",                   format: fmtMha, fonte: "MapBiomas Coleção 10.1 (Pipeline #11)" },
        { campo: "lulc_agricultura_ha",       nome: "Agricultura (toda lavoura)", format: fmtMha, fonte: "MapBiomas Coleção 10.1 (Pipeline #11)" },
        { campo: "lulc_soja_ha",              nome: "Soja (cobertura no mapa)",   format: fmtMha, fonte: "MapBiomas Coleção 10.1 (Pipeline #11)" },
        { campo: "lulc_corpo_dagua_ha",       nome: "Água",                       format: fmtKha, fonte: "MapBiomas Coleção 10.1 (Pipeline #11)" },
        { campo: "lulc_area_urbana_ha",       nome: "Área urbana",                format: fmtKha, fonte: "MapBiomas Coleção 10.1 (Pipeline #11)" },
      ],
    },
    {
      id: "cultivos",
      rotulo: "Cultivos anuais · IBGE/SIDRA-PAM",
      series: [
        { campo: "agri_soja_ton",            nome: "Soja (produção)",         format: fmtMt, fonte: "IBGE/SIDRA-PAM (Pipeline #3)" },
        { campo: "agri_milho_total_ton",     nome: "Milho 1ª + 2ª safra",     format: fmtMt, fonte: "IBGE/SIDRA-PAM (Pipeline #3)" },
        { campo: "agri_cana_ton",            nome: "Cana-de-açúcar (colmo)",  format: fmtMt, fonte: "IBGE/SIDRA-PAM (Pipeline #3)" },
        { campo: "agri_algodao_ton",         nome: "Algodão (caroço)",        format: fmtKt, fonte: "IBGE/SIDRA-PAM (Pipeline #3)" },
        { campo: "agri_sorgo_ton",           nome: "Sorgo",                   format: fmtKt, fonte: "IBGE/SIDRA-PAM (Pipeline #3)" },
        { campo: "agri_arroz_ton",           nome: "Arroz",                   format: fmtKt, fonte: "IBGE/SIDRA-PAM (Pipeline #3)" },
        { campo: "agri_feijao_ton",          nome: "Feijão",                  format: fmtKt, fonte: "IBGE/SIDRA-PAM (Pipeline #3)" },
        { campo: "agri_milho2_ha_plantada",  nome: "Milho safrinha · área plantada", format: fmtMhaPlt, fonte: "IBGE/SIDRA-PAM (Pipeline #15)" },
      ],
    },
    {
      id: "pecuaria",
      rotulo: "Pecuária · IBGE/PPM",
      series: [
        { campo: "pec_bovinos_cab",          nome: "Rebanho bovino",          format: fmtMcab, fonte: "IBGE/PPM (Pipeline #3)" },
        { campo: "lotacao_ua_ha_pasto",      nome: "Lotação bovina",          format: fmtUA, fonte: "Derivada · MapBiomas × IBGE/PPM" },
        { campo: "agri_leite_mil_litros",    nome: "Produção de leite",       format: fmtBiL, fonte: "IBGE/PPM (Pipeline #3)" },
      ],
    },
    {
      id: "macro",
      rotulo: "Macroeconomia · IBGE / IPEAData",
      series: [
        { campo: "pib_uf_real_rs",           nome: "PIB de Goiás (UF, IPEA)",        format: fmtBiRs, fonte: "IBGE Contas Regionais · IPEAData" },
        { campo: "va_agro_uf_real_rs",       nome: "VA agropecuário (UF, IPEA)",     format: fmtBiRs, fonte: "IBGE Contas Regionais · IPEAData" },
        { campo: "pib_real_rs",              nome: "PIB · Σ municípios",             format: fmtBiRs, fonte: "IBGE/SIDRA-5938 (PIB Municipal)" },
        { campo: "va_agro_real_rs",          nome: "VA agropecuário · Σ municípios", format: fmtBiRs, fonte: "IBGE/SIDRA-5938 (PIB Municipal)" },
      ],
    },
    {
      id: "credito",
      rotulo: "Crédito rural · BACEN/SICOR",
      series: [
        { campo: "sicor_total_real_rs",      nome: "Crédito rural total (SICOR)",    format: fmtBiRs, fonte: "BACEN/SICOR (Pipeline #6)" },
      ],
    },
    {
      id: "demo",
      rotulo: "Demografia · IBGE",
      series: [
        { campo: "populacao",                nome: "População de Goiás",             format: fmtMhab, fonte: "IBGE — Estimativas e Censos" },
      ],
    },
    {
      id: "ambiente",
      rotulo: "Ambiente · MapBiomas Fogo",
      series: [
        { campo: "fogo_total_ha",            nome: "Área queimada anual",            format: fmtKha, fonte: "MapBiomas Fogo Coleção 4 (Pipeline #14)" },
      ],
    },
  ];

  // Constroi o caminho SVG da mini-sparkline com area sombreada.
  function makeSparkline(serie, campo) {
    const W = 240, H = 32, padX = 1, padY = 2;
    const dados = serie
      .map(r => ({ ano: r.ano, v: r[campo] }))
      .filter(p => p.v != null && !isNaN(p.v));
    if (dados.length < 2) {
      return `<svg class="inventario-card-sparkline" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true"></svg>`;
    }
    const anos = dados.map(p => p.ano);
    const vals = dados.map(p => p.v);
    const xMin = Math.min(...anos);
    const xMax = Math.max(...anos);
    let yMin = Math.min(...vals);
    let yMax = Math.max(...vals);
    if (yMax === yMin) { yMax = yMin + 1; }
    const xRange = (xMax - xMin) || 1;
    const yRange = (yMax - yMin) || 1;
    const xs = ano => padX + ((ano - xMin) / xRange) * (W - 2 * padX);
    const ys = v   => H - padY - ((v - yMin) / yRange) * (H - 2 * padY);

    const pathLine = dados
      .map((p, i) => `${i === 0 ? "M" : "L"} ${xs(p.ano).toFixed(1)} ${ys(p.v).toFixed(1)}`)
      .join(" ");
    const pathArea = pathLine
      + ` L ${xs(xMax).toFixed(1)} ${(H - padY).toFixed(1)}`
      + ` L ${xs(xMin).toFixed(1)} ${(H - padY).toFixed(1)} Z`;

    return `<svg class="inventario-card-sparkline" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">`
      + `<path class="spark-area" d="${pathArea}"/>`
      + `<path d="${pathLine}"/>`
      + `</svg>`;
  }

  // Calcula janela real de cobertura (primeiro/ultimo ano com valor nao-nulo).
  function janelaCobertura(serie, campo) {
    let primeiro = null, ultimo = null;
    for (const r of serie) {
      if (r[campo] != null && !isNaN(r[campo])) {
        if (primeiro == null) primeiro = r.ano;
        ultimo = r.ano;
      }
    }
    return primeiro == null ? null : { primeiro, ultimo };
  }

  function renderCard(spec, serie, temaId) {
    const dados = serie
      .map(r => ({ ano: r.ano, v: r[spec.campo] }))
      .filter(p => p.v != null && !isNaN(p.v));
    const janela = janelaCobertura(serie, spec.campo);
    const coberturaTxt = janela
      ? `${janela.primeiro}–${janela.ultimo} (anual)`
      : "sem dado disponível";

    if (dados.length === 0) {
      return `
        <div class="inventario-card" data-tema="${temaId}">
          <div class="inventario-card-nome">${spec.nome}</div>
          <div class="inventario-card-valores"><em>(sem dado neste agregado)</em></div>
          <div class="inventario-card-meta">
            <span class="inventario-card-cobertura">${coberturaTxt}</span>
            <span class="inventario-card-fonte">${spec.fonte}</span>
          </div>
        </div>
      `;
    }

    const first = dados[0];
    const last = dados[dados.length - 1];
    const valoresHtml = `<span title="${first.ano}">${spec.format(first.v)}</span>`
      + `<span class="vsep">→</span>`
      + `<span title="${last.ano}">${spec.format(last.v)}</span>`;

    return `
      <div class="inventario-card" data-tema="${temaId}">
        <div class="inventario-card-nome">${spec.nome}</div>
        ${makeSparkline(serie, spec.campo)}
        <div class="inventario-card-valores">${valoresHtml}</div>
        <div class="inventario-card-meta">
          <span class="inventario-card-cobertura">${coberturaTxt}</span>
          <span class="inventario-card-fonte">${spec.fonte}</span>
        </div>
      </div>
    `;
  }

  function renderVitrine(painel) {
    const cont = document.getElementById("inventario-grid");
    if (!cont) return;
    const serie = painel.serie || [];
    const html = TEMAS.map(tema => {
      const cards = tema.series
        .map(spec => renderCard(spec, serie, tema.id))
        .join("");
      return `
        <div class="inventario-tema" data-tema="${tema.id}">
          <h4 class="inventario-tema-rotulo">${tema.rotulo}</h4>
          <div class="inventario-tema-cards">${cards}</div>
        </div>
      `;
    }).join("");
    cont.innerHTML = html;
  }

  async function init() {
    const cont = document.getElementById("inventario-grid");
    if (!cont) return;
    try {
      const painel = await fetch("assets/data/painel_goias.json").then(r => r.json());
      renderVitrine(painel);
    } catch (err) {
      console.error("inventario: falha ao carregar painel", err);
      cont.innerHTML = `<p class="resumo-loading" style="color: var(--color-accent);">Falha ao carregar dados da vitrine: ${err.message}</p>`;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : this);
