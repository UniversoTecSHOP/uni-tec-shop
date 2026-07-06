"""
gerar_site.py — lê dados/produtos.json e monta o site (index.html)

Rodar:  python scripts/gerar_site.py
        (rode o coletar.py antes, pra ter os produtos)
"""

import os
import json

RAIZ = os.path.join(os.path.dirname(__file__), "..")
ARQUIVO_PRODUTOS = os.path.join(RAIZ, "dados", "produtos.json")
ARQUIVO_SAIDA = os.path.join(RAIZ, "index.html")


def carregar_produtos():
    if not os.path.exists(ARQUIVO_PRODUTOS):
        return []
    with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def montar_card(indice, p):
    """Monta o HTML de um card de produto."""
    numero = str(indice + 1).zfill(2)
    reais, _, centavos = p["preco"].partition(",")

    # imagem: se tiver, usa; senão, mostra o placeholder
    if p.get("imagem"):
        img_html = f'<img src="{p["imagem"]}" alt="{p["nome"]}">'
    else:
        img_html = '<span class="placeholder">IMAGEM DO PRODUTO</span>'

    return f"""
      <article class="card">
        <span class="card-index">{numero}</span>
        <button class="card-fav" data-id="{indice}" title="Favoritar" aria-label="Favoritar">{HEART_SVG}</button>
        <div class="card-img">{img_html}</div>
        <div class="card-body">
          <div class="card-cat">{p["cat"]}</div>
          <h3 class="card-name">{p["nome"]}</h3>
          <div class="card-foot">
            <div class="card-price">R$ {reais}<span class="cents">,{centavos}</span></div>
            <a class="card-link" href="{p["link"]}" target="_blank" rel="noopener">Ver
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </a>
          </div>
        </div>
      </article>"""


HEART_SVG = """<svg viewBox="0 0 24 24" fill="none"><path class="heart-fill" d="M12 20.5l-1.4-1.27C5.4 14.55 2 11.47 2 7.7 2 5.1 4.02 3 6.6 3c1.54 0 3.02.72 3.9 1.86C11.38 3.72 12.86 3 14.4 3 16.98 3 19 5.1 19 7.7c0 3.77-3.4 6.85-8.6 11.53L12 20.5z"/><path d="M12 20.5l-1.4-1.27C5.4 14.55 2 11.47 2 7.7 2 5.1 4.02 3 6.6 3c1.54 0 3.02.72 3.9 1.86C11.38 3.72 12.86 3 14.4 3 16.98 3 19 5.1 19 7.7c0 3.77-3.4 6.85-8.6 11.53L12 20.5z" stroke="#4d8dff" stroke-width="1.7" stroke-linejoin="round"/></svg>"""


def main():
    produtos = carregar_produtos()
    cards = "".join(montar_card(i, p) for i, p in enumerate(produtos))

    # Lê o molde (template) e injeta os cards no lugar do marcador
    with open(os.path.join(os.path.dirname(__file__), "template.html"), "r", encoding="utf-8") as f:
        template = f.read()

    html_final = template.replace("<!--PRODUTOS-->", cards)

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        f.write(html_final)

    print(f"OK — site gerado com {len(produtos)} produtos em index.html")


if __name__ == "__main__":
    main()
