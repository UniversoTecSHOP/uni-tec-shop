"""
coletar.py — busca produtos de tecnologia na Shopee Affiliate API

Busca por PALAVRAS-CHAVE (definidas abaixo) em vez de pegar os mais vendidos
da loja inteira. Assim só entram produtos do nicho.

As credenciais NUNCA ficam neste arquivo. São lidas do ambiente:
  - Localmente: do arquivo .env (ignorado pelo .gitignore)
  - No GitHub Actions: dos Secrets do repositório

Rodar:  python scripts/coletar.py
"""

import os
import json
import time
import hashlib
import requests

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO — edite aqui para mudar o que aparece no site
# ---------------------------------------------------------------------------
ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

# Cada busca traz produtos daquele termo, marcados com aquela categoria.
# Adicione, remova ou mude os termos livremente.
BUSCAS = [
    {"termo": "fone bluetooth",        "categoria": "Áudio"},
    {"termo": "carregador rapido usb", "categoria": "Carregamento"},
    {"termo": "power bank",            "categoria": "Carregamento"},
    {"termo": "mousepad gamer",        "categoria": "Periféricos"},
    {"termo": "teclado mecanico",      "categoria": "Periféricos"},
    {"termo": "suporte notebook",      "categoria": "Setup"},
    {"termo": "fita led rgb",          "categoria": "Iluminação"},
    {"termo": "smartwatch",            "categoria": "Vestível"},
]

# Quantos produtos pegar de CADA busca (máx. 50)
POR_BUSCA = 4

# Ordenação: 2 = mais vendidos
TIPO_ORDENACAO = 2

# Pausa entre chamadas, para não bater no limite da API
PAUSA_SEGUNDOS = 1

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")
ARQUIVO_SAIDA = os.path.join(PASTA_DADOS, "produtos.json")


def carregar_credenciais():
    """Lê App ID e Secret do ambiente. Nunca escreva as chaves aqui."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    app_id = os.environ.get("SHOPEE_APP_ID")
    app_secret = os.environ.get("SHOPEE_APP_SECRET")

    if not app_id or not app_secret:
        raise SystemExit(
            "ERRO: credenciais não encontradas.\n"
            "Crie um arquivo .env na raiz do projeto com:\n"
            "  SHOPEE_APP_ID=seu_app_id\n"
            "  SHOPEE_APP_SECRET=sua_senha\n"
        )
    return app_id, app_secret


def montar_payload(termo):
    """Monta o corpo da requisição GraphQL para uma palavra-chave."""
    query = (
        '{productOfferV2('
        f'keyword:"{termo}",'
        f'sortType:{TIPO_ORDENACAO},'
        f'page:1,'
        f'limit:{POR_BUSCA}'
        ')'
        '{nodes{productName priceMin imageUrl offerLink commissionRate}}}'
    )
    corpo = {"query": query, "operationName": None, "variables": {}}
    # sem espaços: o payload assinado deve ser IDÊNTICO ao enviado
    return json.dumps(corpo, separators=(",", ":"))


def assinar(app_id, app_secret, payload, timestamp):
    """Signature = SHA256(AppId + Timestamp + Payload + Secret)"""
    base = f"{app_id}{timestamp}{payload}{app_secret}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def chamar_api(app_id, app_secret, termo):
    """Faz uma busca por palavra-chave e devolve os produtos encontrados."""
    payload = montar_payload(termo)
    timestamp = int(time.time())          # segundos Unix
    assinatura = assinar(app_id, app_secret, payload, timestamp)

    headers = {
        "Content-Type": "application/json",
        "Authorization": (
            f"SHA256 Credential={app_id},"
            f"Timestamp={timestamp},"
            f"Signature={assinatura}"
        ),
    }

    resposta = requests.post(ENDPOINT, data=payload, headers=headers, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()

    if "errors" in dados:
        print(f"  ! erro na busca '{termo}': {dados['errors']}")
        return []

    return dados["data"]["productOfferV2"]["nodes"]


def traduzir(node, categoria):
    """Converte a resposta da API para o formato que o site usa."""
    preco = float(node.get("priceMin") or 0)
    return {
        "cat": categoria,
        "nome": node.get("productName", "").strip(),
        "preco": f"{preco:.2f}".replace(".", ","),
        "imagem": node.get("imageUrl", ""),
        "link": node.get("offerLink", "#"),
    }


def main():
    app_id, app_secret = carregar_credenciais()

    produtos = []
    vistos = set()   # evita produto repetido entre buscas diferentes

    for busca in BUSCAS:
        termo = busca["termo"]
        categoria = busca["categoria"]
        print(f"Buscando: {termo} ...")

        for node in chamar_api(app_id, app_secret, termo):
            link = node.get("offerLink", "")
            if link and link in vistos:
                continue
            vistos.add(link)
            produtos.append(traduzir(node, categoria))

        time.sleep(PAUSA_SEGUNDOS)

    os.makedirs(PASTA_DADOS, exist_ok=True)
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    print(f"\nOK — {len(produtos)} produtos salvos em dados/produtos.json")


if __name__ == "__main__":
    main()
