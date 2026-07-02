"""
coletar.py — busca produtos na Shopee Affiliate API e salva em dados/produtos.json

⚠️ ESQUELETO: ainda não funciona de verdade — está esperando a API ser liberada.
Quando o App ID + Secret chegarem, a gente preenche a parte da assinatura e da chamada.

Fluxo pretendido:
1. Ler App ID e Secret do ambiente (.env local ou Secrets do GitHub)
2. Montar a assinatura SHA256 exigida pela Shopee
3. Chamar a API pedindo produtos por categoria
4. Salvar nome, foto, preço e link de afiliado em dados/produtos.json
"""

import os
import json

# Caminho onde os produtos serão salvos
ARQUIVO_SAIDA = os.path.join("dados", "produtos.json")


def main():
    # TODO: quando a API liberar, ler credenciais aqui
    # app_id = os.environ.get("SHOPEE_APP_ID")
    # app_secret = os.environ.get("SHOPEE_APP_SECRET")

    # TODO: montar assinatura SHA256, chamar a API, tratar resposta
    produtos = []  # por enquanto vazio — vai ser preenchido pela API

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    print(f"OK — {len(produtos)} produtos salvos em {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
