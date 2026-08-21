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
    """Escapa texto vindo do CSV: ele traz "#52", "%", "_" e afins."""
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


ROTULO_REGRESSOR = {
    "lestoque_z":                 "log estoque (z)",
    "lestoque2_z":                "log estoque$^2$ (z)",
    "ldeplecao_z":                "log depleção (z)",
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


def tabela(linhas, colspec, cab, legenda, rotulo, nota,
           fonte="elaboração própria.", tam="small"):
    out = [BR + "begin{table}[htb]", BR + "centering",
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

PREAMBULO = r"""
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

\textbf{Unidade e painel.} As regressões deste apêndice correm sobre o painel de 166
Áreas Mínimas Comparáveis de Goiás, 1985--2024 (\(166 \times 40 = 6.640\)
células), descrito na Seção~\ref{sec:met-amc}. Quando uma fonte não cobre a
janela inteira, o \(n\) reportado na tabela é o efetivo após exclusão de
ausentes por lista.

\textbf{Primeira diferença (D7).} O desfecho é sempre a variação anual, e não o
nível: \(\Delta y_{it} = y_{it} - y_{i,t-1}\). É essa transformação que desarma
o vazamento entre regressor e regressando documentado na
Seção~\ref{sec:met-painel}.

\textbf{Padronização.} As exposições entram em \emph{escore-z} calculado sobre
a seção transversal das 166 unidades \(\tilde{E}_i = (E_i - \bar{E})/\sigma_E\),
com \(\sigma\) populacional. Os coeficientes de interação lêem-se, portanto,
como efeito de um desvio-padrão de exposição.

\textbf{Efeitos fixos e erros-padrão.} Salvo indicação em contrário, todas as
especificações trazem efeito fixo de unidade \emph{e} de ano (2FE) e
erros-padrão agrupados nas duas dimensões. O agrupamento efetivamente aplicado
é reportado em cada tabela, porque em uma especificação ele recai para
agrupamento só por unidade quando a matriz de covariância bidimensional não é
positiva-definida.

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
            r"Seção~\ref{sec:met-instrumental} mostra ser otimista neste desenho. A régua "
            r"de permutação não foi computada para estas linhas: ela existe para a "
            r"especificação confirmatória do rebanho, na Tabela~\ref{tab:horserace}, cujas "
            r"regressões são outras. Os $p$ abaixo, portanto, são limite inferior da "
            r"incerteza, e nenhum deles é lido como significância no corpo do texto.")
    return CONF_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "p{3.2cm}p{1.9cm}cccccc", cab,
        (r"Grade confirmatória do \emph{drive} comum",
         r"Grade confirmatória completa do desenho \emph{shift-share}."),
        "tab:confirmatorio", nota)


def main() -> None:
    partes = [PREAMBULO, secao_precedencia(), secao_slx(), secao_sarsem(),
              secao_shiftshare(), secao_placebos(), secao_confirmatorio(),
              secao_oferta(), secao_ifdm()]
    SAIDA.write_text(chr(10).join(partes) + chr(10), encoding="utf-8")
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
a outra. Este é o único bloco do apêndice que \emph{não} usa o painel de AMCs.
Ele corre sobre \textbf{séries anuais agregadas por região}, o que dá cerca de
38 observações --- e é dessa escassez, e não do desenho, que vem a maior parte
da limitação de poder.

A leitura do teste de Granger tem de ser literal: ele mede \emph{precedência
preditiva}, não causalidade. E, aplicado a séries integradas, fabrica
precedência inexistente --- foi o que a decisão D16 registrou. Por isso a
Tabela~\ref{tab:precedencia} reporta, lado a lado, o \(p\) clássico e o \(p\)
de um teste de Wald com erros-padrão robustos a heterocedasticidade e
autocorrelação, na receita de Toda-Yamamoto, que permanece válido sob
integração.

A direção \emph{reversa} está na tabela de propósito. Ela é o achado que a
decisão D16 classificou como \textbf{artefato espúrio}: o sinal forte que
aparece de norte para sul não sobrevive ao tratamento da integração como
relação de longo prazo, e é reportado aqui para que o leitor veja o que o
diagnóstico teve de descartar.
"""


def secao_precedencia() -> str:
    d = pd.read_csv(PROC / "granger_reverso_lags.csv")
    linhas = []
    atual = None
    for _, r in d.iterrows():
        rel = str(r["relacao"])
        if rel != atual:
            atual = rel
            linhas.append(r"\multicolumn{7}{l}{\textit{" + esc(rel) + r"}} \\")
        linhas.append(" & ".join([
            "", str(int(r["lag"])), p_val(r["granger_p_classico"]), p_val(r["wald_p_HAC"]),
            num(r["b1"], 4, mais=True), p_val(r["b1_p_HAC"]), str(int(r["n"])),
        ]) + r" \\")
    cab = (r"& \textbf{Def.} & \textbf{$p$ Granger} & \textbf{$p$ Wald HAC} & "
           r"\textbf{$\hat{\beta}_1$} & \textbf{$p(\hat{\beta}_1)$} & \textbf{$n$} \\")
    nota = (r"séries anuais agregadas por região, em primeira diferença; ``Def.'' é o "
            r"número de defasagens do modelo. $p$ Granger é o teste-F clássico e $p$ "
            r"Wald HAC o mesmo teste com covariância robusta a heterocedasticidade e "
            r"autocorrelação; $\hat{\beta}_1$ é o coeficiente da primeira defasagem da "
            r"série candidata a precedente. O bloco \textsc{reverso} é reportado porque "
            r"foi ele que originou a decisão D16, e não porque sustente afirmação.")
    return TEMPO_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "lcccccr", cab,
        ("Precedência temporal entre séries regionais",
         "Precedência temporal entre as séries regionais, por defasagem."),
        "tab:precedencia", nota)


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

A matriz \(W\) aqui é de contiguidade \emph{queen} entre as 166 unidades,
padronizada por linha, e não a matriz direcional de oito vizinhos da
Seção~\ref{ap:slx}: aqui o objeto é a dependência genérica, e não a direção
sul-norte. Os testes do multiplicador de Lagrange, em suas versões simples e
robusta, indicam qual das duas formas o dado prefere.
"""


def secao_sarsem() -> str:
    d = pd.read_csv(PROC / "painel_espacial_dinamico.csv")
    linhas = []
    for _, r in d.iterrows():
        linhas.append(" & ".join([
            esc(r["modelo"]), esc(r["desc"]),
            num(r["beta_ols"], 4, mais=True), num(r["beta_lag"], 4, mais=True),
            num(r["beta_err"], 4, mais=True), num(r["rho"], 3), num(r["lam"], 3),
            esc(r["forma_preferida"]),
            "sim" if bool(r["sobrevive"]) else r"\textbf{não}",
        ]) + r" \\")
    cab = (r"& \textbf{Especificação} & \textbf{$\hat{\beta}_{MQ}$} & "
           r"\textbf{$\hat{\beta}_{SAR}$} & \textbf{$\hat{\beta}_{SEM}$} & "
           r"\textbf{$\hat{\rho}$} & \textbf{$\hat{\lambda}$} & \textbf{Forma} & "
           r"\textbf{Sobrev.} \\")
    n = int(d["N"].iloc[0])
    nota = (r"$W$ de contiguidade \emph{queen} entre as " + str(n) + r" unidades, "
            r"padronizada por linha. $\hat{\rho}$ é o parâmetro de defasagem espacial do "
            r"SAR e $\hat{\lambda}$ o de dependência do erro no SEM; ``Forma'' é a "
            r"preferida pelos testes do multiplicador de Lagrange em versão robusta. "
            r"``Sobrev.'' indica se o sinal e a significância do coeficiente de interesse "
            r"resistem à modelagem da dependência. Todos os coeficientes vêm de "
            r"especificações em primeira diferença com efeitos fixos.")
    return SARSEM_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "lp{3.3cm}cccccll", cab,
        ("Dependência espacial nos três modelos de painel",
         "Coeficientes de interesse sob mínimos quadrados, SAR e SEM."),
        "tab:sarsem", nota, tam="footnotesize")


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
            linhas.append(r"\multicolumn{7}{l}{\textit{" + esc(h) + r"}} \\")
        tipo = "desfecho" if "desfecho" in str(r["tipo"]) else "tempo"
        linhas.append(" & ".join([
            "", esc(r["placebo"]), tipo,
            num(r["beta"], 4, mais=True), num(r["se"], 4), p_val(r["p"]),
            num(r["r2_within"], 5),
        ]) + r" \\")
    cab = (r"& \textbf{Placebo} & \textbf{Tipo} & \textbf{$\hat{\gamma}$} & "
           r"\textbf{EP} & \textbf{$p$} & \textbf{$R^2_w$} \\")
    n_obs, n_amc = int(d["n_obs"].iloc[0]), int(d["n_amc"].iloc[0])
    nota = (r"mesma equação da Seção~\ref{ap:shiftshare}, com o desfecho ou a defasagem "
            r"trocados. $n = " + f"{n_obs:,}".replace(",", ".") + r"$ observações, "
            + str(n_amc) + r" unidades; efeitos fixos de unidade e de ano; erros-padrão "
            r"agrupados nas duas dimensões. Um placebo cumpre o seu papel quando "
            r"\textbf{não} rejeita: aqui nenhum dos oito o faz.")
    return PLACEBO_TEXTO + chr(10) + chr(10) + tabela(
        linhas, "lp{4.2cm}lcccc", cab,
        ("Placebos de desfecho e de tempo",
         "Bateria de placebos de desfecho e de tempo do desenho \emph{shift-share}."),
        "tab:placebos", nota)


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

A segunda afirmação é a que a decisão D29 reabriu. A variável de depleção,
construída como \(1 - \text{estoque}_t/\text{estoque}_{1985}\), sai do intervalo
\([0,1]\) em cerca de 14\% do painel, nas unidades que \emph{ganharam} estoque.
Padronizar uma variável com domínio violado dilui o sinal, e o nulo publicado
era artefato disso. A Tabela~\ref{tab:deplecao} traz a grade inteira de
tratamentos dessa variável, com e sem ponderação pelo tamanho do estoque, em
duas amostras --- e não apenas a combinação adotada.
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
                (r"desfecho: fluxo anual de conversão. Efeitos fixos de unidade e de ano; "
                 r"erros-padrão agrupados nas duas dimensões. Regressores em \emph{escore-z}."),
                tam="footnotesize")

    d2 = pd.read_csv(PROC / "fronteira_teste_supply_39b.csv")
    d2 = d2[d2.termo == "principal"]
    linhas2 = []
    for _, r in d2.iterrows():
        peso = "estoque" if isinstance(r["peso"], str) else "---"
        linhas2.append(" & ".join([
            esc(r["descricao"]), esc(r["amostra"]), peso,
            num(r["beta_z"], 3, mais=True), p_val(r["p_entidade"]),
            p_val(r["p_entidade_ano"]), num(r["r2_within"], 4),
        ]) + r" \\")
    t2 = tabela(linhas2, "p{4.0cm}llcccc",
                (r"\textbf{Tratamento da depleção} & \textbf{Amostra} & \textbf{Peso} & "
                 r"\textbf{$\hat{\beta}$} & \textbf{$p_{ent}$} & \textbf{$p_{ent+ano}$} & "
                 r"\textbf{$R^2_w$} \\"),
                ("Grade de tratamentos da variável de depleção",
                 "Grade completa de tratamentos da variável de depleção (decisão D29)."),
                "tab:deplecao",
                (r"desfecho: taxa anual de conversão. $p_{ent}$ agrupa por unidade e "
                 r"$p_{ent+ano}$ nas duas dimensões, que é a régua adotada no teste de "
                 r"origem e a reportada no corpo do texto. ``Peso'' indica ponderação "
                 r"pelo tamanho do estoque. A linha ``sem tratamento'' é a especificação "
                 r"publicada antes da D29, e o nulo dela é o artefato que a decisão "
                 r"corrigiu."),
                tam="footnotesize")
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

O primeiro é transversal, sobre os 246 municípios, e mede se o índice de
desenvolvimento se ordena pela latitude --- em nível e em variação --- com e sem
controle de longitude, que separa o gradiente sul-norte do gradiente
leste-oeste. O segundo é um painel de efeitos fixos \emph{dentro} do município,
que pergunta quanto de desenvolvimento acompanha uma duplicação da área ou do
valor adicionado.
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
                (r"mínimos quadrados sobre a seção transversal dos municípios; latitude e "
                 r"longitude em graus decimais do centroide. Um $\hat{\beta}_{lat}$ negativo "
                 r"no nível significa índice menor mais ao norte. A leitura é associativa."),
                tam="footnotesize")

    pn = d[d.modelo.notna()]
    linhas2 = []
    for _, r in pn.iterrows():
        linhas2.append(" & ".join([
            esc(r["modelo"]), reg(r["regressor"]),
            num(r["beta"], 4, mais=True), p_val(r["p"]), num(r["r2_within"], 5),
        ]) + r" \\")
    t2 = tabela(linhas2, "llccc",
                (r"\textbf{Modelo} & \textbf{Regressor} & \textbf{$\hat{\beta}$} & "
                 r"\textbf{$p$} & \textbf{$R^2_w$} \\"),
                ("Painel de efeitos fixos do desenvolvimento",
                 "Desenvolvimento municipal em painel de efeitos fixos, dentro do município."),
                "tab:ifdm-painel",
                (r"variáveis em log-diferença; efeitos fixos de município e de ano. "
                 r"\texttt{d\_l\_area} é a variação log da área cultivada e "
                 r"\texttt{d\_l\_va} a do valor adicionado agropecuário. O $R^2$ "
                 r"\emph{within} negativo indica ajuste pior que a média dentro do "
                 r"município, e é reportado como saiu."),
                tam="footnotesize")
    return IFDM_TEXTO + chr(10) + chr(10) + t1 + chr(10) + chr(10) + t2


if __name__ == "__main__":
    main()
