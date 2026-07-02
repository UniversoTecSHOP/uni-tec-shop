# Universo Tec 🔵 — Projeto

Site de afiliados de tecnologia da Shopee, com automação.

Um script em Python consome a **Shopee Affiliate API**, atualiza a lista de produtos e gera as páginas do site, publicadas via **GitHub Pages**.

---

## Como funciona

1. O **GitHub Actions** roda o script Python de forma agendada.
2. O script chama a **Shopee Affiliate API** e busca produtos por categoria.
3. Os produtos (nome, foto, preço, link de afiliado) são salvos em `dados/produtos.json`.
4. O script gera as páginas HTML em `site/`.
5. O **GitHub Pages** publica o site.

---

## Estrutura de pastas

```
uni-tec-shop/
├── scripts/            → código Python
│   ├── coletar.py         (chama a API e salva os produtos)
│   └── gerar_site.py      (monta o HTML a partir dos produtos)
├── dados/              → dados do projeto
│   └── produtos.json      (lista de produtos coletados)
├── site/               → o site em si (o que vai pro ar)
│   ├── index.html
│   ├── css/
│   └── assets/            (logo, imagens)
├── .github/workflows/  → automação (agendamento do GitHub Actions)
│   └── automacao.yml
├── .env.exemplo        → modelo de credenciais (SEM as chaves reais)
├── .gitignore          → o que o Git deve ignorar
├── requirements.txt    → bibliotecas Python usadas
└── README.md
```

---

## Credenciais (IMPORTANTE)

As chaves da Shopee (**App ID** e **App Secret**) **NUNCA** ficam no código.

- Localmente: ficam num arquivo `.env` (que o `.gitignore` ignora).
- No GitHub: ficam em **Settings → Secrets and variables → Actions**.

> ⚠️ Nunca commitar `.env`, App ID, App Secret ou qualquer senha.

---

## Status

- [x] Nicho, nome, logo, cor
- [x] Conta de afiliado
- [x] Repositório GitHub
- [x] Estrutura de pastas
- [ ] Acesso à Open API (App ID + Secret) — **em análise**
- [ ] Script de coleta funcionando
- [ ] Geração do site
- [ ] Publicação no GitHub Pages

---

*Projeto pessoal — Universo Tec. Tecnologia que conecta sua vida.*
