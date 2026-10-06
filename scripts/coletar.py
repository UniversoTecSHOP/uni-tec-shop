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
# PRODUTOS FIXOS — os que VOCÊ testou. Sempre aparecem, no topo, com selo
# "Testado". Campos:
#   "link":  link de afiliado (s.shopee.com.br/...). SEM link o produto não
#            aparece no site — fica guardado aqui esperando.
#   "nota":  sua opinião sincera em 1-2 frases (aparece no card de destaque)
#   "video": vídeo do produto. Pode ser um arquivo comprimido em
#            site/assets/videos/ (abre um player no próprio site) ou um link
#            do TikTok/YouTube (abre em outra aba).
#   "capa":  imagem mostrada antes do vídeo começar (opcional)
# ---------------------------------------------------------------------------
PRODUTOS_FIXOS = [
    {
        "cat": "Teclado",
        "nome": "Teclado Gamer RGB Sem Fio ABNT2 Bateria Durável Iluminação LED K518",
        "preco": "259,00",
        "imagem": "site/assets/teclado-golden-yang.jpg",
        "link": "https://s.shopee.com.br/gQcqUIhGy",
        "testado": True,
        "nota": "",                                       # sua opinião sincera (opcional)
        "video": "site/assets/videos/teclado-golden-yang.mp4",
        "capa": "site/assets/videos/teclado-golden-yang-capa.jpg",
    },
    {
        "cat": "Mouse",
        "nome": "Mouse Pad Gamer Grande Borda Costurada Estampa Oriental",
        "preco": "20,99",
        "imagem": "site/assets/mousepad-oriental.jpg",
        "link": "https://s.shopee.com.br/9pcvTA8BO4",
        "testado": True,
        "nota": "Comprei e uso todo dia. Borda costurada firme, base que não escorrega e tamanho que cobre mouse e teclado.",
        "video": "site/assets/videos/mousepad-oriental.mp4",
        "capa": "site/assets/videos/mousepad-oriental-capa.jpg",
    },
]

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------
ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

# Cada linha: termo buscado na Shopee  ->  categoria larga (vira filtro no site)
BUSCAS = [
    # Áudio
    {"termo": "fone bluetooth",          "categoria": "Áudio"},
    {"termo": "fone de ouvido com fio",  "categoria": "Áudio"},
    {"termo": "caixa de som bluetooth",  "categoria": "Áudio"},
    {"termo": "headset sem fio",         "categoria": "Áudio"},
    {"termo": "headset com fio",         "categoria": "Áudio"},
    {"termo": "headset gamer com fio",   "categoria": "Áudio"},
    {"termo": "headset gamer sem fio",   "categoria": "Áudio"},

    # Mouse
    {"termo": "mouse sem fio",           "categoria": "Mouse"},
    {"termo": "mouse vertical",          "categoria": "Mouse"},
    {"termo": "mouse gamer",             "categoria": "Mouse"},
    {"termo": "mousepad gamer",          "categoria": "Mouse"},
    {"termo": "mouse com fio gamer",     "categoria": "Mouse"},
    {"termo": "mouse com fio",           "categoria": "Mouse"},
    {"termo": "mouse sem fio gamer",     "categoria": "Mouse"},
    {"termo": "mouse bluetooth",         "categoria": "Mouse"},

    # Teclado
    {"termo": "teclado mecanico",        "categoria": "Teclado"},
    {"termo": "teclado gamer sem fio",   "categoria": "Teclado"},
    {"termo": "teclado gamer com fio",   "categoria": "Teclado"},
    {"termo": "teclado com fio",         "categoria": "Teclado"},
    {"termo": "teclado sem fio",         "categoria": "Teclado"},

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
    {"termo": "pen drive",               "categoria": "Setup"},
    # {"termo": "hub usb",               "categoria": "Setup"},   # desativado

    # Iluminação (desativada por enquanto — descomente para reativar)
    # {"termo": "fita led rgb",          "categoria": "Iluminação"},
    # {"termo": "ring light",            "categoria": "Iluminação"},

    # Vestível
    {"termo": "smartwatch",              "categoria": "Vestível"},
    {"termo": "pulseira smartwatch",     "categoria": "Vestível"},
]

# Quantos produtos pegar de CADA busca (máx. 50)
POR_BUSCA = 6

# Ordenação: 2 = mais vendidos
TIPO_ORDENACAO = 2

# Pausa entre chamadas, para não bater no limite da API
PAUSA_SEGUNDOS = 1

# Trava de segurança: se a API devolver menos que isso (chave vencida, API fora
# do ar...), o script NÃO sobrescreve o produtos.json — o site continua com os
# produtos de ontem em vez de ficar vazio.
MINIMO_PRODUTOS = 40

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


def sem_acento(texto):
    import unicodedata
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode().lower()


def main():
    app_id, app_secret = carregar_credenciais()

    produtos = []
    vistos = set()          # evita o mesmo produto em duas buscas
    contagem = {}           # quantos produtos por categoria

    # produtos fixos entram primeiro (os sem link/preço ficam de fora)
    fixos = [p for p in PRODUTOS_FIXOS if p.get("link") and p.get("preco")]
    for p in PRODUTOS_FIXOS:
        if p not in fixos:
            print(f"  ! fixo sem link ou preço, fora do site por enquanto: {p['nome']}")
    for p in fixos:
        produtos.append(dict(p))
        vistos.add(p["link"])
        contagem[p["cat"]] = contagem.get(p["cat"], 0) + 1
    print(f"{len(fixos)} produto(s) fixo(s) adicionado(s)\n")

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

    n = len(fixos)
    if len(produtos) - n < MINIMO_PRODUTOS:
        raise SystemExit(
            f"ERRO: a API só devolveu {len(produtos) - n} produtos "
            f"(mínimo {MINIMO_PRODUTOS}). produtos.json NÃO foi alterado.\n"
            "Confira as credenciais e se a API está no ar."
        )

    # ordena por categoria, para os cards saírem agrupados
    # (sem acento na comparação, senão "Áudio" vai pro fim da lista)
    # mantém os fixos no topo
    resto = produtos[n:]
    resto.sort(key=lambda p: sem_acento(p["cat"]))
    produtos = produtos[:n] + resto

    os.makedirs(PASTA_DADOS, exist_ok=True)
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    print(f"\nOK — {len(produtos)} produtos salvos em dados/produtos.json")
    print("\nPor categoria:")
    for cat, n in sorted(contagem.items()):
        print(f"  {cat:15} {n}")


if __name__ == "__main__":
    main()
