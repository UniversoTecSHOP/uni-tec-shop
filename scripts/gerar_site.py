"""
gerar_site.py — lê dados/produtos.json e monta o site (index.html)

Além dos cards, agora gera os BOTÕES DE FILTRO por categoria.

Rodar:  python scripts/gerar_site.py
        (rode o coletar.py antes, pra ter os produtos)
"""

import os
import json

RAIZ = os.path.join(os.path.dirname(__file__), "..")
ARQUIVO_PRODUTOS = os.path.join(RAIZ, "dados", "produtos.json")
ARQUIVO_SAIDA = os.path.join(RAIZ, "index.html")
ARQUIVO_TEMPLATE = os.path.join(os.path.dirname(__file__), "template.html")


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
    return (texto.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace('"', "&quot;"))


def montar_filtros(produtos):
    """Cria os botões de filtro, um por categoria, com a contagem."""
    contagem = {}
    for p in produtos:
        contagem[p["cat"]] = contagem.get(p["cat"], 0) + 1

    botoes = [
        f'<button class="filtro ativo" data-filtro="todos">'
        f'{icone("todos")}Todos <span class="filtro-num">{len(produtos)}</span></button>'
    ]
    for cat in sorted(contagem):
        s = slug(cat)
        botoes.append(
            f'<button class="filtro" data-filtro="{s}">'
            f'{icone(s)}{escapar(cat)} <span class="filtro-num">{contagem[cat]}</span></button>'
        )
    return "\n      ".join(botoes)


def montar_card(indice, p):
    numero = str(indice + 1).zfill(2)
    reais, _, centavos = p["preco"].partition(",")
    nome = escapar(p["nome"])

    if p.get("imagem"):
        img_html = f'<img src="{p["imagem"]}" alt="{nome}" loading="lazy">'
    else:
        img_html = '<span class="placeholder">IMAGEM DO PRODUTO</span>'

    return f"""
      <article class="card" data-cat="{slug(p['cat'])}">
        <span class="card-index">{numero}</span>
        <button class="card-fav" data-id="{indice}" title="Favoritar" aria-label="Favoritar">{HEART_SVG}</button>
        <div class="card-img">{img_html}</div>
        <div class="card-body">
          <div class="card-cat">{escapar(p['cat'])}</div>
          <h3 class="card-name">{nome}</h3>
          <div class="card-foot">
            <div class="card-price">R$ {reais}<span class="cents">,{centavos}</span></div>
            <a class="card-link" href="{p['link']}" target="_blank" rel="noopener">Ver {SETA_SVG}</a>
          </div>
        </div>
      </article>"""


def main():
    produtos = carregar_produtos()

    cards = "".join(montar_card(i, p) for i, p in enumerate(produtos))
    filtros = montar_filtros(produtos)

    with open(ARQUIVO_TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()

    html = template.replace("<!--PRODUTOS-->", cards)
    html = html.replace("<!--FILTROS-->", filtros)
    html = html.replace("<!--TOTAL-->", str(len(produtos)))

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        f.write(html)

    categorias = sorted({p["cat"] for p in produtos})
    print(f"OK — site gerado com {len(produtos)} produtos em index.html")
    print(f"Filtros: Todos, {', '.join(categorias)}")


if __name__ == "__main__":
    main()
