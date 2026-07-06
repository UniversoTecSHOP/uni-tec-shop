"""
coletar.py — reúne os produtos e salva em dados/produtos.json

HOJE: usa uma lista de exemplo, pra você ver a mecânica funcionando.
DEPOIS: quando a Open API da Shopee liberar, a função `buscar_da_api()`
        substitui os dados de exemplo pelos produtos reais.

Rodar:  python scripts/coletar.py
"""

import os
import json

# Onde os produtos serão salvos (a pasta dados/ fica na raiz do projeto)
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")
ARQUIVO_SAIDA = os.path.join(PASTA_DADOS, "produtos.json")


# ---------------------------------------------------------------------------
# DADOS DE EXEMPLO (temporário)
# Isto simula o que a API vai devolver, pra testarmos o site desde já.
# ---------------------------------------------------------------------------
def buscar_exemplo():
    return [
        {"cat": "Áudio",        "nome": "Fone Bluetooth com cancelamento de ruído e estojo de carga", "preco": "149,90", "imagem": "", "link": "#"},
        {"cat": "Acessórios",   "nome": "Suporte articulado de mesa para notebook em alumínio",        "preco": "89,00",  "imagem": "", "link": "#"},
        {"cat": "Carregamento", "nome": "Carregador GaN 65W com três saídas e carga rápida",           "preco": "119,90", "imagem": "", "link": "#"},
        {"cat": "Periféricos",  "nome": "Teclado mecânico compacto sem fio com switches silenciosos",  "preco": "214,90", "imagem": "", "link": "#"},
        {"cat": "Iluminação",   "nome": "Fita de LED RGB inteligente com controle por aplicativo",      "preco": "59,90",  "imagem": "", "link": "#"},
        {"cat": "Mobilidade",   "nome": "Power bank 20000mAh com display digital e carga rápida",       "preco": "134,90", "imagem": "", "link": "#"},
    ]


# ---------------------------------------------------------------------------
# CHAMADA REAL À API (encaixe — completar quando a chave chegar)
# ---------------------------------------------------------------------------
def buscar_da_api():
    """
    Quando a Open API liberar, esta função vai:
    1. Ler App ID e App Secret do ambiente (nunca escrever a chave aqui!)
    2. Montar a assinatura de segurança exigida pela Shopee
    3. Chamar a API pedindo produtos por categoria
    4. Devolver a lista no MESMO formato de buscar_exemplo()
       (cat, nome, preco, imagem, link)

    Deixado comentado de propósito — ativar só com a documentação oficial.
    """
    # app_id = os.environ.get("SHOPEE_APP_ID")
    # app_secret = os.environ.get("SHOPEE_APP_SECRET")
    # ... (assinatura + requisição) ...
    raise NotImplementedError("API ainda não liberada — usando dados de exemplo por enquanto.")


def main():
    # Enquanto a API não libera, usamos o exemplo.
    # Quando liberar, troca esta linha por:  produtos = buscar_da_api()
    produtos = buscar_exemplo()

    os.makedirs(PASTA_DADOS, exist_ok=True)
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

    print(f"OK — {len(produtos)} produtos salvos em dados/produtos.json")


if __name__ == "__main__":
    main()
