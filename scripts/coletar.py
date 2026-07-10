"""
coletar.py — busca produtos de tecnologia na Shopee Affiliate API

As buscas são específicas (ex: "mouse vertical"), mas cada uma recebe uma
CATEGORIA LARGA (ex: "Mouse"). É a categoria larga que vira botão de filtro no site.

Para mudar o que aparece: edite a lista BUSCAS abaixo.

Credenciais nunca ficam aqui. São lidas do ambiente:
  - Local: arquivo .env (ignorado pelo .gitignore)
  - GitHub Actions: Secrets do repositório

Rodar:  python scripts/coletar.py
"""

import os
import json
import time
import hashlib
import requests

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------
ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

# Cada linha: termo buscado na Shopee  ->  categoria larga (vira filtro no site)
BUSCAS = [
    # Áudio
    {"termo": "fone bluetooth",          "categoria": "Áudio"},
    {"termo": "fone de ouvido com fio",  "categoria": "Áudio"},
    {"termo": "headset gamer sem fio",   "categoria": "Áudio"},
    {"termo": "caixa de som bluetooth",  "categoria": "Áudio"},

    # Mouse
    {"termo": "mouse sem fio",           "categoria": "Mouse"},
    {"termo": "mouse vertical",          "categoria": "Mouse"},
    {"termo": "mouse gamer",             "categoria": "Mouse"},
    {"termo": "mousepad gamer",          "categoria": "Mouse"},

    # Teclado
    {"termo": "teclado mecanico",        "categoria": "Teclado"},
    {"termo": "teclado gamer sem fio",   "categoria": "Teclado"},

    # Gamer
    {"termo": "controle pc sem fio",     "categoria": "Gamer"},
    {"termo": "controle para celular",   "categoria": "Gamer"},

    # Carregamento
    {"termo": "power bank",              "categoria": "Carregamento"},
    {"termo": "carregador rapido usb",   "categoria": "Carregamento"},
    {"termo": "adaptador de tomada usb", "categoria": "Carregamento"},

    # Cabos
    {"termo": "cabo lightning",          "categoria": "Cabos"},
    {"termo": "cabo hdmi",               "categoria": "Cabos"},
    {"termo": "cabo usb tipo c",         "categoria": "Cabos"},

    # Celular
    {"termo": "capinha de celular",      "categoria": "Celular"},
    {"termo": "pelicula protetora",      "categoria": "Celular"},
    {"termo": "suporte celular carro",   "categoria": "Celular"},

    # Setup
    {"termo": "suporte notebook",        "categoria": "Setup"},
    {"termo": "hd externo",              "categoria": "Setup"},
    {"termo": "webcam",                  "categoria": "Setup"},
    {"termo": "hub usb",                 "categoria": "Setup"},

    # Iluminação
    {"termo": "fita led rgb",            "categoria": "Iluminação"},
    {"termo": "ring light",              "categoria": "Iluminação"},

    # Vestível
    {"termo": "smartwatch",              "categoria": "Vestível"},
    {"termo": "pulseira smartwatch",     "categoria": "Vestível"},
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
    return json.dumps(corpo, separators=(",", ":"))


def assinar(app_id, app_secret, payload, timestamp):
    """Signature = SHA256(AppId + Timestamp + Payload + Secret)"""
    base = f"{app_id}{timestamp}{payload}{app_secret}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def chamar_api(app_id, app_secret, termo):
    payload = montar_payload(termo)
    timestamp = int(time.time())
    assinatura = assinar(app_id, app_secret, payload, timestamp)

    headers = {
        "Content-Type": "application/json",
        "Authorization": (
            f"SHA256 Credential={app_id},"
            f"Timestamp={timestamp},"
            f"Signature={assinatura}"
        ),
    }

    try:
        resposta = requests.post(ENDPOINT, data=payload, headers=headers, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
    except Exception as e:
        print(f"  ! falhou '{termo}': {e}")
        return []

    if "errors" in dados:
        print(f"  ! erro na busca '{termo}': {dados['errors']}")
        return []

    return dados["data"]["productOfferV2"]["nodes"]


def traduzir(node, categoria):
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
    vistos = set()          # evita o mesmo produto em duas buscas
    contagem = {}           # quantos produtos por categoria

    for busca in BUSCAS:
        termo = busca["termo"]
        categoria = busca["categoria"]
        print(f"Buscando: {termo:28} [{categoria}]")

        for node in chamar_api(app_id, app_secret, termo):
            link = node.get("offerLink", "")
            if link and link in vistos:
                continue
            vistos.add(link)
            produtos.append(traduzir(node, categoria))
            contagem[categoria] = contagem.get(categoria, 0) + 1

        time.sleep(PAUSA_SEGUNDOS)

    # ordena por categoria, para os cards saírem agrupados
    produtos.sort(key=lambda p: p["cat"])

    os.makedirs(PASTA_DADOS, exist_ok=True)
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    print(f"\nOK — {len(produtos)} produtos salvos em dados/produtos.json")
    print("\nPor categoria:")
    for cat, n in sorted(contagem.items()):
        print(f"  {cat:15} {n}")


if __name__ == "__main__":
    main()
