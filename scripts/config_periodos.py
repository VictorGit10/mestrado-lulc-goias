"""config_periodos.py — Definicoes canonicas de ATOS e MARCOS
============================================================

Fonte unica de verdade para periodizacao e marcos institucionais.
Todos os scripts devem importar daqui em vez de definir suas proprias copias.

Periodizacao data-driven (triangulacao de 3 metodos):
    - Metodo primario: sup-F multivariado (Pipeline #29a)
    - Metodos de sensibilidade: Rodionov STARS (Pipeline #29b),
      KL/TV de matrizes de transicao (Pipeline #29c)
    - Intensity Analysis (Pipeline #31) como diagnostico complementar

Fronteiras confirmadas (primario + sensibilidade):
    ~2001: sup-F (F=62.2) + KL/TV (pico 2003)
    ~2020: sup-F (F=21.5) + KL/TV (pico 2018-2020)

Fronteira 2005/2006 — nota metodologica (NAO incluida como fronteira de periodo):
    Detectada por STARS (shifts em 2004/2006 com l=5, alpha=0.05) e KL/TV
    (pico local 2003), mas NAO pelo metodo primario (sup-F multivariado).
    Intensity Analysis confirma: as sub-fases 2001-05 e 2006-19 diferem em
    COMPOSICAO (perda de veg_nat 5x maior em 2001-05, p=0.0008) mas nao em
    TAXA TOTAL (Mann-Whitney p=0.060, poder=0.63 com n=4). Sem o outlier
    2004, p=0.189. A fronteira e sensivel ao ponto de corte (significativa
    em 2005, marginal em 2004, NS em 2006). Por essas razoes, optou-se por
    3 periodos, documentando a sub-fase 2001-05 como nota metodologica.

    Verificacao de sanidade (Pipeline #30):
    - Falso positivo (ruido branco, F_threshold=4.0): FPR=0.110
    - Sensibilidade de parametros: 2001 e 2020 robustas em 9/9 e 6/9
      combinacoes; 1991 instavel (desloca 1989-1993)
    - Consistencia univariado vs multivariado: 3 quebras multi sao subconjunto
      das 6 univariadas
    - STARS: com alpha=0.01, nada detecta; com alpha=0.05, 3 shifts

    Intensity Analysis (Pipeline #31):
    - Kruskal-Wallis 3 periodos: H=20.26, p<0.001
    - P2(2001-05) vs P3(2006-19) taxa total: p=0.060 (NS), poder=0.63
    - P2 vs P3 composicional (veg_nat perda): p=0.0008 (***)
    - Bootstrap IC P2-P3 (taxa total): [0.0007, 0.0055], nao contem zero
    - Bootstrap IC P2-P3 (veg_nat perda): [0.0042, 0.0077], nao contem zero
    - Sensibilidade ao corte: significativo em 2005 (p=0.046), NS em 2006 (p=0.12)

Estrutura:
    - ATOS: periodos LULC empiricos com fronteiras data-driven
    - MARCOS: eventos institucionais com tipologia evidencial (A/B/C)
    - ANOS_MARCO: conjunto de anos com pino institucional
    - CORES_ATO: paleta de cores por ato (consistente com utils.js)
"""

from __future__ import annotations

# ─────────────────────────── ATOS ───────────────────────────
# Titulos descritivos da dinamica LULC observada (NAO de marcos institucionais).
# Fronteiras estabelecidas por triangulacao (P#29a-c, #30, #31).

ATOS = {
    "I":   {"inicio": 1985, "fim": 2000, "titulo": "Pastagem como herança"},
    "II":  {"inicio": 2001, "fim": 2019, "titulo": "Expansão e intensificação"},
    "III": {"inicio": 2020, "fim": 2024, "titulo": "Conversão seletiva"},
}

# Versao flat para scripts que so precisam de (inicio, fim, titulo)
ATOS_FLAT = {k: (v["inicio"], v["fim"], v["titulo"]) for k, v in ATOS.items()}

# ─────────────────────────── MARCOS ───────────────────────────
# Referencias institucionais que contextualizam as transicoes LULC
# nos atos data-driven. Nao sao unidades analiticas independentes —
# sao pontos no tempo que ajudam a narrar o periodo.
#
# Tipologia:
#   A — Evidencia causal: unico marco com quebra estrutural GO-especifica
#       + DiD robusto (Lei Kandir)
#   B — Referencia narrativa: evento institucionalmente significativo;
#       contextualiza as transicoes sem afirmacao causal
#   C — Limite da serie: 1985 e 2024
#
# escopo_empirico:
#   go_especifico  — quebra em GO sem quebra equivalente em TO
#   cerrado_amplo  — quebra simultanea em GO e TO
#   sem_quebra     — nenhuma quebra detectavel em GO ou TO (+-2a)
#   nao_aplicavel  — limites da serie (1985, 2024)

MARCOS = {
    1985: {
        "titulo": "Início da série / Redemocratização",
        "evidencia": "C",       # fronteira
        "escopo_empirico": "nao_aplicavel",
    },
    1994: {
        "titulo": "Plano Real",
        "evidencia": "B",       # referencia narrativa
        "escopo_empirico": "cerrado_amplo",
        "nota": "Perda de veg_nat desacelera de 0,88 pp/a (1990-93) para 0,63 pp/a (1995-98). "
                "A inflexão mais nítida vem em 1998, alinhada à Kandir.",
    },
    1996: {
        "titulo": "Lei Kandir",
        "evidencia": "A",       # evidencia causal
        "escopo_empirico": "go_especifico",
        "nota": "Único evento com efeito diferenciado em GO: perda de veg_nat desacelera "
                "de 0,54 pp/a para 0,41 pp/a após 1998, enquanto agricultura se expande "
                "no sudoeste. DiD confirma divergência vs estados-controle após 1996.",
    },
    2002: {
        "titulo": "Crédito e demanda chinesa",
        "evidencia": "B",       # referencia narrativa
        "escopo_empirico": "cerrado_amplo",
        "nota": "Agricultura goiana salta de 9,3% para 10,8% do território em 3 anos "
                "(2001-04). Em 2004, soja-milho avança 0,94 pp em um único ano.",
    },
    2003: {
        "titulo": "Boom de commodities",
        "evidencia": "B",       # referencia narrativa
        "escopo_empirico": "cerrado_amplo",
        "nota": "Perda de veg_nat atinge 0,49 pp/a em 2003 — a maior desde 1993. "
                "Super-ciclo de preços viabiliza substituição de pastagem por soja-milho.",
    },
    2012: {
        "titulo": "Código Florestal",
        "evidencia": "B",       # referencia narrativa
        "escopo_empirico": "sem_quebra",
        "nota": "Após o código, perda de veg_nat acelera de 0,11 pp/a (2008-11) para "
                "0,21 pp/a (2012-15); agricultura expande 2,3x mais rápido "
                "(0,20 → 0,45 pp/a). Ausência de desaceleração é o achado.",
    },
    2018: {
        "titulo": "Reorganização de mercado",
        "evidencia": "B",       # referencia narrativa
        "escopo_empirico": "cerrado_amplo",
        "nota": "Perda de veg_nat estabiliza em torno de 0,10 pp/a; pastagem cede "
                "0,33-0,61 pp/a consistentemente (2018-21). Agricultura para de "
                "crescer; vegetação se recupera lentamente.",
    },
    2024: {
        "titulo": "Estado atual",
        "evidencia": "C",       # fronteira
        "escopo_empirico": "nao_aplicavel",
    },
}

# Versao flat para scripts que so precisam de {ano: titulo}
MARCOS_FLAT = {ano: m["titulo"] for ano, m in MARCOS.items()}

# Anos com pino institucional (para destacar no atlas e na regua)
ANOS_MARCO = set(MARCOS.keys())

# ─────────────────────────── CORES ───────────────────────────
# Paleta consistente com utils.js

CORES_ATO = {
    "I": "#8b3a1d",
    "II": "#a85234",
    "III": "#2d5a3d",
}

# ─────────────────────────── EXPORTS ───────────────────────────

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    print("ATOS (data-driven, 3 periodos):")
    for k, v in ATOS.items():
        print(f"  {k}: {v['inicio']}-{v['fim']}  {v['titulo']}")
    print()
    print("MARCOS:")
    for ano, m in MARCOS.items():
        print(f"  {ano}: [{m['evidencia']}] {m['titulo']}  ({m['escopo_empirico']})")
        if "nota" in m:
            nota = m["nota"][:80].replace("→", "->")
            print(f"        -> {nota}...")