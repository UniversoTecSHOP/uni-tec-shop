<h1 align="center">Universo Tec 🔵</h1>

<p align="center">
  <b>Achados e ofertas de tecnologia.</b><br>
  Curadoria de produtos tech com os melhores preços da Shopee.
</p>

---

### 🚀 Sobre

O **Universo Tec** garimpa e reúne os melhores achados de tecnologia — gadgets, acessórios e ofertas — pra facilitar sua vida na hora de comprar.

- 🔎 Curadoria de produtos tech
- 🏷️ Foco em ofertas e bons preços
- ⚡ Atualizado com automação própria

---

### 🛠️ Feito com

`Python` · `GitHub Actions` · `GitHub Pages`

---

<p align="center">
  <i>Tecnologia que conecta sua vida.</i>
</p>

---

### 🔧 Atualizar na mão

```
cd "C:\Users\capta\OneDrive\Desktop\uni-tec-shop"
python scripts/coletar.py
python scripts/gerar_site.py
git status        # confira: NADA de .env nem vídeo na lista
git add .
git commit -m "Atualiza produtos"
git push
```

- Produto que você testou: adicione em `PRODUTOS_FIXOS` no `scripts/coletar.py` (com `nota` e `video`).
- Redes sociais e e-mail de sugestão: topo do `scripts/gerar_site.py`.
- Link já filtrado pra mandar nas redes: `.../uni-tec-shop/?cat=mouse` ou `?q=fone`.
