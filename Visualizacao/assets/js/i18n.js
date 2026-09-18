/* i18n.js — camada de tradução para a variante em inglês do site (index.en.html).
 *
 * O idioma vem de <html lang>. Em português T() é a identidade, de modo que o
 * site original roda exatamente como antes; em inglês T() consulta o dicionário
 * abaixo e devolve a string traduzida (ou a própria chave, se não houver entrada).
 *
 * TF() é a versão com interpolação: TF("x {0} y", v) procura "x {0} y" no
 * dicionário e substitui os marcadores {0}, {1}, ...
 *
 * Precisa ser carregado ANTES de utils.js.
 */
(function (root) {
  "use strict";

  var lang = String((root.document && root.document.documentElement.lang) || "pt")
               .toLowerCase().indexOf("en") === 0 ? "en" : "pt";

  var DIC = {
    /* ---------------- utils.js: atos e pinos-dado ---------------- */
    "I. Pastagem como herança":              "I. Pasture as inheritance",
    "II. Expansão e intensificação":         "II. Expansion and intensification",
    "III. Conversão acelerada":              "III. Accelerated conversion",
    "SICOR sistemático":                     "SICOR systematic",
    "Censo Agropecuário":                    "Agricultural Census",
    "Pandemia":                              "Pandemic",

    /* ---------------- timeline.js: eras ---------------- */
    "Ato I":                                 "Act I",
    "Ato II":                                "Act II",
    "Ato III":                               "Act III",
    "Pastagem como herança":                 "Pasture as inheritance",
    "Expansão e intensificação":             "Expansion and intensification",
    "Conversão acelerada (mascarada)":       "Accelerated conversion (masked)",
    "pastagem domina e a soja ainda é pontual":
      "pasture dominates and soy is still patchy",
    "soja avança sobre pastagem; intensificação sem fronteira":
      "soy advances over pasture; intensification without a frontier",
    "a pastagem cede três vezes mais rápido; a conversão acelera — e a medida crua esconde":
      "pasture gives way three times faster; conversion accelerates — and the raw measure hides it",

    /* ---------------- timeline.js: marcos e painel ---------------- */
    "crédito público":                       "public credit",
    "regulação ambiental":                   "environmental regulation",
    "Produção agrícola (toneladas)":         "Crop output (tonnes)",
    "Rebanho bovino":                        "Cattle herd",
    "PIB (Σ municípios)":                    "GDP (Σ municipalities)",
    "VA Agro (Σ municípios)":                "Agric. value added (Σ municipalities)",
    "Crédito rural":                         "Rural credit",
    "Contexto: os números abaixo acompanham o marco, não o testam.":
      "Context: the figures below accompany the milestone, they do not test it.",
    "▲▼ em pp vs. {0}":                      "▲▼ in pp vs. {0}",
    "Início da série":                       "Start of the series",
    "Estado atual":                          "Present state",


    /* ---------------- timeline.js: painel anual ---------------- */
    "contexto":                              "context",
    "macroeconomia":                         "macroeconomics",
    "tributação":                            "taxation",
    "mercado":                               "market",
    "Soja":                                  "Soy",
    "Milho":                                 "Maize",
    "Cana":                                  "Sugarcane",
    "Algodão":                               "Cotton",
    "Sorgo":                                 "Sorghum",
    "Arroz":                                 "Rice",
    "Feijão":                                "Beans",
    "Lotação":                               "Stocking rate",
    "Leite":                                 "Milk",
    "Pecuária":                              "Livestock",
    "Socioeconômico":                        "Socioeconomic",
    "PIB (IPEA UF)":                         "GDP (IPEA state)",
    "VA Agro (IPEA UF)":                     "Agric. VA (IPEA state)",
    "linha de base":                         "baseline",
    "sem dado neste ano":                    "no data for this year",
    "desde 2013":                            "since 2013",
    "desde 2001":                            "since 2001",
    "SIDRA 5938, 2002+":                     "SIDRA 5938, 2002+",
    "IBGE Contas Reg., 1985+":               "IBGE Regional Accounts, 1985+",
    "Fonte: MapBiomas Col. 10.1 · Pipeline #25":
      "Source: MapBiomas Col. 10.1 · Pipeline #25",
    "Falha ao carregar dados: {0}. ":        "Failed to load data: {0}. ",
    " M cab":                                " M head",
    " cab/ha":                               " head/ha",
    " Mi L":                                 " M L",
    " Mi":                                   " M",
    " Mt":                                   " Mt",
    " mil t":                                " thousand t",

    /* ---------------- classes de uso da terra ---------------- */
    "Vegetação natural":                     "Natural vegetation",
    "Vegetação Natural":                     "Natural vegetation",
    "Veg. natural":                          "Nat. vegetation",
    "Pastagem":                              "Pasture",
    "Agricultura":                           "Agriculture",
    "Mosaico de usos":                       "Mosaic of uses",
    "Mosaico de Usos":                       "Mosaic of Uses",
    "Mosaico":                               "Mosaic",
    "Área urbana":                           "Urban area",
    "Área Urbana":                           "Urban area",
    "Água":                                  "Water",
    "Urbano":                                "Urban",
    "Urb.":                                  "Urb.",
    "Veg.":                                  "Veg.",
    "Exibir normal":                         "Show normally",
    "Esmaecer (Marcha)":                     "Fade (March)",
    "Ocultar (Filtrar)":                     "Hide (Filter)",
    "Normal":                                "Normal",
    "Esmaecer":                              "Fade",
    "Ocultar":                               "Hide",
    "Outros":                                "Other",

    /* ---------------- timeline.js: legendas do mapa ---------------- */
    "destino dominante no período":          "dominant destination in the period",
    "acumulado desde 1985: veg {0} · pasto {1}":
      "cumulative since 1985: veg {0} · pasture {1}",
    "Transição dominante por município em Goiás entre {0} e {1}":
      "Dominant transition by municipality in Goiás between {0} and {1}",
    "Cobertura e uso da terra em Goiás em {0}":
      "Land cover and land use in Goiás in {0}",
    "Fonte: MapBiomas Coleção 10.1 &middot; pixel-a-pixel (30&nbsp;m) &middot; o mapa é reduzido para caber na tela, então classes fragmentadas encolhem no desenho: a medida está na barra acima":
      "Source: MapBiomas Collection 10.1 &middot; pixel-by-pixel (30&nbsp;m) &middot; the map is scaled down to fit the screen, so fragmented classes shrink in the drawing: the measurement is in the bar above",
    "Fonte: MapBiomas Coleção 10.1 &middot; agregado <strong>por município</strong>, não por pixel &middot; a partir de 2015 o destino dominante na maior parte do estado é o <em>Mosaico de usos</em>, o que é mudança de rótulo tanto quanto de uso (<a href=\"dossie-mosaico.html\">a investigação</a>)":
      "Source: MapBiomas Collection 10.1 &middot; aggregated <strong>by municipality</strong>, not by pixel &middot; from 2015 onwards the dominant destination across most of the state is the <em>Mosaic of uses</em>, which is a change of label as much as of use (<a href=\"dossie-mosaico.html\">the investigation</a>)",

    /* ---------------- timeline.js: mini-sankeys por ato ---------------- */
    "Para onde foram os hectares entre 1985 e 2000: cruzamento pixel-a-pixel das transições deste período.":
      "Where the hectares went between 1985 and 2000: pixel-by-pixel crossing of this period's transitions.",
    "Para onde foram os hectares entre 2001 e 2019: o período da grande expansão agrícola sobre a pastagem.":
      "Where the hectares went between 2001 and 2019: the period of the great agricultural expansion over pasture.",
    "Para onde foram os hectares entre 2020 e 2024: a conversão acelera sobre a pastagem — e o mapa, sozinho, diz o contrário.":
      "Where the hectares went between 2020 and 2024: conversion accelerates over pasture — and the map, on its own, says the opposite.",
    "Fluxos do Ato {0}":                     "Flows of Act {0}",
    "Sankey de transições do Ato {0}":       "Sankey of Act {0} transitions",
    "Se voce abriu via duplo-clique, use o servir.bat ou servir.ps1.":
      "If you opened this by double-clicking, use servir.bat or servir.ps1 instead.",

    /* ---------------- sankey.js / mini-sankey.js ---------------- */
    "Diagrama de Sankey: transições de uso da terra 1985-2024":
      "Sankey diagram: land-use transitions 1985-2024",
    "Modo de exibição do Mosaico de Usos":   "Display mode for the Mosaic of Uses",
    "Carregando diagrama…":                  "Loading diagram…",

    /* ---------------- matriz.js ---------------- */
    "as células fora da diagonal mostram para onde a área foi convertida. O Mosaico de Usos (lavoura ou pasto, que o classificador não separa) entra como classe própria.":
      "the off-diagonal cells show where the area was converted to. The Mosaic of Uses (cropland or pasture, which the classifier does not separate) enters as a class of its own.",
    "Valores em milhões de hectares (Mha). Na diagonal, os pixels que permaneceram na mesma classe; fora dela, as transições. O Mosaico de Usos (lavoura ou pasto, que o classificador não separa) entra como classe própria.":
      "Values in millions of hectares (Mha). On the diagonal, the pixels that stayed in the same class; off it, the transitions. The Mosaic of Uses (cropland or pasture, which the classifier does not separate) enters as a class of its own.",
    "Origem ↓ / Destino →":                  "Origin ↓ / Destination →",
    "Fonte: MapBiomas Coleção 10.1 (Pipeline #12B).":
      "Source: MapBiomas Collection 10.1 (Pipeline #12B).",

    /* ---------------- marcha-mapa.js ---------------- */
    "Ato":                                   "Act",
    " · Ato {0} ({1})":                      " · Act {0} ({1})",
    "— a agricultura está <strong>~{0} km ao sul</strong> de pasto/rebanho. Arraste a faixa ou o controle para percorrer os 40 anos.":
      "— agriculture is <strong>~{0} km south</strong> of pasture/herd. Drag the slider or the control to move through the 40 years.",
    "<em>(≈ ancorada)</em>":                 "<em>(≈ anchored)</em>",
    "A partir de {0} a linha da agricultura fica <b>pontilhada</b>: dali em diante o satélite roteia a conversão recente para a classe \"Mosaico de Usos\", e o centroide da agricultura passa a subcontá-la. O achatamento é do rótulo, não do campo.":
      "From {0} onwards the agriculture line becomes <b>dotted</b>: from that point the satellite routes recent conversion into the \"Mosaic of Uses\" class, and the agriculture centroid starts undercounting it. The flattening belongs to the label, not to the field.",
    "Reproduzir":                            "Play",
    "Pausar":                                "Pause",

    /* ---------------- reserva-perna2.js ---------------- */
    "Goiás (estado)":                        "Goiás (state)",
    "Goiás inteiro":                         "All of Goiás",
    "Ver a distribuição de {0}":             "See the distribution for {0}",
    "{0} conversões de idade conhecida<br>":  "{0} conversions of known age<br>",
    "{0} de {1} AMCs bimodais por dentro<br>": "{0} of {1} AMCs bimodal internally<br>",
    "<em>clique para ver a distribuição</em>": "<em>click to see the distribution</em>",
    "as duas populações convivem ali dentro ({0} de {1})":
      "the two populations coexist inside it ({0} of {1})",
    "uma população só ({0})":                "a single population ({0})",
    "poucas conversões para ajustar ({0})":  "too few conversions to fit ({0})",
    "pasto de ciclo curto · {0} das conversões":
      "short-cycle pasture · {0} of conversions",
    "pasto antigo · {0}":                    "old pasture · {0}",
    "o que uma população só produziria":     "what a single population would produce",
    "Aqui o histograma tem <strong>vale visível</strong> — desce e volta a subir por volta dos {0} anos (profundidade {1}%).":
      "Here the histogram has a <strong>visible trough</strong> — it dips and rises again at around {0} years (depth {1}%).",
    "Aqui não há vale visível: as duas populações se somam num pico e um ombro.":
      "Here there is no visible trough: the two populations add up to a peak and a shoulder.",
    ", e o coeficiente de Sarle — que não usa ajuste nenhum — dá ":
      ", and Sarle's coefficient — which uses no fit at all — gives ",
    "O ajuste separa modos em <strong>{0}a</strong> e <strong>{1}a</strong>":
      "The fit separates modes at <strong>{0}y</strong> and <strong>{1}y</strong>",
    ", e o coeficiente de Sarle — que não usa ajuste nenhum — dá <strong>{0}</strong>, acima do limiar de 0,555":
      ", and Sarle's coefficient — which uses no fit at all — gives <strong>{0}</strong>, above the 0.555 threshold",
    "O ajuste não separa duas populações aqui.":
      "The fit does not separate two populations here.",
    "{0} conversões de idade conhecida; outras {1} ({2}) já eram pastagem em 1985, têm a idade truncada e ficam de fora.":
      "{0} conversions of known age; another {1} ({2}) were already pasture in 1985, have truncated ages and are left out.",
    "O censo cobre <strong>{0} municípios</strong>, e mesmo o menor deles tem <strong>{1}</strong> conversões de idade conhecida — não há aqui nenhum recorte medido no fio do ruído.":
      "The census covers <strong>{0} municipalities</strong>, and even the smallest of them has <strong>{1}</strong> conversions of known age — no cut here is measured on the edge of noise.",

    /* ---------------- inventario.js ---------------- */
    "Uso e cobertura da terra":              "Land use and land cover",
    "MapBiomas Coleção 10.1 (Pipeline #11)": "MapBiomas Collection 10.1 (Pipeline #11)",
    "Agricultura (toda lavoura)":            "Agriculture (all cropland)",
    "Soja (cobertura no mapa)":              "Soy (cover on the map)",
    "Produção agrícola · IBGE/PAM":          "Crop output · IBGE/PAM",
    "Soja (produção)":                       "Soy (output)",
    "Cana-de-açúcar (colmo)":                "Sugarcane (stalk)",
    "Algodão (caroço)":                      "Cotton (seed)",
    "Milho safrinha · área plantada":        "Second-crop maize · planted area",
    "Pecuária · IBGE/PPM":                   "Livestock · IBGE/PPM",
    "Lotação bovina":                        "Cattle stocking rate",
    "Produção de leite":                     "Milk output",
    "Economia · IPEA":                       "Economy · IPEA",
    "PIB de Goiás (UF, IPEA)":               "GDP of Goiás (state, IPEA)",
    "VA agropecuário (UF, IPEA)":            "Agricultural value added (state, IPEA)",
    "PIB · Σ municípios":                    "GDP · Σ municipalities",
    "VA agropecuário · Σ municípios":        "Agricultural value added · Σ municipalities",
    "Crédito rural · BACEN/SICOR":           "Rural credit · BACEN/SICOR",
    "Crédito rural total (SICOR)":           "Total rural credit (SICOR)",
    "População":                             "Population",
    "População de Goiás":                    "Population of Goiás",
    "Fogo":                                  "Fire",
    "Área queimada anual":                   "Annual burned area",
    "MapBiomas Fogo Coleção 4 (Pipeline #14)": "MapBiomas Fogo Collection 4 (Pipeline #14)",
    "sem dado disponível":                   "no data available",
    "(sem dado neste agregado)":             "(no data in this aggregate)",
    "Carregando vitrine do painel…":         "Loading panel showcase…",


    /* ---------------- inventario.js: temas, séries e fontes ---------------- */
    "Uso e cobertura da terra · MapBiomas":  "Land use and land cover · MapBiomas",
    "Cultivos anuais · IBGE/SIDRA-PAM":      "Annual crops · IBGE/SIDRA-PAM",
    "Macroeconomia · IBGE / IPEAData":       "Macroeconomics · IBGE / IPEAData",
    "Demografia · IBGE":                     "Demographics · IBGE",
    "Ambiente · MapBiomas Fogo":             "Environment · MapBiomas Fogo",
    "Milho 1ª + 2ª safra":                   "Maize, 1st + 2nd crop",
    "Derivada · MapBiomas × IBGE/PPM":       "Derived · MapBiomas × IBGE/PPM",
    "IBGE Contas Regionais · IPEAData":      "IBGE Regional Accounts · IPEAData",
    "IBGE/SIDRA-5938 (PIB Municipal)":       "IBGE/SIDRA-5938 (Municipal GDP)",
    "IBGE — Estimativas e Censos":           "IBGE — Estimates and Censuses",
    "{0}–{1} (anual)":                       "{0}–{1} (annual)",
    " M cab.":                               " M head",
    " Mi hab":                               " M inhab.",
    " Bi L":                                 " Bn L",

    /* ---------------- pipeline-modal.js ---------------- */
    "Carregando…":                           "Loading…",
    "Não foi possível buscar o arquivo (":   "Could not fetch the file (",
    "Cada linha soma 100%. A diagonal mostra a porcentagem que permaneceu na mesma classe; ":
      "Each row sums to 100%. The diagonal shows the percentage that stayed in the same class; ",
    "ver no GitHub &#8599;":                 "view on GitHub &#8599;",
    "Abrir no GitHub &#8599;":               "Open on GitHub &#8599;",
    "Fechar":                                "Close"
  };

  function T(s) {
    if (lang !== "en" || s == null) return s;
    var k = String(s);
    return Object.prototype.hasOwnProperty.call(DIC, k) ? DIC[k] : k;
  }

  /* TF("texto {0}", v) — traduz o molde e depois interpola. */
  function TF(s) {
    var args = Array.prototype.slice.call(arguments, 1);
    var out = T(s);
    for (var i = 0; i < args.length; i++) {
      out = out.split("{" + i + "}").join(String(args[i]));
    }
    return out;
  }

  /* Separador decimal e locale numérico, para os formatadores de utils.js. */
  var NUM = {
    decimal: lang === "en" ? "." : ",",
    locale:  lang === "en" ? "en-US" : "pt-BR",
    bilhao:  lang === "en" ? " bn" : " bi"
  };

  root.GO40I18N = { lang: lang, T: T, TF: TF, num: NUM, dict: DIC };
  root.T = T;
  root.TF = TF;

})(typeof window !== "undefined" ? window : this);
