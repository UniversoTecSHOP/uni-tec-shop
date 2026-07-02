"""
gerar_site.py — lê dados/produtos.json e gera as páginas HTML em site/

⚠️ ESQUELETO: versão inicial. A gente vai completar quando houver produtos reais.

Fluxo pretendido:
1. Ler dados/produtos.json
2. Para cada produto, montar um "card" (foto, nome, preço, botão com link de afiliado)
3. Escrever tudo em site/index.html
"""

import os
import json

ARQUIVO_PRODUTOS = os.path.join("dados", "produtos.json")
ARQUIVO_SITE = os.path.join("site", "index.html")


def carregar_produtos():
    if not os.path.exists(ARQUIVO_PRODUTOS):
        return []
    with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    produtos = carregar_produtos()
    # TODO: montar os cards de produto dentro do HTML
    print(f"OK — {len(produtos)} produtos prontos para o site")


if __name__ == "__main__":
    main()
