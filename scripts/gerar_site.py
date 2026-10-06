"""
gerar_site.py — lê dados/produtos.json e monta o site (index.html)

Gera: cards, botões de filtro por categoria, seção "Testados", links das redes
e a data da última atualização. Tudo é injetado no template.html pelos
marcadores <!--NOME-->.

Rodar:  python scripts/gerar_site.py
        (rode o coletar.py antes, pra ter os produtos)
"""

import os
import json
import hashlib
from urllib.parse import quote
from datetime import datetime, timedelta, timezone

RAIZ = os.path.join(os.path.dirname(__file__), "..")
ARQUIVO_PRODUTOS = os.path.join(RAIZ, "dados", "produtos.json")
ARQUIVO_SAIDA = os.path.join(RAIZ, "index.html")
ARQUIVO_TEMPLATE = os.path.join(os.path.dirname(__file__), "template.html")

# ---------------------------------------------------------------------------
# REDES SOCIAIS — deixe o link vazio ("") para esconder a rede no site
# ---------------------------------------------------------------------------
REDES = [
    ("TikTok",    "https://www.tiktok.com/@universo_tec_shop"),
    ("Instagram", "https://www.instagram.com/universotecshop26/"),
    ("YouTube",   "https://www.youtube.com/@UniversoTecSHOP"),
]

# E-mail para "Sugira um produto". Vazio = só mostra os botões das redes.
EMAIL_SUGESTAO = "universotecshop26@gmail.com"

# Horário de Brasília (sem horário de verão desde 2019)
BRASILIA = timezone(timedelta(hours=-3))


HEART_SVG = (
    '<svg viewBox="0 0 24 24" fill="none">'
    '<path class="heart-fill" d="M12 20.5l-1.4-1.27C5.4 14.55 2 11.47 2 7.7 2 5.1 4.02 3 6.6 3'
    'c1.54 0 3.02.72 3.9 1.86C11.38 3.72 12.86 3 14.4 3 16.98 3 19 5.1 19 7.7'
    'c0 3.77-3.4 6.85-8.6 11.53L12 20.5z"/>'
    '<path d="M12 20.5l-1.4-1.27C5.4 14.55 2 11.47 2 7.7 2 5.1 4.02 3 6.6 3'
    'c1.54 0 3.02.72 3.9 1.86C11.38 3.72 12.86 3 14.4 3 16.98 3 19 5.1 19 7.7'
    'c0 3.77-3.4 6.85-8.6 11.53L12 20.5z" stroke="#4d8dff" stroke-width="1.7" stroke-linejoin="round"/>'
    "</svg>"
)

SETA_SVG = (
    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none">'
    '<path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" stroke-width="1.4" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

SHARE_SVG = (
    '<svg viewBox="0 0 24 24" fill="none"><path d="M4 12v7a2 2 0 002 2h12a2 2 0 002-2v-7M16 6l-4-4-4 4M12 2v13" '
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

CHECK_SVG = (
    '<svg viewBox="0 0 24 24" fill="none"><path d="M9 12l2 2 4-4M12 3l7 4v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V7l7-4z" '
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

PLAY_SVG = (
    '<svg viewBox="0 0 24 24" fill="none"><path d="M7 4.5v15l12-7.5-12-7.5z" stroke="currentColor" '
    'stroke-width="1.8" stroke-linejoin="round"/></svg>'
)

ICONES_REDES = {
    "TikTok": '<path d="M15.5 3c.4 2.3 1.9 3.9 4.5 4.1v3.1c-1.6 0-3.1-.5-4.4-1.4v6.4A6 6 0 119.6 9.2v3.2a2.9 2.9 0 102.9 2.9V3h3z" fill="currentColor"/>',
    "Instagram": '<rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor"/>',
    "E-mail": '<rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" stroke-width="1.8"/><path d="M3.5 7l8.5 6 8.5-6" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
    "YouTube": '<rect x="2.5" y="5" width="19" height="14" rx="4" stroke="currentColor" stroke-width="1.8"/><path d="M10 9.2v5.6l4.8-2.8L10 9.2z" fill="currentColor"/>',
}


def carregar_produtos():
    if not os.path.exists(ARQUIVO_PRODUTOS):
        return []
    with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def slug(texto):
    """Transforma 'Iluminação' em 'iluminacao' — usado no data-cat do filtro."""
    acentos = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ",
                            "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC")
    return texto.translate(acentos).lower().replace(" ", "-")


# ícone SVG de cada categoria (traço fino, no estilo do site)
ICONES = {
    "todos":        '<rect x="3" y="3" width="7" height="7" rx="1.5" stroke-width="1.7"/><rect x="14" y="3" width="7" height="7" rx="1.5" stroke-width="1.7"/><rect x="3" y="14" width="7" height="7" rx="1.5" stroke-width="1.7"/><rect x="14" y="14" width="7" height="7" rx="1.5" stroke-width="1.7"/>',
    "audio":        '<path d="M3 14v-2a9 9 0 0118 0v2M3 14a2 2 0 002 2h1v-5H5a2 2 0 00-2 2zM21 14a2 2 0 01-2 2h-1v-5h1a2 2 0 012 2z" stroke-width="1.7" stroke-linejoin="round"/>',
    "mouse":        '<rect x="7" y="3" width="10" height="18" rx="5" stroke-width="1.7"/><path d="M12 7v3" stroke-width="1.7" stroke-linecap="round"/>',
    "teclado":      '<rect x="2" y="6" width="20" height="12" rx="2" stroke-width="1.7"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M8 14h8" stroke-width="1.7" stroke-linecap="round"/>',
    "gamer":        '<path d="M6 11h4M8 9v4M15 11h.01M18 11h.01M16.5 13h.01M17 8H7a4 4 0 00-4 4l1 5a2 2 0 003.5 1l1.5-2h6l1.5 2a2 2 0 003.5-1l1-5a4 4 0 00-4-4z" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
    "carregamento": '<path d="M13 2L4.5 12.5a1 1 0 00.8 1.6H11l-1 7.9L18.5 11a1 1 0 00-.8-1.6H12l1-7.4z" stroke-width="1.7" stroke-linejoin="round"/>',
    "cabos":        '<path d="M4 8a3 3 0 013-3h1a3 3 0 010 6H7m10 8a3 3 0 01-3-3v0a3 3 0 013-3h1M9 8h6" stroke-width="1.7" stroke-linecap="round"/>',
    "celular":      '<rect x="6" y="2" width="12" height="20" rx="2.5" stroke-width="1.7"/><path d="M11 18h2" stroke-width="1.7" stroke-linecap="round"/>',
    "setup":        '<rect x="2" y="4" width="20" height="12" rx="2" stroke-width="1.7"/><path d="M8 20h8M12 16v4" stroke-width="1.7" stroke-linecap="round"/>',
    "iluminacao":   '<path d="M9 18h6M10 21h4M12 2a6 6 0 00-4 10.5c.6.5 1 1.3 1 2.1V15h6v-.4c0-.8.4-1.6 1-2.1A6 6 0 0012 2z" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
    "vestivel":     '<rect x="7" y="6" width="10" height="12" rx="2.5" stroke-width="1.7"/><path d="M9 6l.5-3h5l.5 3M9 18l.5 3h5l.5-3" stroke-width="1.7" stroke-linejoin="round"/>',
}

def icone(chave):
    """Devolve o SVG do ícone da categoria (ou um genérico se não tiver)."""
    corpo = ICONES.get(chave, '<circle cx="12" cy="12" r="9" stroke-width="1.7"/>')
    return f'<svg viewBox="0 0 24 24" fill="none">{corpo}</svg>'


def escapar(texto):
    """Evita que aspas no nome do produto quebrem o HTML."""
    return (str(texto).replace("&", "&amp;").replace("<", "&lt;")
                      .replace(">", "&gt;").replace('"', "&quot;"))


def id_produto(p):
    """Id estável (não muda quando a ordem muda) — usado nos favoritos."""
    return hashlib.sha1(p["link"].encode("utf-8")).hexdigest()[:10]


def preco_num(p):
    try:
        return float(p["preco"].replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return 0.0


def montar_filtros(produtos):
    """Cria os botões de filtro, um por categoria, com a contagem."""
    contagem = {}
    for p in produtos:
        contagem[p["cat"]] = contagem.get(p["cat"], 0) + 1

    botoes = [
        f'<button class="filtro ativo" data-filtro="todos" aria-pressed="true">'
        f'{icone("todos")}Todos <span class="filtro-num">{len(produtos)}</span></button>'
    ]
    for cat in sorted(contagem, key=slug):
        s = slug(cat)
        botoes.append(
            f'<button class="filtro" data-filtro="{s}" aria-pressed="false">'
            f'{icone(s)}{escapar(cat)} <span class="filtro-num">{contagem[cat]}</span></button>'
        )
    return "\n      ".join(botoes)


def montar_card(indice, p):
    reais, _, centavos = p["preco"].partition(",")
    nome = escapar(p["nome"])
    link = escapar(p["link"])
    testado = bool(p.get("testado"))

    if p.get("imagem"):
        img_html = f'<img src="{escapar(p["imagem"])}" alt="{nome}" loading="lazy" decoding="async">'
    else:
        img_html = '<span class="placeholder">IMAGEM DO PRODUTO</span>'

    selo = f'<span class="selo-testado">{CHECK_SVG}Testado</span>' if testado else ""

    return f"""
      <article class="card{' card-testado' if testado else ''}" data-cat="{slug(p['cat'])}" data-id="{id_produto(p)}" data-preco="{preco_num(p):.2f}" data-ordem="{indice}">
        {selo}
        <div class="card-acoes">
          <button class="card-btn card-share" title="Compartilhar" aria-label="Compartilhar">{SHARE_SVG}</button>
          <button class="card-btn card-fav" title="Favoritar" aria-label="Favoritar">{HEART_SVG}</button>
        </div>
        <a class="card-img" href="{link}" target="_blank" rel="noopener sponsored" tabindex="-1" aria-hidden="true">{img_html}</a>
        <div class="card-body">
          <div class="card-cat">{escapar(p['cat'])}</div>
          <h3 class="card-name">{nome}</h3>
          <div class="card-foot">
            <div class="card-price">R$ {reais}<span class="cents">,{centavos}</span></div>
            <a class="card-link" href="{link}" target="_blank" rel="noopener sponsored">Ver oferta {SETA_SVG}</a>
          </div>
        </div>
      </article>"""


def montar_testados(produtos):
    """Seção de destaque com os produtos que o dono comprou e testou."""
    testados = [p for p in produtos if p.get("testado")]
    if not testados:
        return ""

    blocos = []
    for p in testados:
        reais, _, centavos = p["preco"].partition(",")
        nome = escapar(p["nome"])
        link = escapar(p["link"])
        nota = f'<blockquote class="destaque-nota">“{escapar(p["nota"])}”</blockquote>' if p.get("nota") else ""
        video = p.get("video", "")
        img = f'<img src="{escapar(p["imagem"])}" alt="{nome}" loading="lazy">' if p.get("imagem") else ""
        if video.endswith(".mp4"):
            # vídeo hospedado no site: abre o player sem sair da página
            attrs = f'data-video="{escapar(video)}" data-poster="{escapar(p.get("capa", ""))}" data-titulo="{nome}"'
            botao_video = f'<button class="botao botao-ghost" {attrs}>{PLAY_SVG}Ver vídeo</button>'
            midia = (f'<button class="destaque-img" {attrs} aria-label="Assistir ao vídeo do produto">{img}'
                     f'<span class="play-badge">{PLAY_SVG}</span></button>')
        else:
            botao_video = (f'<a class="botao botao-ghost" href="{escapar(video)}" target="_blank" rel="noopener">{PLAY_SVG}Ver vídeo</a>'
                           if video else "")
            midia = f'<a class="destaque-img" href="{link}" target="_blank" rel="noopener sponsored" tabindex="-1" aria-hidden="true">{img}</a>'
        blocos.append(f"""
      <article class="destaque reveal" data-id="{id_produto(p)}">
        {midia}
        <div class="destaque-body">
          <span class="selo-testado">{CHECK_SVG}Testado por nós</span>
          <div class="card-cat">{escapar(p['cat'])}</div>
          <h3>{nome}</h3>
          {nota}
          <div class="destaque-foot">
            <div class="card-price destaque-preco">R$ {reais}<span class="cents">,{centavos}</span></div>
            <div class="destaque-botoes">
              <a class="botao" href="{link}" target="_blank" rel="noopener sponsored">Ver oferta {SETA_SVG}</a>
              {botao_video}
            </div>
          </div>
        </div>
      </article>""")

    return f"""
  <section class="testados" id="testados">
    <div class="section-head reveal">
      <div>
        <h2>Testados de verdade</h2>
        <p class="section-sub">Comprei, usei e gravei. Esses aqui eu garanto.</p>
      </div>
    </div>
    <div class="destaques">{''.join(blocos)}
    </div>
  </section>"""


def montar_redes(classe="rede", com_email=False):
    itens = []
    redes = REDES + ([("E-mail", f"mailto:{EMAIL_SUGESTAO}")] if com_email and EMAIL_SUGESTAO else [])
    for nome, url in redes:
        if not url:
            continue
        svg = f'<svg viewBox="0 0 24 24" fill="none">{ICONES_REDES.get(nome, "")}</svg>'
        itens.append(
            f'<a class="{classe}" href="{escapar(url)}"'
            + ("" if url.startswith("mailto:") else ' target="_blank" rel="noopener"') + ' '
            f'aria-label="Universo Tec — {nome}" title="{nome}">{svg}<span>{nome}</span></a>'
        )
    return "\n        ".join(itens)


def montar_botoes_sugestao():
    botoes = montar_redes("botao botao-ghost")
    if EMAIL_SUGESTAO:
        assunto = "Sugestão de produto pro Universo Tec"
        botoes += (
            f'\n        <a class="botao" href="mailto:{escapar(EMAIL_SUGESTAO)}?subject={quote(assunto)}">'
            f'<svg viewBox="0 0 24 24" fill="none">{ICONES_REDES["E-mail"]}</svg>Mandar e-mail</a>'
        )
    return botoes


def link_rede(nome):
    return next((url for n, url in REDES if n == nome and url), "")


def main():
    # segurança: produto sem link ou preço nunca vai pro site
    produtos = [p for p in carregar_produtos() if p.get("link") and p.get("preco")]

    cards = "".join(montar_card(i, p) for i, p in enumerate(produtos))
    filtros = montar_filtros(produtos)
    agora = datetime.now(BRASILIA)

    tiktok = link_rede("TikTok")
    cta_rede = (
        f'<a class="botao botao-ghost" href="{escapar(tiktok)}" target="_blank" rel="noopener">'
        f'<svg viewBox="0 0 24 24" fill="none">{ICONES_REDES["TikTok"]}</svg>Ver os vídeos</a>'
        if tiktok else ""
    )
    tem_testados = any(p.get("testado") for p in produtos)

    with open(ARQUIVO_TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()

    trocas = {
        "<!--PRODUTOS-->": cards,
        "<!--FILTROS-->": filtros,
        "<!--TOTAL-->": str(len(produtos)),
        "<!--NUM_CATS-->": str(len({p["cat"] for p in produtos})),
        "<!--ATUALIZADO-->": agora.strftime("%d/%m"),
        "<!--ATUALIZADO_ISO-->": agora.isoformat(timespec="minutes"),
        "<!--TESTADOS-->": montar_testados(produtos),
        "<!--NAV_TESTADOS-->": '<a href="#testados">Testados</a>' if tem_testados else "",
        "<!--REDES-->": montar_redes(com_email=True),
        "<!--SUGESTAO_BOTOES-->": montar_botoes_sugestao(),
        "<!--CTA_REDE-->": cta_rede,
    }
    html = template
    for marcador, valor in trocas.items():
        html = html.replace(marcador, valor)

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        f.write(html)

    categorias = sorted({p["cat"] for p in produtos}, key=slug)
    print(f"OK — site gerado com {len(produtos)} produtos em index.html")
    print(f"Filtros: Todos, {', '.join(categorias)}")


if __name__ == "__main__":
    main()
