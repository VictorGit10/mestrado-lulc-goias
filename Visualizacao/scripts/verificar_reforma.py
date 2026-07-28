"""Verificacao da visualizacao reformulada (docs/PLANO_DE_CONSTRUCAO.md §7).

Uso:
    python -m http.server 8765 --directory Visualizacao
    python Visualizacao/scripts/verificar_reforma.py

Cobre navegacao (rail), as pecas interativas, o Sankey de 7 grupos, a varredura
de frases banidas, console/rede e o comportamento no celular.
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/reforma.html"
# Frases que ja estiveram na peca e cairam (BLUEPRINT_PARTE2.md, "Numeros
# banidos"). Precisam ser especificas: "78 mil" sozinho casa com "378 milhoes".
BANIDOS = ["78 mil pontos", "78.000", "-88%", "−88%", "desloca o peso",
           "34 de 36", "16 decis", "1,5 bilh", "encontra um piso",
           "encontrar um piso", "pasto jovem vem ganhando"]


def esperar_parar(pg, teto_ms=6000):
    """Espera a rolagem assentar (incluindo a correcao pos-lazy-render)."""
    anterior, estavel, gasto = None, 0, 0
    while gasto < teto_ms:
        pg.wait_for_timeout(150)
        gasto += 150
        y = pg.evaluate("window.scrollY")
        estavel = estavel + 1 if y == anterior else 0
        anterior = y
        if estavel >= 3:
            return y
    return anterior


def main():
    erros, avisos = [], []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1440, "height": 900})
        console = []
        pg.on("console", lambda m: console.append((m.type, m.text)))
        pg.on("pageerror", lambda e: console.append(("pageerror", str(e))))
        falhas_rede = []
        pg.on("response", lambda r: falhas_rede.append((r.status, r.url)) if r.status >= 400 else None)

        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_timeout(1200)

        # --- 1. steps dos 40 anos gerados ---
        n_steps = pg.locator(".step[data-year]").count()
        print(f"steps anuais: {n_steps}")
        if n_steps != 40:
            erros.append(f"esperava 40 steps anuais, achei {n_steps}")

        # --- 2. rail lateral ---
        vis_hero = pg.eval_on_selector("#rail-lateral", "el => el.classList.contains('is-visivel')")
        print(f"rail visivel no hero: {vis_hero} (esperado False)")
        if vis_hero:
            erros.append("rail lateral aparece no hero")

        # --- 3. saltar para a Parte 3 pelo rail ---
        pg.evaluate("window.scrollTo(0, 1200)")
        pg.wait_for_timeout(400)
        vis_p1 = pg.eval_on_selector("#rail-lateral", "el => el.classList.contains('is-visivel')")
        print(f"rail visivel na Parte 1: {vis_p1} (esperado True)")
        if not vis_p1:
            erros.append("rail lateral nao aparece depois do hero")

        pg.click("#rail-lateral a[href='#parte-3']")
        esperar_parar(pg)
        ativo = pg.eval_on_selector_all(
            "#rail-lateral .rail-item.is-active, #rail-lateral .rail-subitem.is-active",
            "els => els.map(e => e.dataset.alvo)")
        print(f"apos clicar em 'O veredito', ativo = {ativo}")
        if ativo != ["parte-3"]:
            erros.append(f"rail nao marcou parte-3 como ativa (marcou {ativo})")

        # --- 4. regua dos 40 anos recolhe fora da Parte 1 ---
        recolhida = pg.eval_on_selector("#regua-anos", "el => el.classList.contains('is-recolhida')")
        print(f"regua recolhida na Parte 3: {recolhida} (esperado True)")
        if not recolhida:
            erros.append("a regua dos 40 anos nao recolhe fora da Parte 1")

        # --- 5. perna ativa acende a Parte 2 como ancestral ---
        pg.click("#rail-lateral a[href='#p2-perna3']")
        esperar_parar(pg)
        estado = pg.evaluate("""() => {
            const a = document.querySelector('#rail-lateral .rail-subitem.is-active');
            const p = document.querySelector('#rail-lateral .rail-item.is-ancestral');
            return { ativo: a && a.dataset.alvo, ancestral: p && p.dataset.alvo };
        }""")
        print(f"perna 3 ativa -> {estado}")
        if estado.get("ativo") != "p2-perna3" or estado.get("ancestral") != "parte-2":
            erros.append(f"aninhamento perna->parte falhou: {estado}")

        # --- 6. Sankey desenhou com o Mosaico ---
        pg.evaluate("document.getElementById('p1-fluxos').scrollIntoView()")
        pg.wait_for_timeout(2000)
        sankey = pg.evaluate("""() => {
            const c = document.getElementById('sankey-container');
            const svg = c && c.querySelector('svg');
            if (!svg) return { svg: false };
            const txt = svg.textContent || '';
            return { svg: true, nodes: svg.querySelectorAll('rect').length, mosaico: txt.includes('Mosaico') };
        }""")
        print(f"sankey: {sankey}")
        if not sankey.get("svg"):
            erros.append("o Sankey nao desenhou")
        elif not sankey.get("mosaico"):
            erros.append("o Sankey desenhou sem a classe Mosaico")

        # --- 6b. as duas pecas herdadas montaram ---
        pg.evaluate("document.getElementById('p2-perna1').scrollIntoView()")
        pg.wait_for_timeout(2500)
        pg.evaluate("document.getElementById('p2-perna2').scrollIntoView()")
        pg.wait_for_timeout(2500)
        pecas = pg.evaluate("""() => ({
            marchaMapa: !!document.querySelector('#marchamap-mapa svg'),
            marchaStrip: !!document.querySelector('#marchamap-strip svg'),
            reservaMapa: !!document.querySelector('#reserva-mapa svg'),
            reservaHist: !!document.querySelector('#reserva-hist svg'),
            toggleRegioes: document.querySelectorAll('#reserva-regiao-toggle button').length,
            amcs: document.querySelectorAll('#reserva-mapa path').length,
            esquema: document.querySelectorAll('.esquema-painel svg').length
        })""")
        print(f"pecas: {pecas}")
        for k, minimo in [("marchaMapa", True), ("marchaStrip", True),
                          ("reservaMapa", True), ("reservaHist", True)]:
            if not pecas.get(k):
                erros.append(f"peca interativa nao montou: {k}")
        if pecas.get("toggleRegioes", 0) < 5:
            erros.append(f"toggle de regioes com {pecas.get('toggleRegioes')} botoes (esperava >=5)")
        if pecas.get("amcs", 0) < 150:
            erros.append(f"mapa de AMCs com {pecas.get('amcs')} poligonos (esperava ~166)")
        if pecas.get("esquema") != 2:
            erros.append(f"esquema da regressao espuria com {pecas.get('esquema')} paineis (esperava 2)")

        # --- 6c. Partes 3 e 4 (a oficina) ---
        pg.evaluate("document.getElementById('parte-3').scrollIntoView()")
        pg.wait_for_timeout(800)
        pg.evaluate("document.getElementById('p4-painel').scrollIntoView()")
        pg.wait_for_timeout(2500)
        fecho = pg.evaluate("""() => {
            const inv = document.getElementById('inventario-grid');
            const det = document.getElementById('p4-decisoes-tabela');
            return {
                autocorrecoes: document.querySelectorAll('.autocorrecoes > li').length,
                verificacoes: document.querySelectorAll('.verificacoes-ok li').length,
                limites: document.querySelectorAll('.limites-lista > li').length,
                decisoesColapsadas: det ? !det.open : null,
                decisoes: document.querySelectorAll('.decisao-card').length,
                inventario: inv ? inv.querySelectorAll('.inventario-card, .inventario-tema, article, section').length : 0,
                inventarioCarregou: inv ? !inv.querySelector('.resumo-loading') : false
            };
        }""")
        print(f"fecho: {fecho}")
        if fecho.get("autocorrecoes") != 10:
            erros.append(f"painel de autocorrecoes com {fecho.get('autocorrecoes')} itens (esperava 10)")
        if fecho.get("verificacoes") != 3:
            erros.append(f"bloco de verificacoes com {fecho.get('verificacoes')} itens (esperava 3)")
        if fecho.get("decisoes") != 26:
            erros.append(f"{fecho.get('decisoes')} cards de decisao (esperava 26 = D1-D26)")
        if not fecho.get("decisoesColapsadas"):
            erros.append("as 26 decisoes deveriam comecar colapsadas (sao referencia)")
        if not fecho.get("inventarioCarregou"):
            erros.append("a vitrine do painel nao carregou")

        # --- 7. frases banidas ---
        # A lista guarda contra REAFIRMAR um achado que caiu. Os blocos abaixo
        # fazem o oposto: narram a queda, e por isso citam as frases de
        # proposito ("nao se afirma que o pasto jovem vem ganhando peso"; "essa
        # regua derrubou o -88%"). Acusar ali seria punir a parte mais honesta
        # da peca — e o teste passaria a premiar quem varre o erro para debaixo
        # do tapete. Por isso sao excluidos da varredura, por classe explicita.
        EXCLUIR = [".nao-diz", ".nota-honestidade", ".autocorrecoes",
                   ".verificacoes-ok", ".decisoes-corpo", ".regua-decidiu"]
        texto = pg.evaluate("""(sel) => {
            const c = document.body.cloneNode(true);
            c.querySelectorAll(sel.join(',')).forEach(e => e.remove());
            return c.innerText;
        }""", EXCLUIR)
        achados = [b for b in BANIDOS if b.lower() in texto.lower()]
        print("frases banidas encontradas:", ascii(achados))
        if achados:
            erros.append(f"frases banidas no DOM: {achados}")

        # --- 7b. integridade das ancoras ---
        anc = pg.evaluate("""() => {
            const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
            const dup = ids.filter((v, i) => ids.indexOf(v) !== i);
            const alvos = new Set(ids);
            const quebrados = [...document.querySelectorAll('a[href^="#"]')]
                .map(a => a.getAttribute('href').slice(1))
                .filter(h => h && !alvos.has(h));
            return { dup: [...new Set(dup)], quebrados: [...new Set(quebrados)] };
        }""")
        print(f"ancoras: {anc}")
        if anc.get("dup"):
            erros.append(f"ids duplicados: {anc['dup']}")
        if anc.get("quebrados"):
            erros.append(f"links internos sem alvo: {anc['quebrados']}")

        # --- 8. console + rede ---
        ruins = [c for c in console if c[0] in ("error", "pageerror")]
        print(f"console errors: {ruins}")
        if ruins:
            erros.append(f"console com erros: {ruins}")
        f404 = [f for f in falhas_rede if not f[1].endswith("favicon.ico")]
        print(f"respostas >=400: {f404}")
        if f404:
            erros.append(f"assets faltando: {f404}")

        # --- 9. mobile ---
        pg.set_viewport_size({"width": 390, "height": 844})
        pg.evaluate("window.scrollTo(0, 3000)")
        pg.wait_for_timeout(800)
        mob = pg.evaluate("""() => {
            const btn = document.getElementById('rail-lateral-toggle');
            const lista = document.getElementById('rail-lateral-lista');
            return {
                btnVisivel: btn ? getComputedStyle(btn).display !== 'none' : null,
                listaOculta: lista ? getComputedStyle(lista).display === 'none' : null,
                overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
                // `overflow-x: clip` no html nao pode ter quebrado o sticky.
                stickyMapa: getComputedStyle(document.querySelector('.story-figure')).position,
                stickyRegua: getComputedStyle(document.getElementById('regua-anos')).position
            };
        }""")
        print(f"mobile: {mob}")
        if not mob.get("btnVisivel"):
            erros.append("botao do sumario nao aparece no mobile")
        if not mob.get("listaOculta"):
            avisos.append("a lista do rail comeca aberta no mobile")
        if mob.get("overflowX"):
            erros.append("a pagina rola horizontalmente no mobile")
        if mob.get("stickyMapa") != "sticky" or mob.get("stickyRegua") != "sticky":
            erros.append(f"o overflow-x: clip quebrou o sticky: {mob}")

        nav.close()

    print("\n" + "=" * 60)
    for a in avisos:
        print("AVISO:", a)
    if erros:
        for e in erros:
            print("FALHA:", e)
        sys.exit(1)
    print("Reforma: todas as verificacoes passaram.")


main()
