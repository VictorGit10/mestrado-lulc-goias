"""Gera as figuras SVG-inline da Perna 4 da reforma a partir dos CSVs reais.

Por que um script e nao SVG escrito a mao: rotulo de figura e' afirmacao e
envelhece (D27). Aqui cada coordenada sai do CSV, e o `--auditar` reimprime todo
numero que aparece na tela ao lado da sua fonte — da' para reconferir sem abrir o
Inkscape e sem confiar na memoria de quem desenhou.

FIGURAS
  fig1  "A protecao nao estava no caminho"   (#46 blocos A/B/C + #39)
        painel A: protecao acumulada (PI/US) x conversao acumulada — mesmo eixo, Mha
        painel B: Cerrado exposto por regiao, com a fatia sob PI (regua pixel)
  fig2  "Emissao = area x densidade"          (#47) retangulos area-verdadeiros
  fig3  "Quando e onde se pagou"              (#47) Mt/ano por regiao x ato + centroide
  fig4  "O que a area comprou"                (#51) serie IFDM 2013-23 por regiao

ENTRADAS  (todas em data/processed/)
    protecao_temporal.csv, protecao_uc_amc.csv, protecao_gap_regional.csv,
    protecao_gap_pixel_regiao.csv, fronteira_regional.csv,
    fronteira_estoque_convertivel.csv, carbono_por_formacao.csv,
    carbono_regional_ato.csv, carbono_centroide_ato.csv,
    ifdm_goias_municipal.csv, mapeamento_mesorregioes.csv,
    desenvolvimento_gradiente.csv, painel_unificado.parquet

SAIDA
    Visualizacao/scratch/figuras_perna4.html  (fragmento, para conferir isolado)
    Visualizacao/reforma.html                 (com --aplicar, entre os marcadores
                                               <!-- fig-perna4:N -->; idempotente)

COMO RODAR
    py -3.14 Visualizacao/scripts/gerar_figuras_perna4.py
    py -3.14 Visualizacao/scripts/gerar_figuras_perna4.py --auditar
    py -3.14 Visualizacao/scripts/gerar_figuras_perna4.py --aplicar   (escreve no HTML)

Cor: reaproveita a convencao da figura do estoque logo acima na pagina (Sul =
terracota, Centro = cinza, Norte = verde). O par verde/cinza fica abaixo do piso
de separacao para visao normal e o par verde/terracota e' fraco sob deuteranopia,
entao NENHUMA figura daqui usa cor como canal unico de identidade: toda marca
regional leva rotulo direto, e posicao (linha/faixa) repete a identidade.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
SAIDA = ROOT / "Visualizacao" / "scratch" / "figuras_perna4.html"
HTML = ROOT / "Visualizacao" / "reforma.html"

AUDIT: list[tuple[str, str, str]] = []   # (figura, numero na tela, fonte)


def anota(fig: str, valor: str, fonte: str) -> str:
    AUDIT.append((fig, valor, fonte))
    return valor


# --------------------------------------------------------------------------
# helpers de escala / formatacao
# --------------------------------------------------------------------------
class Escala:
    def __init__(self, d0: float, d1: float, r0: float, r1: float):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v: float) -> float:
        t = (v - self.d0) / (self.d1 - self.d0)
        return round(self.r0 + t * (self.r1 - self.r0), 1)


def br(v: float, casas: int = 1) -> str:
    """Numero no formato pt-BR (virgula decimal, ponto de milhar).

    Arredonda meio-para-cima: o padrao do Python e' meio-para-par, e 76,5 viraria
    "76" — um numero na tela que erra o CSV pelo lado errado.
    """
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(str(v)).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    s = f"{q:,.{casas}f}".replace("-", "&minus;")
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def poly(pts: list[tuple[float, float]]) -> str:
    return " ".join(f"{x},{y}" for x, y in pts)


# --------------------------------------------------------------------------
# FIGURA 1 — a protecao nao estava no caminho
# --------------------------------------------------------------------------
def figura1() -> str:
    prot = pd.read_csv(PROC / "protecao_temporal.csv")
    piv = prot.pivot(index="ano", columns="grupo", values="ha_acumulado") / 1e6

    reg = pd.read_csv(PROC / "fronteira_regional.csv")
    est = (reg[reg.agrupamento == "mesorregiao"]
           .groupby("ano")["estoque_refinada_mha"].sum())
    conv = est.loc[1985] - est          # convertido acumulado desde 1985

    anos = list(range(1985, 2025))
    sx = Escala(1985, 2024, 62, 452)
    sy = Escala(0, 4.4, 262, 40)

    l_conv = poly([(sx(a), sy(conv.loc[a])) for a in anos])
    l_pi = poly([(sx(a), sy(piv.loc[a, "PI"])) for a in anos])
    l_us = poly([(sx(a), sy(piv.loc[a, "US"])) for a in anos])
    area_conv = (f"{sx(1985)},{sy(0)} " + l_conv + f" {sx(2024)},{sy(0)}")

    c24 = anota("fig1A", br(conv.loc[2024], 2), "fronteira_regional: estoque 1985-2024")
    pi24 = anota("fig1A", br(piv.loc[2024, "PI"], 2), "protecao_temporal PI acum. 2024")
    us24 = anota("fig1A", br(piv.loc[2024, "US"], 2), "protecao_temporal US acum. 2024")
    pi85 = anota("fig1A", br(100 * piv.loc[1985, "PI"] / piv.loc[2024, "PI"], 0),
                 "% da PI de 2024 que ja existia em 1985")
    d_pi = anota("fig1A", br(piv.loc[2024, "PI"] - piv.loc[1985, "PI"], 2),
                 "PI criada 1985->2024")

    grade = "".join(
        f'<line class="p4-grade" x1="62" y1="{sy(v)}" x2="452" y2="{sy(v)}"></line>'
        f'<text class="p4-escala" x="54" y="{sy(v) + 4}" text-anchor="end">{br(v, 0)}</text>'
        for v in [0, 1, 2, 3, 4])
    atos = "".join(
        f'<line class="p4-ato" x1="{sx(a)}" y1="40" x2="{sx(a)}" y2="262"></line>'
        f'<text class="p4-ato-rot" x="{sx(a) + 4}" y="52">{rot}</text>'
        for a, rot in [(2001, "Ato II"), (2020, "Ato III")])

    painel_a = f"""
        <svg viewBox="0 0 620 300" role="img"
             aria-label="Entre 1985 e 2024 Goias converteu {c24} milhoes de hectares de
             Cerrado convertivel, enquanto o estoque de Protecao Integral do estado saiu de
             0,38 para {pi24} milhao de hectares. A protecao de Uso Sustentavel, que admite uso
             rural, salta para {us24} milhoes de hectares nos anos 2000, depois da maior parte
             da conversao ja ter acontecido.">
          <text class="p4-eixo-titulo" x="62" y="22">milhões de hectares (Mha)</text>
          {grade}
          {atos}
          <polygon class="p4-area-conv" points="{area_conv}"></polygon>
          <polyline class="p4-linha p4-linha--conv" points="{l_conv}"></polyline>
          <polyline class="p4-linha p4-linha--us" points="{l_us}"></polyline>
          <polyline class="p4-linha p4-linha--pi" points="{l_pi}"></polyline>

          <text class="p4-rot p4-rot--conv" x="460" y="{sy(conv.loc[2024])}">Cerrado convertido</text>
          <text class="p4-rot p4-rot--conv p4-rot--val" x="460" y="{sy(conv.loc[2024]) + 15}">{c24} Mha</text>
          <text class="p4-rot p4-rot--us" x="460" y="{sy(piv.loc[2024, 'US'])}">Uso Sustentável</text>
          <text class="p4-rot p4-rot--us p4-rot--val" x="460" y="{sy(piv.loc[2024, 'US']) + 15}">{us24} Mha</text>
          <text class="p4-rot p4-rot--pi" x="460" y="{sy(piv.loc[2024, 'PI']) + 10}">Proteção Integral</text>
          <text class="p4-rot p4-rot--pi p4-rot--val" x="460" y="{sy(piv.loc[2024, 'PI']) + 25}">{pi24} Mha</text>

          <line class="p4-eixo" x1="62" y1="262" x2="452" y2="262"></line>
          <text class="p4-escala" x="62" y="278" text-anchor="middle">1985</text>
          <text class="p4-escala" x="{sx(2000)}" y="278" text-anchor="middle">2000</text>
          <text class="p4-escala" x="{sx(2012)}" y="278" text-anchor="middle">2012</text>
          <text class="p4-escala" x="452" y="278" text-anchor="middle">2024</text>
        </svg>"""

    # ---- painel B: onde esta' o Cerrado exposto, e quanto dele a lei veda ----
    # Versao anterior desenhava as 166 AMC como espinhos ao longo da latitude:
    # honesto, ilegivel. Tres barras respondem a mesma pergunta sem cobrar
    # decodificacao do leitor. Regua PIXEL (a mais exigente das duas do #46).
    px = pd.read_csv(PROC / "protecao_gap_pixel_regiao.csv").set_index("regiao")
    fora = anota("fig1B", br(px.loc["ESTADO", "pct_desprot_pixel"], 1),
                 "protecao_gap_pixel_regiao ESTADO")

    bx = Escala(0, 3.0, 132, 528)
    linhas_y = {"Norte": 70, "Centro": 116, "Sul": 162}
    barras = []
    for reg_, y in linhas_y.items():
        tot_r = float(px.loc[reg_, "conv_px_Mha"])
        prot_r = float(px.loc[reg_, "conv_pi_px_Mha"])
        pct_f = float(px.loc[reg_, "pct_desprot_pixel"])
        anota("fig1B", br(tot_r, 2), f"Cerrado exposto {reg_} (Mha, pixel)")
        anota("fig1B", br(pct_f, 0) + "%", f"% fora da protecao integral, {reg_}")
        x_prot = bx(prot_r)
        barras.append(
            f'<text class="p4-bar-rot" x="124" y="{y + 5}" text-anchor="end">{reg_}</text>'
            f'<rect class="p4-seg p4-seg--prot" x="{bx(0)}" y="{y - 11}" '
            f'width="{max(round(x_prot - bx(0), 1), 2)}" height="22"></rect>'
            f'<rect class="p4-seg p4-seg--expo" x="{round(x_prot + 1.5, 1)}" y="{y - 11}" '
            f'width="{round(bx(tot_r) - x_prot - 1.5, 1)}" height="22"></rect>'
            f'<text class="p4-bar-val" x="{round(bx(tot_r) + 8, 1)}" y="{y + 5}">'
            f'{br(pct_f, 0)}% fora</text>')

    grade_b = "".join(
        f'<line class="p4-grade" x1="{bx(v)}" y1="44" x2="{bx(v)}" y2="186"></line>'
        f'<text class="p4-escala" x="{bx(v)}" y="202" text-anchor="middle">{br(v, 0)}</text>'
        for v in [1, 2, 3])

    painel_b = f"""
        <svg viewBox="0 0 620 224" role="img"
             aria-label="Tres barras, uma por regiao. O Norte tem
             {br(px.loc['Norte', 'conv_px_Mha'], 2)} milhoes de hectares de Cerrado ainda exposto a
             conversao e {br(px.loc['Norte', 'pct_desprot_pixel'], 0)} por cento deles estao fora de
             Protecao Integral; no Centro sao {br(px.loc['Centro', 'pct_desprot_pixel'], 0)} por cento e
             no Sul {br(px.loc['Sul', 'pct_desprot_pixel'], 0)} por cento. A parte protegida e' uma
             fatia fina no comeco de cada barra.">
          <g class="p4-legenda-svg">
            <rect class="p4-seg p4-seg--prot" x="132" y="16" width="11" height="11"></rect>
            <text class="p4-legenda-rot" x="149" y="26">sob Proteção Integral</text>
            <rect class="p4-seg p4-seg--expo" x="292" y="16" width="11" height="11"></rect>
            <text class="p4-legenda-rot" x="309" y="26">exposto à conversão</text>
          </g>
          {grade_b}
          {''.join(barras)}
          <line class="p4-eixo" x1="{bx(0)}" y1="186" x2="{bx(3.0)}" y2="186"></line>
          <text class="p4-eixo-titulo" x="{bx(0)}" y="220">milhões de hectares de Cerrado que resta (2024)</text>
        </svg>"""

    return f"""
      <figure class="p4fig p4fig--teto">
        <figcaption class="p4fig-titulo">
          A proteção não estava no caminho da fronteira
          <span class="p4fig-sub">se o teto fosse a lei, a proteção teria vindo antes da freada
          e estaria onde a fronteira vai. Não veio, e não está.</span>
        </figcaption>

        <div class="p4fig-painel">
          <p class="p4fig-painel-rot"><span>A</span> Quando a proteção foi criada</p>
          {painel_a}
          <p class="p4fig-painel-nota">
            {pi85}% da Proteção Integral que Goiás tem hoje já existia em 1985, antes da marcha:
            em quarenta anos ela cresceu <strong>{d_pi} Mha</strong>, contra <strong>{c24} Mha</strong>
            de Cerrado convertidos. O que cresceu nos anos 2000 foi o <strong>Uso Sustentável</strong>
            &mdash; APAs, que admitem uso rural e não vedam conversão.
          </p>
        </div>

        <div class="p4fig-painel">
          <p class="p4fig-painel-rot"><span>B</span> Onde ela está, hoje</p>
          {painel_b}
          <p class="p4fig-painel-nota">
            O Norte é quem guarda mais Cerrado exposto à conversão &mdash; e <strong>{fora}%</strong>
            do que resta em Goiás está fora da única categoria que veda converter.
          </p>
        </div>

        <p class="p4fig-legenda">
          &ldquo;Barrar&rdquo; aqui tem sentido estreito: a Proteção Integral é a única categoria que
          <em>veda</em> a conversão &mdash; Reserva Legal e APP seguem valendo dentro de cada
          propriedade e protegem parte deste mesmo Cerrado. A figura separa a <em>causa</em> da
          freada, não a existência de lei ambiental. <em>(#39, #46 &rarr; D13, D17)</em>
        </p>
      </figure>"""


# --------------------------------------------------------------------------
# FIGURA 2 — emissao = area x densidade
# --------------------------------------------------------------------------
def figura2() -> str:
    cf = pd.read_csv(PROC / "carbono_por_formacao.csv")
    tot = cf[cf.formacao == "TOTAL"].iloc[0]
    f = cf[cf.formacao != "TOTAL"].copy()
    for c in ["baixa", "central", "alta"]:
        f[f"dens_{c}"] = f[f"MtCO2_{c}"] / f["area_perdida_Mha"]
    f = f.sort_values("dens_central", ascending=False).reset_index(drop=True)

    sx = Escala(0, float(tot.area_perdida_Mha), 62, 556)
    base_y, topo_y = 246, 44
    sy = Escala(0, 460, base_y, topo_y)

    rot_curto = {"Floresta nativa (galeria/cerradão)": "floresta nativa",
                 "Formação savânica (Cerrado s.s.)": "formação savânica",
                 "Campo nativo": "campo nativo"}
    classe = {"Floresta nativa (galeria/cerradão)": "flor",
              "Formação savânica (Cerrado s.s.)": "sav",
              "Campo nativo": "campo"}

    partes, x0 = [], 0.0
    for r in f.itertuples():
        x1 = x0 + r.area_perdida_Mha
        px0, px1 = sx(x0), sx(x1)
        py = sy(r.dens_central)
        meio = round((px0 + px1) / 2, 1)
        cls = classe[r.formacao]
        emis = anota("fig2", br(r.MtCO2_central, 0), f"carbono_por_formacao {cls} central")
        anota("fig2", br(r.area_perdida_Mha, 2), f"area perdida {cls} (Mha)")
        anota("fig2", br(r.dens_central, 0), f"densidade implicita {cls} (tCO2e/ha)")
        largo = px1 - px0 > 90
        # A haste do cenario fica na borda direita do retangulo quando ha largura:
        # centrada, ela cruzaria o rotulo de emissao.
        hx = round(px1 - 12, 1) if largo else meio
        partes.append(
            f'<rect class="p4-ret p4-ret--{cls}" x="{px0 + 1}" y="{py}" '
            f'width="{round(px1 - px0 - 2, 1)}" height="{round(base_y - py, 1)}"></rect>'
            f'<line class="p4-whisk" x1="{hx}" y1="{sy(r.dens_baixa)}" x2="{hx}" y2="{sy(r.dens_alta)}"></line>'
            f'<line class="p4-whisk" x1="{hx - 5}" y1="{sy(r.dens_alta)}" x2="{hx + 5}" y2="{sy(r.dens_alta)}"></line>'
            f'<line class="p4-whisk" x1="{hx - 5}" y1="{sy(r.dens_baixa)}" x2="{hx + 5}" y2="{sy(r.dens_baixa)}"></line>')
        if largo:
            partes.append(
                f'<text class="p4-ret-nome" x="{meio}" y="{py - 28}">{rot_curto[r.formacao]}</text>'
                f'<text class="p4-ret-val" x="{meio}" y="{py - 10}">{emis} Mt CO<tspan dy="3" font-size="9">2</tspan><tspan dy="-3">e</tspan></text>')
        else:
            partes.append(
                f'<line class="p4-guia" x1="{meio}" y1="{py - 4}" x2="{meio}" y2="{topo_y + 42}"></line>'
                f'<text class="p4-ret-nome" x="{meio}" y="{topo_y + 14}">{rot_curto[r.formacao]}</text>'
                f'<text class="p4-ret-val" x="{meio}" y="{topo_y + 34}">{emis} Mt</text>')
        partes.append(
            f'<text class="p4-ret-dim" x="{meio}" y="{base_y + 16}">{br(r.area_perdida_Mha, 2)} Mha</text>')
        x0 = x1

    grade = "".join(
        f'<line class="p4-grade" x1="62" y1="{sy(v)}" x2="556" y2="{sy(v)}"></line>'
        f'<text class="p4-escala" x="54" y="{sy(v) + 4}" text-anchor="end">{v}</text>'
        for v in [100, 200, 300, 400])

    razao_area = anota("fig2", br(f.iloc[1].area_perdida_Mha / f.iloc[0].area_perdida_Mha, 1),
                       "razao area savanica/floresta")
    razao_dens = anota("fig2", br(f.iloc[0].dens_central / f.iloc[1].dens_central, 1),
                       "razao densidade floresta/savanica")
    total = anota("fig2", br(tot.MtCO2_central, 0), "carbono_por_formacao TOTAL central")
    t_baixa = anota("fig2", br(tot.MtCO2_baixa, 0), "TOTAL baixa")
    t_alta = anota("fig2", br(tot.MtCO2_alta, 0), "TOTAL alta")
    area_tot = anota("fig2", br(tot.area_perdida_Mha, 2), "TOTAL area perdida Mha")

    return f"""
      <figure class="p4fig">
        <figcaption class="p4fig-titulo">
          Quem paga a conta de carbono
          <span class="p4fig-sub">cada retângulo tem <strong>largura</strong> = área convertida e
          <strong>altura</strong> = densidade de carbono; a <strong>área</strong> do retângulo é a emissão</span>
        </figcaption>
        <svg viewBox="0 0 620 290" role="img"
             aria-label="Tres retangulos lado a lado. A floresta nativa e' estreita e alta: {br(f.iloc[0].area_perdida_Mha,2)}
             milhoes de hectares a {br(f.iloc[0].dens_central,0)} toneladas de CO2 equivalente por hectare, {br(f.iloc[0].MtCO2_central,0)} megatoneladas.
             A formacao savanica e' larga e baixa: {br(f.iloc[1].area_perdida_Mha,2)} milhoes de hectares a {br(f.iloc[1].dens_central,0)} toneladas por hectare,
             {br(f.iloc[1].MtCO2_central,0)} megatoneladas. O campo nativo e' pequeno nas duas dimensoes.">
          <text class="p4-eixo-titulo" x="62" y="26">densidade de carbono &middot; t CO<tspan dy="3" font-size="9">2</tspan><tspan dy="-3">e</tspan> por hectare</text>
          {grade}
          {''.join(partes)}
          <line class="p4-eixo" x1="62" y1="{base_y}" x2="556" y2="{base_y}"></line>
          <text class="p4-eixo-titulo p4-eixo-titulo--fim" x="556" y="{base_y + 34}" text-anchor="end">área convertida 1985&ndash;2024 &middot; {area_tot} Mha no total</text>
          <text class="p4-anot" x="62" y="{base_y + 34}">0</text>
        </svg>
        <p class="p4fig-legenda">
          A savânica perde <strong>{razao_area}&times; mais área</strong> que a floresta e ainda
          assim emite menos: a floresta é <strong>{razao_dens}&times; mais densa</strong> em
          carbono, e a conta é o produto das duas coisas. Total comprometido:
          <strong>{total} Mt CO<sub>2</sub>e</strong> ({t_baixa} a {t_alta} conforme o cenário de
          densidade &mdash; as hastes verticais). Estoques por fisionomia em Tier 1 do IPCC, sem
          carbono de solo; é uma conta de <em>diferença de estoque</em>, não um inventário de
          fluxo. <em>(#47 &rarr; D18)</em>
        </p>
      </figure>"""


# --------------------------------------------------------------------------
# FIGURA 3 — quando e onde se pagou
# --------------------------------------------------------------------------
def figura3() -> str:
    ca = pd.read_csv(PROC / "carbono_regional_ato.csv")
    tab = (ca.pivot_table(index=["ato", "regiao"], values="MtCO2_por_ano", aggfunc="sum")
             .reset_index())
    cen = pd.read_csv(PROC / "carbono_centroide_ato.csv").set_index("ato")
    periodos = {"I": "1985&ndash;2000", "II": "2001&ndash;2019", "III": "2020&ndash;2024"}

    largura, x_ini, gap = 172, 22, 24
    smax = 21.0
    linhas_y = {"Norte": 78, "Centro": 108, "Sul": 138}
    paineis = []
    for i, ato in enumerate(["I", "II", "III"]):
        ox = x_ini + i * (largura + gap)
        sx = Escala(0, smax, ox + 46, ox + largura - 6)
        tot_ato = tab[tab.ato == ato]["MtCO2_por_ano"].sum()
        anota("fig3", br(tot_ato, 1), f"Mt/ano total Ato {ato}")
        barras = []
        for reg_, y in linhas_y.items():
            v = float(tab[(tab.ato == ato) & (tab.regiao == reg_)]["MtCO2_por_ano"].iloc[0])
            anota("fig3", br(v, 1), f"Mt/ano {reg_} Ato {ato}")
            cls = {"Norte": "norte", "Centro": "centro", "Sul": "sul"}[reg_]
            barras.append(
                f'<text class="p4-bar-rot" x="{ox + 42}" y="{y + 4}" text-anchor="end">{reg_}</text>'
                f'<rect class="p4-bar p4-bar--{cls}" x="{sx(0)}" y="{y - 8}" '
                f'width="{max(round(sx(v) - sx(0), 1), 1.5)}" height="16" rx="2"></rect>'
                f'<text class="p4-bar-val" x="{round(sx(v) + 6, 1)}" y="{y + 4}">{br(v, 1)}</text>')
        lat = float(cen.loc[ato, "lat_mean"])
        lat_rot = br(abs(lat), 2) + "° S"   # latitude sul lida como positiva, com o hemisferio
        anota("fig3", lat_rot, f"latitude do centroide de emissao, Ato {ato}")
        paineis.append(f"""
          <g>
            <text class="p4-mini-titulo" x="{ox}" y="30">Ato {ato}</text>
            <text class="p4-mini-sub" x="{ox}" y="46">{periodos[ato]}</text>
            <text class="p4-mini-tot" x="{ox + largura - 6}" y="30" text-anchor="end">{br(tot_ato, 1)} Mt/ano</text>
            <line class="p4-eixo" x1="{sx(0)}" y1="60" x2="{sx(0)}" y2="152"></line>
            {''.join(barras)}
            <text class="p4-cent" x="{ox}" y="180">centroide da emissão</text>
            <text class="p4-cent p4-cent--val" x="{ox}" y="196">{lat_rot}</text>
          </g>""")

    d_km = anota("fig3", br((cen.loc["III", "lat_mean"] - cen.loc["I", "lat_mean"]) * 111.32, 0),
                 "deslocamento do centroide I->III (km)")
    p_ato1 = anota("fig3", br(100 * cen.loc["I", "MtCO2_perda"]
                              / cen["MtCO2_perda"].sum(), 0), "% do total emitido no Ato I")
    sul1 = br(float(tab[(tab.ato == "I") & (tab.regiao == "Sul")]["MtCO2_por_ano"].iloc[0]), 1)
    queda = anota("fig3", br(tab[tab.ato == "I"]["MtCO2_por_ano"].sum()
                             / tab[tab.ato == "II"]["MtCO2_por_ano"].sum(), 1),
                  "razao ritmo Ato I / Ato II")

    return f"""
      <figure class="p4fig">
        <figcaption class="p4fig-titulo">
          Quando e onde se pagou
          <span class="p4fig-sub">ritmo de emissão por região (Mt CO<sub>2</sub>e por ano), na mesma escala nos três atos &mdash;
          norte em cima, sul embaixo</span>
        </figcaption>
        <svg viewBox="0 0 620 214" role="img"
             aria-label="Tres paineis na mesma escala. No Ato I o ritmo e' de {br(tab[tab.ato=='I']['MtCO2_por_ano'].sum(),1)}
             megatoneladas por ano e a maior barra e' a do Sul, {sul1}. Nos Atos II e III as barras encolhem
             para menos de cinco megatoneladas e a maior passa a ser a do Centro e a do Norte; a do Sul
             vira a menor. O centroide da emissao sobe de {br(abs(cen.loc['I','lat_mean']),2)} para
             {br(abs(cen.loc['III','lat_mean']),2)} graus de latitude sul.">
          <line class="p4-guia-cent" x1="22" y1="166" x2="598" y2="166"></line>
          {''.join(paineis)}
          <text class="p4-anot p4-anot--forte" x="598" y="196" text-anchor="end">{d_km} km ao norte &rarr;</text>
        </svg>
        <p class="p4fig-legenda">
          <strong>{p_ato1}% de toda a emissão saiu no Ato I</strong>, e saiu no Sul, a {sul1} Mt/ano.
          Depois de 2001 o ritmo cai <strong>{queda}&times;</strong> e a geografia se inverte: no Ato
          III o Sul é o menor emissor e o Centro o maior. O grosso do dano já estava feito antes de a
          marcha começar a ser notada. As barras são líquidas &mdash; no Norte a floresta nativa
          mostra ganho de área nos Atos II e III, o que abate parte da emissão savânica de lá.
          <em>(#47 &rarr; D18)</em>
        </p>
      </figure>"""


# --------------------------------------------------------------------------
# FIGURA 4 — crescimento sem desenvolvimento
# --------------------------------------------------------------------------
def figura4() -> str:
    sys.path.insert(0, str(ROOT / "scripts"))
    from deslocamento_espacial import MESO_SUL, MESO_NORTE

    ifdm = pd.read_csv(PROC / "ifdm_goias_municipal.csv")
    mm = pd.read_csv(PROC / "mapeamento_mesorregioes.csv")
    mm["regiao"] = mm["nm_meso"].map(
        lambda m: "Sul" if m in MESO_SUL else ("Norte" if m in MESO_NORTE else "Centro"))

    # O esforco: crescimento AGREGADO da area cultivada 2013->2021 (soma regional,
    # nao media de razoes municipais — a media de log-ratio infla base pequena).
    pan = pd.read_parquet(PROC / "painel_unificado.parquet")
    pan = pan[pan.ano.isin([2013, 2021])].merge(mm[["cd_mun", "regiao"]], on="cd_mun", how="left")
    cresc = {}
    for reg_ in ["Norte", "Sul"]:
        s = pan[pan.regiao == reg_].groupby("ano")["lulc_agricultura_ha"].sum()
        cresc[reg_] = 100 * (s.loc[2021] / s.loc[2013] - 1)
        anota("fig4stat", "+" + br(cresc[reg_], 0) + "%",
              f"crescimento agregado da area cultivada 2013-2021, {reg_}")
    ifdm = ifdm.merge(mm[["cd_mun", "regiao"]], on="cd_mun", how="left")
    serie = ifdm.pivot_table(index="ano", columns="regiao", values="ifdm", aggfunc="mean")
    anos = list(serie.index)

    sx = Escala(anos[0], anos[-1], 62, 470)
    sy = Escala(0.40, 0.70, 236, 46)
    linhas = {}
    for reg_ in ["Sul", "Centro", "Norte"]:
        linhas[reg_] = poly([(sx(a), sy(serie.loc[a, reg_])) for a in anos])
    faixa = (poly([(sx(a), sy(serie.loc[a, "Sul"])) for a in anos]) + " " +
             poly([(sx(a), sy(serie.loc[a, "Norte"])) for a in reversed(anos)]))

    g0 = anota("fig4A", br(serie.loc[2013, "Norte"] - serie.loc[2013, "Sul"], 3),
               "vao Norte-Sul 2013")
    g1 = anota("fig4A", br(serie.loc[2023, "Norte"] - serie.loc[2023, "Sul"], 3),
               "vao Norte-Sul 2023")
    for reg_ in ["Sul", "Centro", "Norte"]:
        anota("fig4A", br(serie.loc[2013, reg_], 2), f"IFDM {reg_} 2013")
        anota("fig4A", br(serie.loc[2023, reg_], 2), f"IFDM {reg_} 2023")

    grade = "".join(
        f'<line class="p4-grade" x1="62" y1="{sy(v)}" x2="470" y2="{sy(v)}"></line>'
        f'<text class="p4-escala" x="54" y="{sy(v) + 4}" text-anchor="end">{br(v, 2)}</text>'
        for v in [0.45, 0.50, 0.55, 0.60, 0.65, 0.70])
    ticks = "".join(
        f'<text class="p4-escala" x="{sx(a)}" y="252" text-anchor="middle">{a}</text>'
        for a in [2013, 2016, 2019, 2023])

    painel_a = f"""
        <svg viewBox="0 0 620 264" role="img"
             aria-label="IFDM medio por regiao de 2013 a 2023. As tres linhas sobem quase paralelas.
             O vao entre Norte e Sul era de {g0} em 2013 e de {g1} em 2023: a faixa sombreada entre as
             duas linhas nao se fecha.">
          <text class="p4-eixo-titulo" x="62" y="26">IFDM médio dos municípios (0 a 1)</text>
          {grade}
          <polygon class="p4-faixa-vao" points="{faixa}"></polygon>
          <polyline class="p4-linha p4-linha--centro" points="{linhas['Centro']}"></polyline>
          <polyline class="p4-linha p4-linha--sul" points="{linhas['Sul']}"></polyline>
          <polyline class="p4-linha p4-linha--norte" points="{linhas['Norte']}"></polyline>
          <text class="p4-rot p4-rot--sul" x="478" y="{sy(serie.loc[2023, 'Sul'])}">Sul {br(serie.loc[2023, 'Sul'], 2)}</text>
          <text class="p4-rot p4-rot--centro" x="478" y="{sy(serie.loc[2023, 'Centro'])}">Centro {br(serie.loc[2023, 'Centro'], 2)}</text>
          <text class="p4-rot p4-rot--norte" x="478" y="{sy(serie.loc[2023, 'Norte']) + 6}">Norte {br(serie.loc[2023, 'Norte'], 2)}</text>
          <line class="p4-vao-med" x1="{sx(2013)}" y1="{sy(serie.loc[2013, 'Sul'])}" x2="{sx(2013)}" y2="{sy(serie.loc[2013, 'Norte'])}"></line>
          <line class="p4-vao-med" x1="{sx(2023)}" y1="{sy(serie.loc[2023, 'Sul'])}" x2="{sx(2023)}" y2="{sy(serie.loc[2023, 'Norte'])}"></line>
          <text class="p4-vao-rot" x="{sx(2013) + 6}" y="{sy(serie.loc[2013, 'Norte']) + 16}">vão {g0}</text>
          <text class="p4-vao-rot" x="{sx(2023) - 6}" y="{sy(serie.loc[2023, 'Norte']) + 16}" text-anchor="end">vão {g1}</text>
          <line class="p4-eixo" x1="62" y1="236" x2="470" y2="236"></line>
          {ticks}
        </svg>"""

    # O painel de coeficientes saiu (31/jul): pedia leitura de beta padronizado e
    # IC para dizer o que a prosa ao lado ja' diz em uma frase. O numero do painel
    # 2FE fica na legenda, que e' onde ele pesa.
    gr = pd.read_csv(PROC / "desenvolvimento_gradiente.csv")
    p2fe = gr[(gr.bloco == "C2_painel2fe") & (gr.modelo == "d_l_va+d_l_area")
              & (gr.regressor == "d_l_area")].iloc[0]
    dobra = anota("fig4", br(p2fe.beta * np.log(2), 3),
                  "efeito 2FE de dobrar a area, em pontos de IFDM")

    return f"""
      <figure class="p4fig">
        <figcaption class="p4fig-titulo">
          O que a área comprou
          <span class="p4fig-sub">o Norte quase dobrou a lavoura entre 2013 e 2021; o
          desenvolvimento municipal subiu em toda parte, e o vão continuou onde estava</span>
        </figcaption>

        <p class="p4-stats">
          <span class="p4-stats-rot">o esforço &middot; área cultivada 2013&rarr;2021</span>
          <span class="p4-stat"><b>+{br(cresc['Norte'], 0)}%</b> Norte</span>
          <span class="p4-stat p4-stat--fraco"><b>+{br(cresc['Sul'], 0)}%</b> Sul</span>
        </p>

        {painel_a}

        <p class="p4fig-legenda">
          Ano a ano, não só nas pontas: as três trajetórias sobem quase paralelas, e o vão entre
          Norte e Sul &mdash; <strong>{g0}</strong> em 2013, <strong>{g1}</strong> em 2023 &mdash;
          oscila sem tendência de fechamento. Média simples dos municípios de cada região (82 no
          Sul, 114 no Centro, 50 no Norte). O IFDM (Índice FIRJAN: emprego&amp;renda, educação,
          saúde) é proxy de desenvolvimento, não de bem-estar amplo, e a leitura é
          <strong>associativa</strong>, não causal. Num painel de efeitos fixos dentro do
          município, dobrar a área vale <strong>{dobra}</strong> ponto de IFDM &mdash; contra
          ~0,15 que o índice subiu na década. <em>(#51 &rarr; D14)</em>
        </p>
      </figure>"""


# --------------------------------------------------------------------------
def aplicar(pecas: list[str]) -> None:
    """Substitui as figuras dentro de reforma.html, entre os marcadores.

    Na primeira aplicacao os marcadores ainda nao existem: cai para trocar os
    <figure class="p4fig..."> na ordem em que aparecem e ja deixa os marcadores
    no lugar, para as proximas rodadas serem so texto-entre-marcas.
    """
    html = HTML.read_text(encoding="utf-8")
    for i, peca in enumerate(pecas, start=1):
        ini, fim = f"<!-- fig-perna4:{i} -->", f"<!-- /fig-perna4:{i} -->"
        bloco = f"{ini}\n{peca}\n        {fim}"
        if ini in html:
            a = html.index(ini)
            b = html.index(fim, a) + len(fim)
        else:
            a = html.index('<figure class="p4fig', 0 if i == 1 else b_ant)
            b = html.index("\n        </figure>", a) + len("\n        </figure>")
        html = html[:a] + bloco + html[b:]
        b_ant = html.index(fim) + len(fim)
    # newline explicito: no Windows o write_text traduz \n para \r\n e reescreve o
    # arquivo INTEIRO em CRLF — um diff de milhares de linhas por causa de 4 figuras.
    HTML.write_text(html, encoding="utf-8", newline="\n")
    print(f"[OK] {HTML.relative_to(ROOT)} atualizado ({len(pecas)} figuras)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Figuras SVG da Perna 4")
    ap.add_argument("--auditar", action="store_true",
                    help="lista todo numero que aparece na tela e sua fonte")
    ap.add_argument("--aplicar", action="store_true",
                    help="escreve as figuras direto no reforma.html")
    args = ap.parse_args()

    figs = [figura1(), figura2(), figura3(), figura4()]
    # Toda SVG ganha um envelope que rola sozinho: no celular a figura encolheria
    # ate' o rotulo ficar ilegivel, e e' melhor rolar a figura que a pagina.
    def envelopar(s: str) -> str:
        return (s.replace("<svg ", '<div class="p4fig-svg"><svg ')
                 .replace("</svg>", "</svg></div>"))

    pecas = [envelopar(f).strip() for f in figs]
    frag = "\n".join(pecas)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(frag, encoding="utf-8", newline="\n")
    print(f"[OK] {SAIDA.relative_to(ROOT)} ({len(frag)} chars)")

    if args.aplicar:
        aplicar([("        " + p).replace("\n      ", "\n        ") for p in pecas])

    if args.auditar:
        print("\nNumeros na tela x fonte")
        print("-" * 76)
        for fig, val, fonte in AUDIT:
            print(f"  {fig:7s} {val:>10s}   {fonte}")
        print(f"\n  {len(AUDIT)} numeros, todos lidos de data/processed/ nesta execucao.")


if __name__ == "__main__":
    main()
