#!/usr/bin/env python3
"""Invariantes do texto de qualificação.

Não é auditoria: é teste de regressão. Roda sempre as mesmas cinco checagens,
dá sempre o mesmo resultado, e detecta a classe de defeito que as
reestruturações produzem (ponteiro quebrado, lista dessincronizada, sigla
órfã, calibragem perdida).

O que ele NÃO faz: conferir número contra CSV, conferir atribuição contra
fonte, revisar língua. Isso é auditoria, é humana, e tem escopo declarado.

    python verificar.py          # tudo
    python verificar.py 3        # só a invariante 3
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent
CORPO = [
    RAIZ / "pre" / "resumo.tex",
    RAIZ / "pre" / "abstract.tex",
    RAIZ / "pre" / "siglas.tex",
    *[RAIZ / "cap" / f for f in sorted(p.name for p in (RAIZ / "cap").glob("*.tex"))],
]
BIB = RAIZ / "ref" / "referencias.bib"
CAP2 = RAIZ / "cap" / "02_referencial.tex"
CAP5 = RAIZ / "cap" / "05_discussao.tex"

erros: list[str] = []
avisos: list[str] = []


def ler(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def sem_comentario(texto: str) -> str:
    """Remove comentários LaTeX (% não escapado) preservando as linhas."""
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in texto.splitlines())


def rel(p: Path) -> str:
    return str(p.relative_to(RAIZ)).replace("\\", "/")


# --------------------------------------------------------------------------
# 1. Todo \ref resolve a um \label existente
# --------------------------------------------------------------------------
def inv1() -> None:
    labels: set[str] = set()
    refs: list[tuple[str, int, str]] = []
    for p in CORPO:
        txt = sem_comentario(ler(p))
        labels |= set(re.findall(r"\\label\{([^}]*)\}", txt))
        for n, linha in enumerate(txt.splitlines(), 1):
            for chave in re.findall(r"\\(?:auto)?ref\{([^}]*)\}", linha):
                refs.append((rel(p), n, chave))
    for arquivo, n, chave in refs:
        if chave not in labels:
            erros.append(f"[1] {arquivo}:{n} — \\ref{{{chave}}} sem \\label correspondente")
    print(f"  1. ponteiros ....... {len(refs)} \\ref contra {len(labels)} \\label")


# --------------------------------------------------------------------------
# 2. Toda chave citada existe no .bib; nenhuma entrada ativa fica órfã
# --------------------------------------------------------------------------
def inv2() -> None:
    bib = ler(BIB)
    entradas = set(re.findall(r"^@\w+\{([^,]+),", sem_comentario(bib), re.M))
    citadas: dict[str, tuple[str, int]] = {}
    for p in CORPO:
        txt = sem_comentario(ler(p))
        for n, linha in enumerate(txt.splitlines(), 1):
            for grupo in re.findall(r"\\cite[a-zA-Z]*(?:\[[^\]]*\])*\{([^}]*)\}", linha):
                for chave in (c.strip() for c in grupo.split(",")):
                    citadas.setdefault(chave, (rel(p), n))
    for chave, (arquivo, n) in sorted(citadas.items()):
        if chave not in entradas:
            erros.append(f"[2] {arquivo}:{n} — chave '{chave}' citada e ausente do .bib")
    for chave in sorted(entradas - set(citadas)):
        avisos.append(f"[2] entrada '{chave}' está no .bib e não é citada em lugar nenhum")
    print(f"  2. citações ........ {len(citadas)} chaves citadas, {len(entradas)} entradas no .bib")


# --------------------------------------------------------------------------
# 3. Lista de leitura do .bib == nomes do §2.10
# --------------------------------------------------------------------------
PARADAS = {"et", "al", "e", "de", "da", "do", "von", "the", "and"}


def sobrenomes(bruto: str) -> set[str]:
    return {
        t.lower()
        for t in re.findall(r"[A-ZÀ-Ü][\wÀ-ü'’-]+", bruto)
        if t.lower() not in PARADAS and len(t) > 2
    }


def obras_bib(bloco: str) -> dict[str, set[str]]:
    """Uma obra por linha de item ('% Nome, X. (ano). Título'); linha indentada
    com dois espaços ou mais é continuação; linha aberta por palavra em
    CAIXA-ALTA é nota de prosa (SAÍDA, RESOLVIDO), não item da lista."""
    achadas: dict[str, set[str]] = {}
    for linha in bloco.splitlines():
        if not re.match(r"^%\s(?!\s)", linha):
            continue
        corpo_linha = linha[2:]
        if re.match(r"^[A-ZÀ-Ü]{4,}\b", corpo_linha):
            continue
        m = re.search(r"^([^(\[]{2,70}?)\((1[6-9]\d\d|20\d\d)\)", corpo_linha)
        if m and (toks := sobrenomes(m.group(1))):
            achadas.setdefault(m.group(2), set()).update(toks)
    return achadas


def obras_cap(texto: str) -> dict[str, set[str]]:
    """Uma obra por ficha. Desde 19/ago/2026 o §2.10 traz registro NBR 6023
    dentro do comando de ficha, em vez de autor-data: o ano fecha o registro e
    a autoria é o trecho até o primeiro ponto final."""
    achadas: dict[str, set[str]] = {}
    for pedaco in texto.split("ficha{")[1:]:
        prof, fim = 1, 0
        while fim < len(pedaco) and prof:
            prof += {"{": 1, "}": -1}.get(pedaco[fim], 0)
            fim += 1
        bruto = pedaco[: fim - 1]
        limpo = re.sub(r"(?:emph|textbf|textit)\{([^}]*)\}", r"\1", bruto)
        limpo = re.sub(r"\s+", " ", limpo).replace("\\", "")
        anos = re.findall(r"(1[6-9]\d\d|20\d\d)", limpo)
        if anos and (toks := sobrenomes(limpo.split(".")[0])):
            achadas.setdefault(anos[-1], set()).update(toks)
    return achadas


def inv3() -> None:
    bib = ler(BIB)
    bloco = re.search(r"LISTA DE LEITURA.*?(?=^% ={10,})", bib, re.S | re.M)
    if not bloco:
        erros.append("[3] bloco 'LISTA DE LEITURA' não encontrado no .bib")
        return
    agenda = re.search(r"\\label\{sec:ref-agenda\}(.*?)(?=\\section|\Z)", ler(CAP2), re.S)
    if not agenda:
        erros.append("[3] seção sec:ref-agenda não encontrada no cap. 2")
        return

    no_bib, no_cap = obras_bib(bloco.group(0)), obras_cap(agenda.group(1))
    for ano in sorted(set(no_bib) | set(no_cap)):
        b, c = no_bib.get(ano, set()), no_cap.get(ano, set())
        if b and not c:
            erros.append(f"[3] obra de {ano} ({'/'.join(sorted(b))}) está na lista do .bib e não no §2.10")
        elif c and not b:
            erros.append(f"[3] obra de {ano} ({'/'.join(sorted(c))}) está no §2.10 e não na lista do .bib")
        elif b and c and not (b & c):
            erros.append(f"[3] {ano}: .bib diz {'/'.join(sorted(b))}, §2.10 diz {'/'.join(sorted(c))}")
    print(f"  3. lista de leitura  {len(no_bib)} obras datadas no .bib, {len(no_cap)} no §2.10")
    print("     (obra sem ano — Becker — fica fora desta checagem, por construção)")


# --------------------------------------------------------------------------
# 4. Toda sigla é definida na primeira ocorrência no corpo
# --------------------------------------------------------------------------
EXPANSOES: dict[str, str] = {}


def inv4() -> None:
    pares = re.findall(r"\\item\[([^\]]+)\]\s*([^\n\\]*)", ler(RAIZ / "pre" / "siglas.tex"))
    EXPANSOES.update({s: e for s, e in pares})
    siglas = [s for s, _ in pares]
    corpo = [(p, sem_comentario(ler(p))) for p in CORPO if "siglas" not in p.name]
    for sigla in siglas:
        alvo = re.escape(sigla)
        primeira = None
        for p, txt in corpo:
            m = re.search(rf"(?<![\w-]){alvo}(?![\w-])", txt)
            if m:
                n = txt[: m.start()].count("\n") + 1
                linha = txt.splitlines()[n - 1]
                primeira = (rel(p), n, linha, m.start() - txt.rfind("\n", 0, m.start()) - 1)
                break
        if primeira is None:
            erros.append(f"[4] sigla '{sigla}' está na lista e não aparece no corpo")
            continue
        arquivo, n, linha, col = primeira
        janela = linha[max(0, col - 90) : col + len(sigla) + 40]
        definida = f"({sigla}" in janela or f"{sigla})" in janela or "\\footnote" in janela
        if definida:
            continue
        # A sigla é expandida em algum lugar do corpo? Se nunca, é órfã de fato.
        # Duas palavras plenas da expansão, com folga entre elas, bastam de
        # sinal e toleram a variação de redação ("Sistema IBGE de Recuperação").
        chaves = re.findall(r"[\wÀ-ü]{4,}", EXPANSOES.get(sigla, ""))[:2]
        alvo = r"[^.]{0,45}?".join(re.escape(k) for k in chaves)
        nunca = len(chaves) == 2 and not any(
            re.search(alvo, re.sub(r"\s+", " ", t), re.I) for _, t in corpo
        )
        if nunca:
            avisos.append(f"[4] '{sigla}' nunca é expandida no corpo (1a ocorrência em {arquivo}:{n})")
        elif " & " not in linha:  # célula de tabela pode usar a forma curta
            avisos.append(f"[4] {arquivo}:{n} — 1a ocorrência de '{sigla}' fora de tabela e sem definição: ...{janela.strip()}...")
    print(f"  4. siglas .......... {len(siglas)} na lista, conferidas na 1a ocorrência")


# --------------------------------------------------------------------------
# 5. Calibragem: frases proibidas ausentes, âncoras presentes
# --------------------------------------------------------------------------
PROIBIDAS = [
    (r"iLUC[^.]{0,60}refutad|refutad[^.]{0,60}iLUC", "iLUC nunca 'refutado' (regra de 28/jul)"),
    (r"teto\s+f[íi]sico", "'teto físico' contradiz o cap. 4 (não separou exaustão de restrição legal)"),
    (r"terra\s+dispon[íi]vel|estoque\s+dispon[íi]vel", "Cerrado remanescente é exposição, não disponibilidade"),
    (r"0,026|0,031", "p-valores agrupados não devem ser citados como significância"),
    (r"vegeta[çc][ãa]o\s+nativa", "usar 'vegetação natural' (classe 3 'floresta nativa' é exceção legítima)"),
]
ANCORAS = [
    (CAP2, r"não equivale a demonstrar que o fenômeno não exista", "ressalva do nulo do iLUC (§2.3)"),
    (CAP2, r"corroborante e não estabelecida", "grau do drive comum no cap. 2 (§2.5)"),
    (CAP2, r"não constitui teste", "Martins entra como vocabulário (§2.7)"),
    (CAP5, r"corroborante e não estabelecido", "grau do drive comum (§5.3)"),
    (CAP5, r"não descreve uma reserva de terra aproveitável", "voz da exposição (§5.5)"),
]


ABSOLVE = r"não devem ser citados|não deve ser citad|floresta nativa|campo nativo|Cerrado nativo"


def inv5() -> None:
    for p in CORPO:
        bruto = sem_comentario(ler(p))
        # normaliza para achar frase quebrada em duas linhas, guardando o mapa
        # de posição -> linha original
        pos_linha, plano = [], []
        for n, linha in enumerate(bruto.splitlines(), 1):
            for ch in linha + " ":
                plano.append(ch)
                pos_linha.append(n)
        txt = "".join(plano)
        # trechos entre aspas latex são citação direta: reproduzem a fonte
        citacoes = [m.span() for m in re.finditer(r"``.+?''", txt, re.S)]
        for padrao, motivo in PROIBIDAS:
            for m in re.finditer(padrao, txt, re.I):
                if any(a <= m.start() < b for a, b in citacoes):
                    continue
                ctx = txt[max(0, m.start() - 160) : m.end() + 160]
                if re.search(ABSOLVE, ctx, re.I):
                    continue
                avisos.append(f"[5] {rel(p)}:{pos_linha[m.start()]} — {motivo}: ...{ctx[130:230].strip()}...")
    for p, padrao, oque in ANCORAS:
        if not re.search(padrao, ler(p)):
            erros.append(f"[5] âncora de calibragem sumiu de {rel(p)}: {oque}")
    print(f"  5. calibragem ...... {len(PROIBIDAS)} padrões proibidos, {len(ANCORAS)} âncoras")


# --------------------------------------------------------------------------
TODAS = {1: inv1, 2: inv2, 3: inv3, 4: inv4, 5: inv5}

if __name__ == "__main__":
    pedidas = [int(a) for a in sys.argv[1:]] or sorted(TODAS)
    print("Invariantes do texto de qualificação\n")
    for i in pedidas:
        TODAS[i]()
    print()
    for a in avisos:
        print(f"AVISO {a}")
    for e in erros:
        print(f"ERRO  {e}")
    print(f"\n{len(erros)} erro(s), {len(avisos)} aviso(s).")
    print("Aviso pede olho humano; erro quebra invariante.")
    sys.exit(1 if erros else 0)
