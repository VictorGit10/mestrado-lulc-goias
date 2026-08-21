"""gerar_apendice.py --- Apendice A: especificacoes completas dos modelos.

Escreve `cap/07_apendice.tex` a partir dos CSVs que os pipelines gravaram, de
modo que nenhum coeficiente do apendice seja digitado a mao. Rodar:

    py -3.14 qualificacao/apendice/gerar_apendice.py

Fontes:
    data/processed/deslocamento_bracket_slx.csv        (#49  --- SLX direcional)
    data/processed/drive_horse_race_latitude.csv       (#56  --- corrida de exposicoes)
    data/processed/drive_amc_apt_confirmatorio.csv     (#52  --- shift-share confirmatorio)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent.parent
PROC = RAIZ / "data" / "processed"
SAIDA = RAIZ / "qualificacao" / "cap" / "07_apendice.tex"

BR = chr(92)


def esc(s) -> str:
    """Escapa texto vindo do CSV: ele traz "#52", "%", "_" e afins.

    Guarda o ausente como `num()` e `p_val()` já guardavam: sem isto, uma célula
    vazia do CSV vira a string "nan" e sai impressa na tabela. Foi o defeito que
    a leitura externa de 20/ago encontrou nas Tabelas de placebos e de depleção.
    """
    if s is None or (not isinstance(s, str) and pd.isna(s)):
        return "---"
    s = str(s)
    for c in ("&", "%", "$", "#", "_", "{", "}"):
        s = s.replace(c, BR + c)
    # os CSVs trazem símbolos que o pdflatex não conhece em modo texto
    s = s.replace("~", "$" + BR + "sim$")
    for u, tex in (("Δ", "$" + BR + "Delta$"),
                   ("→", "$" + BR + "rightarrow$"),
                   ("≤", "$" + BR + "leq$"), ("≥", "$" + BR + "geq$"),
                   ("²", "$^2$"), ("–", "--"), ("—", "---"),
                   ("β", "$" + BR + "beta$"), ("ρ", "$" + BR + "rho$")):
        s = s.replace(u, tex)
    return s


# ATENCAO ao mapear estes tres. No #39 as colunas se chamam `lestoque`, `lestoque2` e
# `ldeplecao`, mas o `l` NAO e log: o codigo atribui `estoque_prev` e `deplecao_prev`
# crus (fronteira_fechando.py:260-262) e `np.log` nao aparece no arquivo. Rotula-los
# como "log" -- que foi o que este gerador fez ate 20/ago/2026 -- manda o leitor
# reconstruir o modelo com uma transformacao que a estimacao nao aplicou.
ROTULO_REGRESSOR = {
    "lestoque_z":                 "estoque defasado (z)",
    "lestoque2_z":                "estoque defasado$^2$ (z)",
    "ldeplecao_z":                "depleção defasada (z)",
    "zd_cambio_real_efetivo":     "$" + BR + "Delta$ câmbio real (z)",
    "zd_preco_recebido_soja_idx": "$" + BR + "Delta$ preço da soja (z)",
    "zd_credito_rural_go_real":   "$" + BR + "Delta$ crédito rural (z)",
    "d_l_va":                     "$" + BR + "Delta$ log VA agro",
    "d_l_area":                   "$" + BR + "Delta$ log área cultivada",
}


def reg(nome):
    """Nome legível do regressor; cai no cru escapado se não houver rótulo."""
    return ROTULO_REGRESSOR.get(str(nome), esc(nome))


def num(v, casas=3, mais=False):
    """Numero no padrao brasileiro, dentro de $...$ para o traco de menos certo."""
    if pd.isna(v):
        return "---"
    s = f"{v:+.{casas}f}" if mais else f"{v:.{casas}f}"
    return "$" + s.replace(".", "{,}") + "$"


def p_val(v):
    if pd.isna(v):
        return "---"
    if v < 0.001:
        return "$<0{,}001$"
    return "$" + f"{v:.3f}".replace(".", "{,}") + "$"


def n_obs(v) -> str:
    """Contagem no padrao brasileiro (ponto de milhar)."""
    if pd.isna(v):
        return "---"
    return f"{int(v):,}".replace(",", ".")


def tabela(linhas, colspec, cab, legenda, rotulo, nota,
           fonte="elaboração própria.", tam="small", colsep=None):
    r"""`colsep` aperta o espaco entre colunas (em pt) dentro do ambiente table.

    So a Tabela SAR/SEM precisa: com 14 colunas ela estourava a mancha em
    80,5pt. Diminuir a fonte tornaria a tabela ilegivel e tirar coluna tiraria
    informacao; o espaco entre colunas e' o unico dos tres que nao custa nada.
    O ajuste morre com o \end{table}, e nao vaza para as tabelas seguintes.
    """
    # `!ht` e nao `htb`: com a barreira de flutuante, `b` fazia a tabela grande descer
    # ao pe de uma pagina nova e deixar uma faixa vazia no topo. O `!` afrouxa os
    # limites de tamanho para que ela suba ao alto da pagina seguinte.
    out = [BR + "begin{table}[!ht]", BR + "centering"]
    if colsep is not None:
        out.append(BR + "setlength{" + BR + "tabcolsep}{" + str(colsep) + "pt}")
    out += [
           BR + f"caption[{legenda[0]}]{{{legenda[1]}}}",
           BR + "label{" + rotulo + "}", BR + tam,
           BR + "begin{tabular}{" + colspec + "}", BR + "toprule", cab,
           BR + "midrule"]
    out += linhas
    out += [BR + "bottomrule", BR + "end{tabular}",
            BR + "fontefig{" + fonte + "}"]
    if nota:
        out.append(BR + "notafig{" + nota + "}")
    out.append(BR + "end{table}")
    return BR.join([]) + chr(10).join(out)


# ---------------------------------------------------------------------------
# A.1 --- Notação comum
# ---------------------------------------------------------------------------

# A marca de raiz do editor vai no arquivo GERADO. Posta so no .tex, ela
# sumiria na primeira regeneracao -- e sem ela o editor abre o apendice
# sem saber a que documento ele pertence.
PREAMBULO = r"""% !TEX root = ../main.tex
\chapter{Especificações completas dos modelos}
\label{ap:especificacoes}

Este apêndice reúne, para cada desenho inferencial de que dependem as
afirmações do Capítulo~\ref{cap:resultados}, a equação estimada, a definição e
a escala das variáveis, a estrutura de efeitos fixos, o agrupamento dos
erros-padrão, o número de observações e de unidades, e o resultado de \emph{todas}
as especificações rodadas em cada grade --- e não apenas das que o texto
comenta. O objetivo é que os modelos possam ser reconstruídos a partir deste
documento, sem recurso ao repositório. São sete blocos: a precedência temporal
entre as séries regionais; o teste espacial do deslocamento; a dependência
espacial nas formas SAR e SEM; o desenho \emph{shift-share} do \emph{drive}
comum, com a sua bateria de placebos e a corrida entre exposições rivais; a
grade confirmatória completa; o teto de oferta, com a grade inteira de
tratamentos da variável de depleção; e o desenvolvimento municipal.

\textbf{O que não está aqui, e por quê.} Três coisas. As \textbf{estatísticas
das quebras estruturais} já têm quadro próprio no corpo do texto
(Quadro~\ref{quadro:quebras}), e repeti-las aqui seria duplicação. O
\textbf{ajuste de mistura da idade da pastagem} não é regressão: seus
parâmetros são médias, dispersões e pesos das duas componentes, e estão
enunciados na própria Seção~\ref{sec:res-perna2}, com a figura que os sustenta.
E a \textbf{grade exploratória} do \emph{drive} comum --- 192 combinações,
contra as 14 da confirmatória --- fica de fora por decisão de desenho, não de
espaço: ela existe para gerar hipóteses sob controle de multiplicidade, e
nenhuma afirmação do texto se apoia nela. Quem quiser conferi-la encontra o
arquivo nomeado na Seção~\ref{sec:met-repro}.

As tabelas deste apêndice são geradas por \texttt{apendice/gerar\_apendice.py} a
partir dos mesmos arquivos que os pipelines gravam; nenhum coeficiente foi
transcrito à mão.

\section{Convenções comuns}
\label{ap:convencoes}

\textbf{Alcance destas convenções.} Elas valem para os desenhos em painel de
AMCs --- as Seções~\ref{ap:slx} a \ref{ap:oferta}. Dois blocos correm sobre
outra unidade e \emph{não} as seguem: a precedência temporal
(Seção~\ref{ap:precedencia}), que usa séries anuais agregadas por região, e o
desenvolvimento municipal (Seção~\ref{ap:ifdm}), cujo primeiro bloco é uma
seção transversal de municípios em \emph{nível}. Cada um declara as suas na
abertura da seção.

\textbf{Unidade e painel.} As regressões em painel deste apêndice correm sobre
o painel de 166 Áreas Mínimas Comparáveis de Goiás, 1985--2024 (\(166 \times 40
= 6.640\) células), descrito na Seção~\ref{sec:met-amc}. Quando uma fonte não
cobre a janela inteira, o \(n\) reportado na tabela é o efetivo após exclusão de
ausentes por lista.

\textbf{Primeira diferença (D7).} Nesses desenhos o desfecho é a variação
anual, e não o nível: \(\Delta y_{it} = y_{it} - y_{i,t-1}\). É essa
transformação que desarma o vazamento entre regressor e regressando documentado
na Seção~\ref{sec:met-painel}.

\textbf{Padronização.} As exposições entram em \emph{escore-z} calculado sobre
a seção transversal das 166 unidades \(\tilde{E}_i = (E_i - \bar{E})/\sigma_E\),
com \(\sigma\) populacional. Os coeficientes de interação lêem-se, portanto,
como efeito de um desvio-padrão de exposição.

\textbf{Efeitos fixos e erros-padrão.} Salvo indicação em contrário, as
especificações em painel trazem efeito fixo de unidade \emph{e} de ano (2FE) e
erros-padrão agrupados nas duas dimensões. O agrupamento efetivamente aplicado
é reportado em cada tabela, porque há especificações em que ele recai para
agrupamento só por unidade --- por escolha do desenho, no painel municipal da
Seção~\ref{ap:ifdm}, ou porque a matriz de covariância bidimensional não é
positiva-definida. Onde uma especificação dispensa o efeito fixo de ano, a
própria linha o diz.

\textbf{Duas réguas de inferência.} Onde o desenho é do tipo
\emph{shift-share}, o \(p\) agrupado e o \(p\) de permutação circular do
\emph{shifter} são reportados lado a lado. Eles não são comparáveis entre si: o
primeiro trata cada ano como realização independente do choque, e o segundo
não. A régua defensável é a segunda, pela razão exposta na
Seção~\ref{sec:met-instrumental}.
"""


# ---------------------------------------------------------------------------
# A.2 --- Teste espacial do deslocamento (SLX direcional, #49)
# ---------------------------------------------------------------------------

SLX_TEXTO = r"""
\section{Teste espacial do deslocamento local (Perna 3a)}
\label{ap:slx}

A hipótese é a de que a lavoura que avança numa unidade empurre a pastagem das
unidades \emph{ao sul} dela. O desenho é um modelo espacial de defasagem dos
\emph{regressores} (SLX), estimado em primeira diferença com efeitos fixos de
unidade e de ano:

\begin{equation}
\Delta y_{it} = \beta\,\Delta x_{it}
             + \theta\,(W\Delta x)_{it}
             + \alpha_i + \lambda_t + \varepsilon_{it},
\label{eq:slx}
\end{equation}

\noindent em que \(\Delta y_{it}\) é a variação anual da área de pastagem (ou
do efetivo bovino, nas linhas assim indicadas) da unidade \(i\) no ano \(t\);
\(\Delta x_{it}\) é a variação anual da área de lavoura \emph{na própria
unidade}; \(\alpha_i\) e \(\lambda_t\) são os efeitos fixos; e \((W\Delta
x)_{it}\) é a média da variação de lavoura nas unidades vizinhas selecionadas
por \(W\). O parâmetro de interesse é \(\theta\), não \(\beta\): \(\beta\)
mede substituição \emph{dentro} da unidade, que não é deslocamento.

\textbf{Matriz de pesos.} \(W\) é \(166 \times 166\), construída sobre os oito
vizinhos mais próximos de cada unidade por distância euclidiana entre
centroides em EPSG:5880, e \textbf{padronizada por linha}. A direção é imposta
por filtro: em \(W_{\mathrm{sul}}\) só permanecem, entre os oito, os vizinhos de
centroide mais ao sul; em \(W_{\mathrm{norte}}\), os mais ao norte. A diagonal é
nula. \(W_{\mathrm{norte}}\) é \emph{placebo}: se o mecanismo for o empurrão da
lavoura do sul, o termo de vizinhança deve aparecer com \(W_{\mathrm{sul}}\) e
não com \(W_{\mathrm{norte}}\).

\textbf{Grade de especificações.} A grade é o produto de três réguas de
lavoura --- a classe Agricultura do MapBiomas, a união dela com o Mosaico de
Usos (o \emph{bracket} da decisão D26) e a área plantada de soja do SIDRA, que
é imune ao classificador --- por duas janelas --- a série plena e a truncada em
2019, que exclui o trecho de deriva do Mosaico --- por três modelos, sendo um
deles o placebo com $W_{\mathrm{norte}}$. São dezoito especificações e trinta e
seis coeficientes, já que cada uma estima o termo local e o de vizinhança; a
Tabela~\ref{tab:slx} traz os dezoito termos de vizinhança, que são os de
interesse.
"""


def secao_slx() -> str:
    d = pd.read_csv(PROC / "deslocamento_bracket_slx.csv")
    d = d[d.termo == "vizinhanca"].copy()
    rot = {"agric": "Agricultura", "agric_uniao": r"Agric. $\cup$ Mosaico",
           "soja_sidra": "Soja (SIDRA)"}
    W_SUL, W_NOR = r"$W_{\mathrm{sul}}$", r"$W_{\mathrm{norte}}$ (placebo)"
    DP, DB = r"$\Delta$ pastagem", r"$\Delta$ bovinos"
    chave = {"pasto_sul": (W_SUL, DP), "pasto_norte": (W_NOR, DP),
             "bovinos_sul": (W_SUL, DB)}

    def classificar(modelo: str) -> str:
        if "placebo" in modelo:
            return "pasto_norte"
        return "bovinos_sul" if "bovinos" in modelo else "pasto_sul"

    linhas = []
    for jan, jan_rot in (("plena", "Janela plena (1985--2024)"),
                         ("truncada 1985–2019", "Janela truncada (1985--2019)")):
        linhas.append(r"\multicolumn{7}{l}{\textit{" + jan_rot + r"}} \\")
        for _, r in d[d.janela == jan].iterrows():
            w, des = chave[classificar(r["modelo"])]
            linhas.append(" & ".join([
                (rot[r["regua"]] if r["regua"] in rot else esc(r["regua"])), des, w,
                num(r["beta"], 3, mais=True), num(r["se"], 3), p_val(r["p"]),
                f'{int(r["n"]):,}'.replace(",", "."),
            ]) + r" \\")
    cab = (r"\textbf{Régua de lavoura} & \textbf{Desfecho} & \textbf{$W$} & "
           r"\textbf{$\hat{\theta}$} & \textbf{EP} & \textbf{$p$} & \textbf{$n$} \\")
    nota = (r"estimação por mínimos quadrados com efeitos fixos de unidade e de ano; "
            r"erros-padrão agrupados por unidade. O coeficiente reportado é o do termo "
            r"de vizinhança $\hat{\theta}$ da Equação~\ref{eq:slx}; o termo local "
            r"$\hat{\beta}$ é omitido porque mede substituição dentro da unidade, que "
            r"não é deslocamento. O $n$ menor nas linhas da soja reflete o início mais "
            r"tardio da série municipal do SIDRA.")
    return SLX_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "llccccr", cab,
        ("Termo de vizinhança do teste espacial",
         "Termo de vizinhança do teste espacial do deslocamento, nas dezoito especificações."),
        "tab:slx", nota)


# ---------------------------------------------------------------------------
# A.3 --- Drive comum: shift-share e corrida entre exposições (#52 / #54 / #56)
# ---------------------------------------------------------------------------

SS_TEXTO = r"""
\section{\emph{Drive} comum: desenho \emph{shift-share} (Perna 3b)}
\label{ap:shiftshare}

A hipótese é a de que um choque macroeconômico nacional atinja de modo
diferente lugares com exposição diferente. A especificação estimada é de
interação pura, em primeira diferença e com dois conjuntos de efeitos fixos:

\begin{equation}
\Delta y_{it} = \gamma\,\bigl(\tilde{s}_{t-1} \times \tilde{E}_i\bigr)
             + \alpha_i + \lambda_t + \varepsilon_{it},
\label{eq:shiftshare}
\end{equation}

\noindent em que \(\Delta y_{it}\) é a variação anual do efetivo bovino da
unidade \(i\) (em milhões de cabeças); \(\tilde{s}_{t-1}\) é o \emph{shifter}
nacional --- a variação padronizada do índice de taxa de câmbio efetiva real,
defasada um ano ---; e \(\tilde{E}_i\) é a exposição local padronizada, fixa no
tempo.

Três propriedades da equação merecem registro, porque determinam o que ela pode
e não pode responder. Primeira: \textbf{não há termos principais}. O
\emph{shifter} é comum a todas as unidades num dado ano e é absorvido por
\(\lambda_t\); a exposição é fixa no tempo e é absorvida por \(\alpha_i\). O
que resta identificado é apenas o \emph{gradiente} do efeito --- se o choque
morde mais onde a exposição é maior --- e nunca o seu nível. Segunda: por
isso mesmo, \(\gamma\) não mede o efeito do câmbio sobre o rebanho, e nenhum
número deste apêndice autoriza essa leitura. Terceira: o número de realizações
independentes do choque é o número de anos, cerca de 38, e não o número de
células do painel; nenhuma quantidade adicional de unidades espaciais o
aumenta. É essa a razão de o \(p\) agrupado e o \(p\) de permutação divergirem.

\subsection{Inferência por permutação}

A permutação circular reembaralha o \emph{shifter} ao longo dos anos,
preservando a sua autocorrelação, e recalcula \(\hat{\gamma}\) em cada
reembaralhamento sobre o desfecho duplamente centrado. O \(p\) reportado é a
proporção de reembaralhamentos que produzem estatística ao menos tão extrema
quanto a observada. Com 38 anos, o menor \(p\) atingível é da ordem de
\(1/38 \approx 0{,}026\), o que impõe um piso à resolução da régua.

\subsection{A corrida entre exposições}

A bateria de placebos do Capítulo~\ref{cap:resultados} é toda de \emph{desfecho}:
ela pergunta se o sinal aparece onde não deveria. A
Tabela~\ref{tab:horserace} responde a outra pergunta, que é a decisiva para uma
\emph{share} espacial --- se a exposição escolhida é a certa --- pondo as
exposições rivais na mesma regressão. A latitude entra como confundidor puro:
ela mede ``quão ao norte'' sem nenhum conteúdo agronômico.
"""


def secao_shiftshare() -> str:
    h = pd.read_csv(PROC / "drive_horse_race_latitude.csv")
    linhas = []
    for _, r in h.iterrows():
        linhas.append(" & ".join([
            esc(r["spec"]), esc(r["descricao"]), esc(r["rotulo"]),
            num(r["beta"], 3, mais=True), num(r["se"], 3),
            p_val(r["p_agrupado"]), p_val(r["p_circular"]),
            num(r["r2_within"], 4),
        ]) + r" \\")
    cab = (r"\textbf{Esp.} & \textbf{Especificação} & \textbf{Exposição do termo} & "
           r"\textbf{$\hat{\gamma}$} & \textbf{EP} & \textbf{$p_{\mathrm{agr}}$} & "
           r"\textbf{$p_{\mathrm{perm}}$} & \textbf{$R^2_w$} \\")
    n_obs, n_amc = int(h["n_obs"].iloc[0]), int(h["n_amc"].iloc[0])
    nota = (r"desfecho: variação anual do efetivo bovino. Efeitos fixos de unidade e de "
            r"ano em todas as linhas; erros-padrão agrupados por unidade e por ano "
            r"($n = " + f"{n_obs:,}".replace(",", ".") + r"$ observações, "
            + str(n_amc) + r" unidades). $p_{\mathrm{agr}}$ é o $p$ do erro-padrão "
            r"agrupado e $p_{\mathrm{perm}}$ o da permutação circular do \emph{shifter}; "
            r"as duas réguas não são comparáveis entre si, e a segunda é a defensável. "
            r"$R^2_w$ é o $R^2$ \emph{within}. Quando uma especificação traz mais de uma "
            r"exposição, cada linha reporta o termo de interação da exposição nomeada, "
            r"com as demais mantidas na mesma regressão.")
    return SS_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "lp{3.5cm}p{3.1cm}ccccc", cab,
        ("Corrida entre exposições rivais",
         r"Corrida entre exposições rivais no desenho \emph{shift-share}."),
        "tab:horserace", nota, tam="footnotesize")


# ---------------------------------------------------------------------------
# A.4 --- Grade confirmatória e escrita do arquivo
# ---------------------------------------------------------------------------

CONF_TEXTO = r"""
\subsection{A grade confirmatória completa}

A Tabela~\ref{tab:confirmatorio} traz \emph{todas} as combinações de exposição,
desfecho e defasagem que a grade confirmatória rodou, e não apenas as
comentadas no Capítulo~\ref{cap:resultados}. A distinção entre grade
confirmatória e exploratória foi fixada antes da estimação, e o controle de
multiplicidade descrito na Seção~\ref{sec:met-instrumental} incide sobre a
segunda. Os desfechos de área --- pastagem e agricultura --- são nulos, e isso
consta aqui com o mesmo destaque dos demais.
"""


def secao_confirmatorio() -> str:
    d = pd.read_csv(PROC / "drive_amc_apt_confirmatorio.csv")
    linhas = []
    for _, r in d.iterrows():
        linhas.append(" & ".join([
            esc(r["exposicao_rotulo"]), esc(r["desfecho_rotulo"]).replace("Δ", r"$\Delta$ "),
            str(int(r["lag"])), esc(r["sinal_esperado"]),
            num(r["beta"], 4, mais=True), num(r["se"], 4), p_val(r["p"]),
            num(r["r2_within"], 5),
        ]) + r" \\")
    cab = (r"\textbf{Exposição} & \textbf{Desfecho} & \textbf{Def.} & \textbf{Sinal} & "
           r"\textbf{$\hat{\gamma}$} & \textbf{EP} & \textbf{$p$} & \textbf{$R^2_w$} \\")
    n_amc = int(d["n_amc"].iloc[0])
    nota = (r"\emph{shifter}: variação padronizada do índice de taxa de câmbio efetiva "
            r"real. ``Def.'' é a defasagem em anos do \emph{shifter}; ``Sinal'' é a "
            r"direção prevista antes da estimação. Efeitos fixos de unidade e de ano; "
            r"erros-padrão agrupados nas duas dimensões; " + str(n_amc) + r" unidades. "
            r"O $p$ desta tabela é o do erro-padrão agrupado, que a "
            r"Seção~\ref{sec:met-instrumental} mostra ser otimista neste desenho, porque "
            r"trata cada ano como realização independente do choque quando as realizações "
            r"efetivas são cerca de 38. A régua de permutação não foi computada para estas "
            r"linhas: ela existe para a especificação confirmatória do rebanho, na "
            r"Tabela~\ref{tab:horserace}, cujas regressões são outras. Nas dez linhas em "
            r"que as duas foram computadas lado a lado, o $p$ agrupado saiu \emph{menor} "
            r"que o de permutação em oito --- e em duas, maior. É regularidade observada, "
            r"e não garantia matemática de que o agrupado limite o outro por baixo; "
            r"chamá-lo de ``piso da incerteza'' seria dizer mais do que se mediu, e o "
            r"$p$-valor não é, de todo modo, uma medida de incerteza. Nenhum $p$ desta "
            r"tabela é lido como significância no corpo do texto.")
    return CONF_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "p{3.2cm}p{1.9cm}cccccc", cab,
        (r"Grade confirmatória do \emph{drive} comum",
         r"Grade confirmatória completa do desenho \emph{shift-share}."),
        "tab:confirmatorio", nota)


def main() -> None:
    partes = [PREAMBULO, secao_precedencia(), secao_slx(), secao_sarsem(),
              secao_shiftshare(), secao_placebos(), secao_confirmatorio(),
              secao_oferta(), secao_ifdm()]
    # Barreira de flutuante ao fim de cada bloco. Sem ela o LaTeX empurra as tabelas
    # grandes para as paginas seguintes e elas saem DEPOIS da secao seguinte ter
    # comecado -- a A.6 abria antes de as proprias tabelas aparecerem. A barreira
    # prende cada tabela ao bloco a que pertence.
    barreira = chr(10) + chr(10) + BR + "FloatBarrier" + chr(10)
    SAIDA.write_text(barreira.join(partes) + chr(10), encoding="utf-8")
    n = len(SAIDA.read_text(encoding="utf-8").splitlines())
    print(f"[ok] {SAIDA.relative_to(RAIZ)} — {n} linhas")




# ---------------------------------------------------------------------------
# A.2 --- Precedência temporal (#34/#42)
# ---------------------------------------------------------------------------

TEMPO_TEXTO = r"""
\section{Precedência temporal entre as séries regionais}
\label{ap:precedencia}

Antes do teste espacial, a hipótese do empurrão foi examinada no tempo: se a
lavoura do Sul puxa a pastagem do Norte, o passado de uma deve ajudar a prever
a outra. Este bloco \emph{não} usa o painel de AMCs e não segue as convenções
da Seção~\ref{ap:convencoes}: ele corre sobre \textbf{séries anuais agregadas
por região}, o que dá cerca de 38 observações --- e é dessa escassez, e não do
desenho, que vem a maior parte da limitação de poder.

A leitura do teste de Granger tem de ser literal: ele mede \emph{precedência
preditiva}, não causalidade. E, aplicado a séries integradas, fabrica
precedência inexistente --- foi o que a decisão D16 registrou. O diagnóstico
que sustenta essa decisão vem em dois passos, e as duas tabelas seguintes os
separam porque \textbf{não são o mesmo teste}.

O primeiro passo é a classificação das ordens de integração, por confronto
entre os testes de Dickey-Fuller aumentado (ADF) e de
Kwiatkowski-Phillips-Schmidt-Shin (KPSS), cujas hipóteses nulas são opostas. O
veredito registrado é o do ADF, e a nota da tabela diz onde o KPSS o acompanha
e onde não. A Tabela~\ref{tab:integracao} traz as duas séries em nível, em
primeira e em segunda diferença. É ela que mostra o descasamento: a agricultura
do Sul é estacionária já em nível pelo ADF, enquanto a pastagem do Norte não o
é nem depois de convertida em variações anuais --- a montagem clássica que
fabrica precedência. A pastagem só perde a raiz unitária na \emph{segunda}
diferença, e é essa linha, e não uma suposição, que fixa \(d_{\max} = 2\) no
teste do passo seguinte.

O segundo passo é a inferência válida sob integração. A
Tabela~\ref{tab:precedencia} reporta três colunas de \(p\), e a distinção entre
elas é a correção que esta versão do apêndice faz. O \(p\) de Granger é o
teste-F clássico. O \(p\) de Wald HAC é o mesmo teste em primeira diferença,
com covariância robusta a heterocedasticidade e autocorrelação (Newey-West com
duas defasagens, o mesmo número que aumenta o modelo de Toda-Yamamoto): ele
corrige o \emph{erro-padrão}, e não a integração, de modo que \textbf{não}
resolve o problema diagnosticado acima. Quem o resolve é a terceira coluna, o \(p\) de
Toda-Yamamoto \cite{TodaYamamoto1995}, que ajusta o modelo vetorial
autorregressivo em \emph{níveis} com \(p + d_{\max}\) defasagens e aplica o
teste de Wald apenas às \(p\) primeiras. É esse o número que o
Capítulo~\ref{cap:resultados} usa para o veredito, e é ele que apaga o
resultado nas duas direções.

A direção \emph{reversa} está na tabela de propósito. Ela é o achado que a
decisão D16 classificou como \textbf{artefato espúrio}: o sinal forte que
aparece de norte para sul --- \(p < 0{,}001\) nas duas primeiras colunas ---
não sobrevive à terceira, e é reportado aqui para que o leitor veja o que o
diagnóstico teve de descartar. O contraste entre as colunas é, ele próprio, a
evidência: uma régua que corrige o erro-padrão mantém o achado; a que corrige a
integração o dissolve.
"""


def secao_precedencia() -> str:
    est = pd.read_csv(PROC / "granger_reverso_estacionaria.csv")

    # --- passo 1: ordens de integração (ADF x KPSS) ---
    ordens = est[est.bloco == "estacionariedade"]
    rot_serie = {
        "agric_Sul (nível)":  "Agricultura do Sul, em nível",
        "pasto_Norte (nível)": "Pastagem do Norte, em nível",
        "Δagric_Sul":          r"Agricultura do Sul, em 1\textsuperscript{a} diferença",
        "Δpasto_Norte":        r"Pastagem do Norte, em 1\textsuperscript{a} diferença",
        "ΔΔagric_Sul":         r"Agricultura do Sul, em 2\textsuperscript{a} diferença",
        "ΔΔpasto_Norte":       r"Pastagem do Norte, em 2\textsuperscript{a} diferença",
    }
    lin_i = []
    for _, r in ordens.iterrows():
        # As nulas sao opostas: ADF rejeita = estacionaria; KPSS rejeita = NAO estacionaria.
        veredito = ("estacionária" if bool(r["estacionaria_adf"]) else "não estacionária")
        lin_i.append(" & ".join([
            rot_serie.get(str(r["serie"]), esc(r["serie"])), n_obs(r["n"]),
            p_val(r["adf_p"]), p_val(r["kpss_p"]), veredito,
        ]) + r" \\")
    t_int = tabela(
        lin_i, "lrccl",
        (r"\textbf{Série} & \textbf{$n$} & \textbf{$p$ ADF} & \textbf{$p$ KPSS} & "
         r"\textbf{Veredito (ADF)} \\"),
        ("Ordens de integração das séries regionais",
         "Testes de raiz unitária nas séries regionais, em nível, em primeira e em "
         "segunda diferença."),
        "tab:integracao",
        # A versao anterior desta nota chamava de "discordancia" o que era ACORDO: onde o
        # ADF nao rejeita a raiz unitaria e o KPSS rejeita a estacionariedade, os dois
        # dizem a MESMA coisa. Corrigida, a nota passa a sustentar o argumento em vez de
        # o enfraquecer -- as duas reguas concordam justamente na serie de onde vem o
        # diagnostico, e voltam a concordar na 2a diferenca, que e o que fixa dmax=2.
        (r"as hipóteses nulas dos dois testes são \textbf{opostas}: o ADF tem por nula a "
         r"presença de raiz unitária, de modo que $p$ baixo indica série estacionária; o "
         r"KPSS tem por nula a estacionariedade, de modo que $p$ baixo indica o contrário. "
         r"A última coluna traz o veredito do ADF, que é a régua com que $d_{\max}$ foi "
         r"fixado. Os dois testes \textbf{concordam} nas duas linhas da pastagem do Norte "
         r"--- ambos a dão não estacionária em nível e em primeira diferença ---, e é dela "
         r"que vem o diagnóstico; \textbf{divergem} nas duas linhas da agricultura do Sul, "
         r"que o ADF dá estacionária e o KPSS não; e \textbf{voltam a concordar} nas duas "
         r"segundas diferenças, estacionárias pelas duas réguas. São estas as linhas que "
         r"sustentam $d_{\max} = 2$: sem elas a ordem de integração da pastagem ficaria "
         r"afirmada e não mostrada. O $p$ do KPSS é truncado na tabela de valores críticos "
         r"da rotina, de modo que $0{,}010$ e $0{,}100$ são limites e se leem como "
         r"``$\leq$'' e ``$\geq$''. Com 40 observações e duas quebras estimadas nessas "
         r"mesmas séries, nenhum dos dois testes é decisivo sozinho, e a classificação vale "
         r"como \emph{a resposta do teste} nesta amostra, e não como propriedade "
         r"estabelecida do processo. O que a tabela estabelece com segurança é o "
         r"\emph{descasamento} entre as duas séries em nível e em primeira diferença, que "
         r"é o que invalida o teste clássico."),
        tam="footnotesize")

    # --- passo 2: precedencia, com a coluna de Toda-Yamamoto ---
    d = pd.read_csv(PROC / "granger_reverso_lags.csv")
    # O TY roda sobre o par de series, nao sobre a direcao "bov": a chave e o prefixo
    # da relacao antes dos dois-pontos ("Sul->Norte", "REVERSO") mais o numero de lags.
    ty = est[est.bloco == "toda_yamamoto"]
    mapa_ty = {(str(r["relacao"]), int(r["p"])): r["ty_p"] for _, r in ty.iterrows()}

    linhas = []
    atual = None
    for _, r in d.iterrows():
        rel = str(r["relacao"])
        if rel != atual:
            atual = rel
            linhas.append(r"\multicolumn{8}{l}{\textit{" + esc(rel) + r"}} \\")
        chave = (rel.split(":")[0].strip(), int(r["lag"]))
        linhas.append(" & ".join([
            "", str(int(r["lag"])), p_val(r["granger_p_classico"]), p_val(r["wald_p_HAC"]),
            p_val(mapa_ty[chave]) if chave in mapa_ty else "---",
            num(r["b1"], 4, mais=True), p_val(r["b1_p_HAC"]), n_obs(r["n"]),
        ]) + r" \\")
    cab = (r"& \textbf{Def.} & \textbf{$p$ Granger} & \textbf{$p$ Wald HAC} & "
           r"\textbf{$p$ T-Y} & \textbf{$\hat{\beta}_1$} & \textbf{$p(\hat{\beta}_1)$} & "
           r"\textbf{$n$} \\")
    nota = (r"séries anuais agregadas por região; ``Def.'' é o número de defasagens do "
            r"modelo. As três colunas de $p$ \textbf{não são a mesma régua}. $p$ Granger é "
            r"o teste-F clássico em primeira diferença. $p$ Wald HAC é o mesmo teste com "
            r"covariância robusta a heterocedasticidade e autocorrelação (Newey-West com "
            r"duas defasagens): "
            r"corrige o erro-padrão, não a integração. $p$ T-Y é o de Toda-Yamamoto, "
            r"ajustado em \emph{níveis} com $p + d_{\max}$ defasagens ($d_{\max} = 2$) e "
            r"com o teste de Wald restrito às $p$ primeiras --- é a única das três válida "
            r"sob integração, e é a reportada no Capítulo~\ref{cap:resultados}. Ela consta "
            r"apenas do par agricultura--pastagem, que é onde o resultado espúrio "
            r"apareceu e onde o diagnóstico foi conduzido; nos dois blocos "
            r"\textsc{bov} não foi computada, e as linhas trazem ``---'' em vez de "
            r"repetir a coluna vizinha. $\hat{\beta}_1$ é o coeficiente da primeira "
            r"defasagem da série candidata a precedente, na equação em diferenças. O bloco "
            r"\textsc{reverso} é reportado porque foi ele que originou a decisão D16, e "
            r"não porque sustente afirmação.")
    t_prec = tabela(
        linhas, "lccccccr", cab,
        ("Precedência temporal entre séries regionais",
         "Precedência temporal entre as séries regionais, por defasagem e por régua de inferência."),
        "tab:precedencia", nota, tam="footnotesize")
    return TEMPO_TEXTO + chr(10) + chr(10) + t_int + chr(10) + chr(10) + t_prec


# ---------------------------------------------------------------------------
# A.4 --- Dependência espacial: SAR e SEM (#22/#49)
# ---------------------------------------------------------------------------

SARSEM_TEXTO = r"""
\section{Dependência espacial: modelos de defasagem e de erro}
\label{ap:sarsem}

As unidades vizinhas não são independentes, e ignorá-lo estreita a barra de
erro. Três modelos de painel foram, por isso, reestimados em três formas: por
mínimos quadrados com efeitos fixos; com defasagem espacial da \emph{variável
dependente} (SAR); e com dependência no \emph{termo de erro} (SEM). A
comparação responde a uma pergunta só --- se os coeficientes de interesse
sobrevivem quando a dependência é modelada --- e a resposta consta na última
coluna da Tabela~\ref{tab:sarsem}.

Partindo da especificação por mínimos quadrados, em primeira diferença e com
os dois efeitos fixos,
\begin{equation}
\Delta y_{it} = \Delta \mathbf{x}_{it}'\boldsymbol{\beta}
             + \alpha_i + \lambda_t + \varepsilon_{it},
\label{eq:mq}
\end{equation}
\noindent as duas formas espaciais acrescentam um termo cada. O SAR põe a
dependência na variável dependente,
\begin{equation}
\Delta y_{it} = \rho\,(W\Delta y)_{it} + \Delta \mathbf{x}_{it}'\boldsymbol{\beta}
             + \alpha_i + \lambda_t + \varepsilon_{it},
\label{eq:sar}
\end{equation}
\noindent e o SEM a põe no erro, deixando a equação de média intacta:
\begin{equation}
\Delta y_{it} = \Delta \mathbf{x}_{it}'\boldsymbol{\beta} + \alpha_i + \lambda_t + u_{it},
\qquad u_{it} = \lambda\,(Wu)_{it} + \varepsilon_{it}.
\label{eq:sem}
\end{equation}

\noindent A distinção importa para a leitura. Sob o SAR, o efeito de um choque
numa unidade transborda para as vizinhas e volta, de modo que
\(\boldsymbol{\beta}\) deixa de ser o efeito total; sob o SEM, \(\boldsymbol{\beta}\)
continua interpretável e o que muda é a eficiência da estimativa. Os
coeficientes das duas colunas espaciais da tabela \textbf{não são, portanto,
diretamente comparáveis} ao de mínimos quadrados --- e o que a tabela pergunta
não é se eles coincidem, e sim se o sinal e a significância resistem.

A matriz \(W\) é, na maioria das linhas, de contiguidade \emph{queen} entre as
166 unidades, padronizada por linha --- e não a matriz direcional de oito
vizinhos da Seção~\ref{ap:slx}, porque aqui o objeto é a dependência genérica,
e não a direção sul-norte. O modelo M3 é estimado \emph{duas vezes}, uma com
cada matriz, e as duas linhas constam da tabela: é o teste de sensibilidade da
escolha de \(W\). A coluna \(W\) identifica qual foi usada em cada linha. Os
testes do multiplicador de Lagrange, em suas versões simples e robusta, indicam
qual das duas formas de dependência o dado prefere.

\textbf{Os três modelos.} A Tabela~\ref{tab:sarsem} reporta apenas o
coeficiente de interesse de cada um, e não a regressão inteira; os regressores
completos são estes.

\begin{description}
\item[M1 --- intensificação.] Desfecho \(\Delta\)agricultura; regressor de
interesse \(\Delta\) valor adicionado agropecuário real. Um \(\beta\) negativo
indica que o valor adicionado cresce sem acompanhar a área \emph{dentro} da
unidade, que é a assinatura de intensificação discutida na
Seção~\ref{sec:res-perna2}.
\item[M2 --- crédito para pastagem.] Desfecho \(\Delta\)pastagem; regressor de
interesse \(\Delta\) crédito rural do SICOR, com \(\Delta\) valor adicionado
agropecuário como controle na mesma regressão. A janela é a do SICOR, que
começa em 2013, e é a razão de o \(n\) desta linha ser o menor da tabela.
\item[M3 --- substituição local.] Desfecho \(\Delta\)pastagem; regressor de
interesse \(\Delta\)agricultura, sem controles. Mede troca de uso \emph{dentro}
da unidade --- e não deslocamento, que é objeto da Seção~\ref{ap:slx}.
\end{description}

O erro-padrão da tabela é o da estimação por mínimos quadrados, que é a
referência contra a qual as outras duas colunas são lidas; o \(p\) é reportado
para as três, de modo que a coluna ``Sobrev.'' possa ser conferida na própria
linha, e não aceita sob palavra.
"""


def secao_sarsem() -> str:
    d = pd.read_csv(PROC / "painel_espacial_dinamico.csv")
    rot_w = {"queen": r"\emph{queen}", "knn8": "8 viz."}
    rot_forma = {"lag": "SAR", "error": "SEM"}
    linhas = []
    for _, r in d.iterrows():
        linhas.append(" & ".join([
            esc(r["modelo"]),
            rot_w.get(str(r["W"]), esc(r["W"])), n_obs(r["n_obs"]),
            num(r["beta_ols"], 4, mais=True), num(r["se_ols"], 4), p_val(r["p_ols"]),
            num(r["beta_lag"], 4, mais=True), p_val(r["p_lag"]),
            num(r["beta_err"], 4, mais=True), p_val(r["p_err"]),
            num(r["rho"], 3), num(r["lam"], 3),
            rot_forma.get(str(r["forma_preferida"]), esc(r["forma_preferida"])),
            "sim" if bool(r["sobrevive"]) else r"\textbf{não}",
        ]) + r" \\")
    cab = (r"\textbf{Modelo} & \textbf{$W$} & \textbf{$n$} & "
           r"\textbf{$\hat{\beta}_{MQ}$} & \textbf{EP} & \textbf{$p$} & "
           r"\textbf{$\hat{\beta}_{SAR}$} & \textbf{$p$} & "
           r"\textbf{$\hat{\beta}_{SEM}$} & \textbf{$p$} & "
           r"\textbf{$\hat{\rho}$} & \textbf{$\hat{\lambda}$} & \textbf{Forma} & "
           r"\textbf{Sobrev.} \\")
    n = int(d["N"].iloc[0])
    # A nota NAO pode afirmar "atenua-se" a mao. A versao anterior dizia "nas quatro
    # linhas o coeficiente atenua-se" e ja era falsa: o SEM do M3 com 8 vizinhos CRESCE
    # 0,6% em magnitude. Frase de tabela e afirmacao, e afirmacao digitada envelhece --
    # a faixa passa a ser lida do proprio CSV a cada regeneracao.
    razoes = [abs(r[c]) / abs(r["beta_ols"]) - 1.0
              for _, r in d.iterrows() for c in ("beta_lag", "beta_err")]
    n_atenua = sum(1 for v in razoes if v < 0)
    n_esp = len(razoes)
    p_max_esp = max(max(r["p_lag"], r["p_err"]) for _, r in d.iterrows())

    def pct(v):
        return f"{abs(v) * 100:.1f}".replace(".", "{,}") + BR + "%"

    # O maior p espacial e' da ordem de 1e-10; `p_val` o achataria em "<0,001" e a nota
    # ficaria dizendo "abaixo de <0,001". Abaixo do piso da tabela, reporta-se a ordem.
    if p_max_esp < 0.001:
        exp = f"{p_max_esp:.0e}".split("e")[1]
        sig_esp = (r"o maior $p$ entre as oito estimativas espaciais é da ordem de "
                   r"$10^{" + str(int(exp)) + r"}$")
    else:
        sig_esp = (r"o maior $p$ entre as oito estimativas espaciais é " +
                   p_val(p_max_esp))

    # Numeral por extenso: e' prosa de nota de rodape, nao celula de tabela.
    ext = {1: "uma", 2: "duas", 3: "três", 4: "quatro", 5: "cinco", 6: "seis",
           7: "sete", 8: "oito", 9: "nove", 10: "dez"}
    def nome_n(v):
        return ext.get(v, str(v))

    n_cresce = n_esp - n_atenua
    if n_cresce == 0:
        faixa = (r"as " + nome_n(n_esp) + r" estimativas espaciais atenuam-se em relação "
                 r"aos mínimos quadrados, no máximo " + pct(min(razoes)) + ".")
    else:
        faixa = (nome_n(n_atenua) + r" das " + nome_n(n_esp) + r" estimativas espaciais "
                 r"atenuam-se em relação aos mínimos quadrados, no máximo " +
                 pct(min(razoes)) + r"; " +
                 (r"a restante cresce " if n_cresce == 1
                  else nome_n(n_cresce) + r" crescem em magnitude, no máximo ") +
                 pct(max(razoes)) + r" em magnitude.")
    nota = (r"todas as especificações correm sobre as " + str(n) + r" unidades, em "
            r"primeira diferença e com efeitos fixos de unidade e de ano; $n$ é o total de "
            r"células após exclusão de ausentes, e varia porque as fontes dos regressores "
            r"cobrem janelas diferentes (o SICOR do M2 começa em 2013). $W$ identifica a "
            r"matriz de pesos: \emph{queen} é a de "
            r"contiguidade, ``8 viz.'' a dos oito vizinhos mais próximos --- o M3 é "
            r"estimado com as duas, para medir quanto a escolha de $W$ move o resultado. "
            r"O erro-padrão é o da estimação por mínimos quadrados; cada uma das três "
            r"estimações traz o seu próprio $p$. $\hat{\rho}$ "
            r"é o parâmetro de defasagem espacial do SAR e $\hat{\lambda}$ o de dependência "
            r"do erro no SEM. ``Forma'' é a preferida pelos testes do multiplicador de "
            r"Lagrange em versão robusta, nomeada pela forma que ela indica (SAR para "
            r"defasagem, SEM para erro). ``Sobrev.'' indica se o sinal e a significância "
            r"do coeficiente de interesse resistem à modelagem da dependência. As "
            r"magnitudes ficam \textbf{estáveis}: " + faixa + r" Nenhuma troca de sinal, e "
            r"nenhuma perda de significância: " + sig_esp + r".")
    return SARSEM_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "lcrcccccccccll", cab,
        ("Dependência espacial nos três modelos de painel",
         "Coeficientes de interesse sob mínimos quadrados, SAR e SEM, nas duas matrizes de peso."),
        "tab:sarsem", nota, tam="scriptsize", colsep=3)


# ---------------------------------------------------------------------------
# A.6 --- Placebos do drive comum (#54)
# ---------------------------------------------------------------------------

PLACEBO_TEXTO = r"""
\subsection{A bateria de placebos}

O que sustenta a leitura da Seção~\ref{ap:shiftshare} não é a magnitude do
coeficiente, e sim a \emph{especificidade}: cada teste que deveria sair vazio
sai vazio. A Tabela~\ref{tab:placebos} traz a bateria inteira. Os placebos de
\emph{desfecho} trocam a variável dependente por outra que o câmbio não deveria
mover pela via testada --- área urbana e água; os de \emph{tempo} adiantam o
\emph{shifter} em um e dois anos, de modo que o efeito precederia a causa.

Convém dizer o que a bateria \emph{não} faz, porque é a ressalva que a
Seção~\ref{ap:shiftshare} desenvolve: todos estes são placebos de desfecho e de
tempo, e nenhum pergunta se a \emph{exposição} escolhida é a certa. Essa
pergunta é a da corrida entre exposições, e a resposta dela reduz o alcance da
frente.
"""


def secao_placebos() -> str:
    d = pd.read_csv(PROC / "perna4_placebos.csv")
    linhas = []
    atual = None
    for _, r in d.iterrows():
        h = str(r["headline"])
        if h != atual:
            atual = h
            linhas.append(r"\multicolumn{8}{l}{\textit{" + esc(h) + r"}} \\")
        tipo = "desfecho" if "desfecho" in str(r["tipo"]) else "tempo"
        # Nos placebos de TEMPO a coluna `placebo` do CSV vem vazia: o que muda nao e o
        # desfecho e sim a defasagem, e o rotulo tem de ser montado a partir de `lead`.
        if pd.notna(r["placebo"]):
            rot = esc(r["placebo"])
        else:
            k = int(r["lead"])
            por_extenso = {1: "um ano", 2: "dois anos", 3: "três anos"}
            rot = r"\emph{Shifter} adiantado " + por_extenso.get(k, f"{k} anos")
        linhas.append(" & ".join([
            "", rot, tipo,
            num(r["beta"], 4, mais=True), num(r["se"], 4), p_val(r["p"]),
            num(r["r2_within"], 5), n_obs(r["n_obs"]),
        ]) + r" \\")
    cab = (r"& \textbf{Placebo} & \textbf{Tipo} & \textbf{$\hat{\gamma}$} & "
           r"\textbf{EP} & \textbf{$p$} & \textbf{$R^2_w$} & \textbf{$n$} \\")
    n_amc = int(d["n_amc"].iloc[0])
    nota = (r"mesma equação da Seção~\ref{ap:shiftshare}, com o desfecho ou a defasagem "
            r"trocados; " + str(n_amc) + r" unidades em todas as linhas, com efeitos "
            r"fixos de unidade e de ano e erros-padrão agrupados nas duas dimensões. O $n$ "
            r"é reportado por linha porque \textbf{não é o mesmo}: adiantar o "
            r"\emph{shifter} em dois anos custa um ano de painel, e as duas linhas "
            r"correspondentes caem para 6.142 células. Um placebo cumpre o seu papel "
            r"quando \textbf{não} rejeita: aqui nenhum dos oito o faz. Os que chegam mais "
            r"perto são os dois placebos de tempo da exposição de fronteira, com $p$ de "
            r"$0{,}062$ e $0{,}070$, e convém dizer por que não são inquietantes: o sinal "
            r"deles é \emph{negativo}, isto é, o oposto do que a hipótese prevê para essa "
            r"exposição. Um placebo que quase rejeita na direção contrária à hipótese não "
            r"a socorre.")
    return PLACEBO_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "lp{4.0cm}lccccr", cab,
        ("Placebos de desfecho e de tempo",
         r"Bateria de placebos de desfecho e de tempo do desenho \emph{shift-share}."),
        "tab:placebos", nota, tam="footnotesize")


# ---------------------------------------------------------------------------
# A.7 --- Teto de oferta (#39 / #39B)
# ---------------------------------------------------------------------------

OFERTA_TEXTO = r"""
\section{Teto de oferta: disponibilidade e depleção}
\label{ap:oferta}

A frente do teto de oferta separa duas afirmações que o mesmo painel testa. A
primeira é de \emph{nível}: o fluxo de conversão escala com o estoque ainda
disponível. A segunda é de \emph{comportamento}: a taxa de conversão cai à
medida que a unidade se deplete --- e é essa que distingue esgotamento de mera
aritmética, porque um fluxo proporcional ao estoque cairia sozinho sem que a
taxa mudasse.

As duas são a mesma equação com desfecho e regressor trocados, ambas em painel
com os dois efeitos fixos:
\begin{equation}
\text{fluxo}_{it} = \beta\,\text{estoque}_{i,t-1}
                  + \alpha_i + \lambda_t + \varepsilon_{it},
\label{eq:b1}
\end{equation}
\begin{equation}
\text{taxa}_{it} = \beta\,\text{depleção}_{i,t-1}
                 + \alpha_i + \lambda_t + \varepsilon_{it}.
\label{eq:b2b}
\end{equation}

\noindent Estoque e depleção entram \textbf{em nível}, e não em logaritmo ---
registre-se porque as colunas correspondentes do repositório trazem um prefixo
\texttt{l} que sugere o contrário, e quem reconstruir o modelo aplicando
logaritmo não reproduzirá estes coeficientes. A depleção é a fração
\(1 - \text{estoque}_t/\text{estoque}_{1985}\) e o estoque é medido em hectares.
A taxa é \(\text{fluxo}_{it}/\text{estoque}_{i,t-1}\), de modo que a
Equação~\ref{eq:b1} carrega a identidade \(\text{fluxo} \equiv \text{taxa}
\times \text{estoque}\) e não pode surpreender; é a Equação~\ref{eq:b2b} que
tem conteúdo empírico. Regressor e desfecho entram em \emph{escore-z}, e por
isso cada célula reporta também o efeito em unidade natural.

A segunda afirmação é a que a decisão D29 reabriu. A variável de depleção,
construída como \(1 - \text{estoque}_t/\text{estoque}_{1985}\), sai do intervalo
\([0,1]\) em cerca de 14\% do painel, nas unidades que \emph{ganharam} estoque.
Padronizar uma variável com domínio violado dilui o sinal, e o nulo publicado
era artefato disso. A Tabela~\ref{tab:deplecao} traz a grade inteira de
tratamentos dessa variável, com e sem ponderação pelo tamanho do estoque, em
duas amostras --- e não apenas a combinação adotada.

\textbf{Como ler as duas tabelas juntas.} A linha \texttt{B2b} da
Tabela~\ref{tab:disponibilidade} é a especificação \emph{publicada antes} da
D29, e o seu nulo (\(p = 0{,}481\)) é o artefato: ela está ali porque a tabela
reproduz o bloco do Pipeline~\#39 como ele saiu, e não porque sustente
afirmação. A Tabela~\ref{tab:deplecao} é a que a substitui, e a primeira linha
dela é a mesma estimativa, agora no seu lugar --- a célula ``sem tratamento'',
sem peso, na amostra completa.

\textbf{Três limites da grade, que o veredito não dissolve.} O primeiro é que o
tratamento por \emph{domínio} descarta 46 unidades, e elas não são
desprezíveis: detêm 17,3\% do estoque convertível de 2024. Para a regressão a
exclusão é correta --- nessas unidades a depleção é indefinida, e não extrema ---,
mas quem for somar hectares não deve herdá-la. É por isso que a grade traz
também o tratamento de \emph{piso em zero}, que não descarta ninguém e dá o
mesmo veredito. O segundo é que esse piso, por sua vez, cria um acúmulo
artificial de observações exatamente em zero, o que é um defeito de forma
distinto; os dois tratamentos têm defeitos diferentes e concordam, e é a
concordância que carrega a leitura, não qualquer um deles isolado. O terceiro é
que nenhum dos quatro conserta a \emph{razão} de as 46 existirem, que é a
oscilação do classificador na borda entre pastagem e savana, discutida na
Seção~\ref{sec:met-decisoes}.

\textbf{Sobre multiplicidade.} As dezesseis células são dezesseis leituras da
\emph{mesma} hipótese, pré-declarada no Pipeline~\#39 antes da estimação, e não
uma família de hipóteses distintas. O controle de falsas descobertas da
Seção~\ref{sec:met-instrumental} incide sobre grades exploratórias, que
perguntam coisas diferentes; aplicá-lo a uma grade de robustez, que pergunta a
mesma coisa de quatro maneiras, puniria a checagem em vez da pescaria. O que
esta grade oferece no lugar é a concordância entre tratamentos com defeitos
independentes.
"""


def secao_oferta() -> str:
    b1 = pd.read_csv(PROC / "fronteira_teste_supply.csv")
    linhas = []
    for _, r in b1.iterrows():
        linhas.append(" & ".join([
            esc(r["spec"]), reg(r["regressor"]),
            num(r["beta"], 3, mais=True), num(r["se"], 3), p_val(r["p"]),
            num(r["r2_within"], 3), f'{int(r["n_obs"]):,}'.replace(",", "."),
        ]) + r" \\")
    t1 = tabela(linhas, "p{4.0cm}p{2.6cm}ccccr",
                (r"\textbf{Especificação} & \textbf{Regressor} & \textbf{$\hat{\beta}$} & "
                 r"\textbf{EP} & \textbf{$p$} & \textbf{$R^2_w$} & \textbf{$n$} \\"),
                ("Canal de disponibilidade", "O canal de disponibilidade: fluxo de conversão contra estoque."),
                "tab:disponibilidade",
                (r"desfecho: fluxo anual de conversão, exceto nas linhas \texttt{B2a} e "
                 r"\texttt{B2b}, cujo desfecho é a \emph{taxa}. Erros-padrão agrupados nas "
                 r"duas dimensões; regressores em \emph{escore-z}. Efeitos fixos de unidade "
                 r"e de ano em todas as linhas \textbf{menos} as do \texttt{B3}, que "
                 r"dispensa o de ano de propósito: os sinais de demanda que ele testa "
                 r"(câmbio, preço, crédito) são nacionais e um efeito fixo de ano os "
                 r"absorveria por inteiro, deixando o coeficiente sem identificação. Esse é "
                 r"também o motivo de os $p$ do \texttt{B3} não serem lidos como o das "
                 r"demais linhas. A linha \texttt{B2b} é a especificação que a decisão D29 "
                 r"superou; ver a Tabela~\ref{tab:deplecao}."),
                tam="footnotesize")

    d2 = pd.read_csv(PROC / "fronteira_teste_supply_39b.csv")
    # `termo == "principal"` NAO basta: o CSV do #39B carrega tambem as linhas B1/B1q/B2a,
    # que sao do canal de disponibilidade (ja impressas na t1 acima) e nao tratamentos da
    # depleçao. Sem o filtro por `tratamento` elas entram aqui com a descriçao vazia --
    # o defeito que a leitura externa de 20/ago viu como "nan" e que era, na verdade,
    # duplicaçao de tabela. A chave da grade e (spec B2b, tratamento preenchido).
    d2 = d2[(d2.termo == "principal") & (d2.spec == "B2b") & d2.tratamento.notna()]
    linhas2 = []
    for _, r in d2.iterrows():
        peso = "estoque" if isinstance(r["peso"], str) else "---"
        linhas2.append(" & ".join([
            esc(r["descricao"]), esc(r["amostra"]), peso,
            num(r["beta_z"], 3, mais=True),
            num(100 * r["beta_por_01_deplecao"], 3, mais=True),
            p_val(r["p_entidade"]), p_val(r["p_entidade_ano"]),
            num(r["r2_within"], 4), n_obs(r["n_obs"]),
        ]) + r" \\")
    t2 = tabela(linhas2, "p{3.6cm}llcccccr",
                (r"\textbf{Tratamento da depleção} & \textbf{Amostra} & \textbf{Peso} & "
                 r"\textbf{$\hat{\beta}_z$} & \textbf{p.p./0,1} & \textbf{$p_{ent}$} & "
                 r"\textbf{$p_{ent+ano}$} & \textbf{$R^2_w$} & \textbf{$n$} \\"),
                ("Grade de tratamentos da variável de depleção",
                 "Grade completa de tratamentos da variável de depleção (decisão D29)."),
                "tab:deplecao",
                (r"desfecho: taxa anual de conversão; todas as dezesseis linhas são a "
                 r"especificação \texttt{B2b}, com efeitos fixos de unidade e de ano. "
                 r"$p_{ent}$ agrupa por unidade e $p_{ent+ano}$ nas duas dimensões, que é "
                 r"a régua adotada no teste de origem e a reportada no corpo do texto. "
                 r"``Peso'' indica ponderação pelo tamanho do estoque. As duas colunas de "
                 r"efeito \textbf{não são a mesma medida}: $\hat{\beta}_z$ está em "
                 r"\emph{escore-z} e \textbf{não é comparável entre tratamentos}, porque o "
                 r"desvio-padrão do regressor vai de $0{,}21$ no domínio a $3{,}54$ sem "
                 r"tratamento --- dezessete vezes; ``p.p./0,1'' é o mesmo efeito em "
                 r"unidade natural, pontos percentuais de taxa anual por décimo de "
                 r"depleção, e é essa a coluna em que os tratamentos podem ser comparados "
                 r"e em que se lê a convergência para $-0{,}5$ a $-0{,}8$. O $n$ varia "
                 r"porque \emph{domínio} descarta as unidades fora de $[0,1]$ e "
                 r"\texttt{corte1k} as de estoque abaixo de mil hectares. A linha ``sem "
                 r"tratamento'' é a especificação publicada antes da D29, e o nulo dela é "
                 r"o artefato que a decisão corrigiu."),
                tam="scriptsize")
    return OFERTA_TEXTO + chr(10) + chr(10) + t1 + chr(10) + chr(10) + t2


# ---------------------------------------------------------------------------
# A.8 --- Desenvolvimento municipal (#41)
# ---------------------------------------------------------------------------

IFDM_TEXTO = r"""
\section{Desenvolvimento municipal e o gradiente}
\label{ap:ifdm}

A última conta do Capítulo~\ref{cap:resultados} pergunta se a expansão da área
cultivada comprou desenvolvimento. Ela tem dois blocos, e os dois são
\textbf{associativos}: nenhum identifica efeito causal.

Esta seção é a segunda que \emph{não} segue as convenções da
Seção~\ref{ap:convencoes}, e convém dizer em quê antes das tabelas. A unidade
não é a AMC e sim o \textbf{município} (246 em Goiás). O primeiro bloco não está
em primeira diferença: é uma seção transversal em \emph{nível}, sem efeitos
fixos, e o que nele se padroniza é a latitude, não uma exposição. E o painel do
segundo bloco agrupa os erros-padrão \textbf{apenas por município}, e não nas
duas dimensões.

A fonte também tem um limite que decide a janela. O índice é a série revista da
FIRJAN, que começa em 2013: a revisão metodológica a tornou internamente
consistente mas \textbf{não emendável} com a série anterior, de 2005 a 2016, de
modo que nenhuma conta aqui atravessa esse corte. Onze anos é janela curta para
um índice de desenvolvimento, e é a razão principal de os dois blocos serem
lidos como associativos.

O primeiro bloco é transversal e mede se o índice se ordena pela latitude --- em
nível e em variação --- com e sem controle de longitude, que separa o gradiente
sul-norte do gradiente leste-oeste. O segundo é um painel de efeitos fixos
\emph{dentro} do município, que pergunta quanto de desenvolvimento acompanha uma
duplicação da área ou do valor adicionado.
"""


def secao_ifdm() -> str:
    d = pd.read_csv(PROC / "desenvolvimento_gradiente.csv")
    g = d[d.bloco == "B_gradiente"]
    linhas = []
    for _, r in g.iterrows():
        lon = num(r["beta_lon"], 4, mais=True) if pd.notna(r["beta_lon"]) else "---"
        plon = p_val(r["p_lon"]) if pd.notna(r["beta_lon"]) else "---"
        linhas.append(" & ".join([
            esc(r["alvo"]), esc(r["spec"]), str(int(r["n"])), num(r["r2"], 3),
            num(r["beta_lat"], 4, mais=True), p_val(r["p_lat"]), lon, plon,
        ]) + r" \\")
    t1 = tabela(linhas, "llccccccc"[:8],
                (r"\textbf{Desfecho} & \textbf{Spec.} & \textbf{$n$} & \textbf{$R^2$} & "
                 r"\textbf{$\hat{\beta}_{lat}$} & \textbf{$p$} & "
                 r"\textbf{$\hat{\beta}_{lon}$} & \textbf{$p$} \\"),
                ("Gradiente do desenvolvimento municipal",
                 "Gradiente latitudinal do desenvolvimento municipal, com e sem controle de longitude."),
                "tab:ifdm-gradiente",
                (r"mínimos quadrados sobre a seção transversal dos municípios, em "
                 r"\textbf{nível} e sem efeitos fixos --- não se aplicam aqui as convenções "
                 r"de primeira diferença e padronização da Seção~\ref{ap:convencoes}. "
                 r"Erros-padrão robustos a heterocedasticidade (HC1). Latitude e longitude "
                 r"são as do centroide \emph{municipal}, e não da AMC, e entram em "
                 r"\emph{escore-z}: $\hat{\beta}_{lat}$ lê-se por desvio-padrão de "
                 r"latitude, e não por grau. As duas "
                 r"primeiras linhas usam o índice de 2023; as duas últimas, a variação na "
                 r"janela cheia da série revista (2013 a 2023), e perdem um município sem "
                 r"observação nas duas pontas. Um $\hat{\beta}_{lat}$ negativo no nível "
                 r"significa índice menor mais ao norte. A leitura é associativa: nenhuma "
                 r"das quatro linhas identifica efeito causal."),
                tam="footnotesize")

    pn = d[d.modelo.notna()]
    linhas2 = []
    for _, r in pn.iterrows():
        linhas2.append(" & ".join([
            esc(r["modelo"]), reg(r["regressor"]),
            num(r["beta"], 4, mais=True), p_val(r["p"]), num(r["r2_within"], 5),
            n_obs(r["n"]),
        ]) + r" \\")
    t2 = tabela(linhas2, "llcccr",
                (r"\textbf{Modelo} & \textbf{Regressor} & \textbf{$\hat{\beta}$} & "
                 r"\textbf{$p$} & \textbf{$R^2_w$} & \textbf{$n$} \\"),
                ("Painel de efeitos fixos do desenvolvimento",
                 "Desenvolvimento municipal em painel de efeitos fixos, dentro do município."),
                "tab:ifdm-painel",
                (r"variáveis em log-diferença; efeitos fixos de município e de ano, com "
                 r"erros-padrão agrupados \textbf{apenas por município} --- o painel tem "
                 r"oito anos, poucos demais para agrupar também na dimensão temporal. "
                 r"$n = 1.950$ células, de 245 municípios sobre as diferenças anuais de "
                 r"2014 a 2021: a janela termina em 2021 porque é onde acaba a série de "
                 r"valor adicionado do IBGE, e o painel é desbalanceado porque um município "
                 r"não tem par de anos completo e dez células caem por ausência. "
                 r"\texttt{d\_l\_area} é a variação log da área cultivada e "
                 r"\texttt{d\_l\_va} a do valor adicionado agropecuário. O $R^2$ "
                 r"\emph{within} negativo indica ajuste pior que a média dentro do "
                 r"município, e é reportado como saiu."),
                tam="footnotesize")
    return IFDM_TEXTO + chr(10) + chr(10) + t1 + chr(10) + chr(10) + t2


if __name__ == "__main__":
    main()
