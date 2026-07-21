# CHANGELOG

Todos os marcos relevantes do projeto FALAE são registrados neste documento.

---

# [0.4.0] - Fundação da FALAE UI

**Data:** 29/06/2026

## 🚀 Destaques da Sprint

Esta versão marca uma importante evolução arquitetural do projeto, com a criação da **FALAE UI**, biblioteca de componentes reutilizáveis baseada em macros do Jinja2, além da reorganização completa da estrutura de templates da aplicação.

---

## ✨ Adicionado

### FALAE UI

Criação da biblioteca oficial de componentes reutilizáveis do sistema.

Primeiros componentes implementados:

* `metric_card()`
* `status_badge()`

---

## 🏗 Arquitetura

Reestruturação completa da pasta `templates`.

Nova organização:

```text
templates/
│
├── layouts/
├── components/
│   ├── layout/
│   ├── cards/
│   └── badges/
│
├── public/
├── empresa/
├── admin/
└── errors/
```

Principais mudanças:

* criação da pasta `layouts`;
* criação da pasta `components`;
* criação da pasta `public`;
* organização dos componentes de layout (`sidebar` e `topbar`);
* padronização da estrutura de templates.

---

## ♻️ Refatoração

* Migração do Dashboard para utilização do componente `metric_card()`.
* Migração da tela de denúncias para utilização do componente `status_badge()`.
* Redução de duplicação de HTML utilizando macros do Jinja2.
* Ajuste dos `extends`.
* Ajuste dos `include`.
* Adequação dos `render_template()` à nova arquitetura.

---

## 🎨 Interface

Melhorias visuais:

* Cards padronizados.
* Badges reutilizáveis.
* Dashboard reorganizado.
* Estrutura Enterprise da interface consolidada.

---

## ✅ Testes realizados

Validação completa dos seguintes módulos:

* Login
* Dashboard
* Filtros do Dashboard
* Listagem de denúncias
* Componente `metric_card()`
* Componente `status_badge()`

Todos os testes executados com sucesso.

---

## 📌 Observações

Esta versão representa um marco importante do projeto, estabelecendo a arquitetura oficial de templates e o início da biblioteca de componentes **FALAE UI**, que será utilizada em todas as próximas funcionalidades do sistema.

### ✨ Adicionado

* Pesquisa de denúncias por protocolo utilizando método GET.
* Busca parcial por protocolo (`LIKE`).
* Botão para limpeza rápida dos filtros.
* Preservação do isolamento de dados por empresa durante a pesquisa.
### ✨ Adicionado

#### Sprint 7 — Produtividade

Implementado o primeiro conjunto de filtros da tela de gestão de denúncias:

* Pesquisa por protocolo.
* Filtro por status.
* Filtro por categoria.
* Filtro por criticidade.
* Filtro por unidade.
* Filtro por período.
* Combinação de múltiplos filtros utilizando método GET.
* Preservação dos filtros após a pesquisa.
* Isolamento dos dados por empresa mantido em todas as consultas.

Todos os cenários foram testados com sucesso.
### 🚀 Sprint 7 — Produtividade da Gestão de Denúncias

#### ✨ Adicionado

* Pesquisa por protocolo.
* Filtro por status.
* Filtro por categoria.
* Filtro por criticidade.
* Filtro por unidade.
* Filtro por período.
* Ordenação por data e protocolo.
* Paginação com 20 registros por página.
* Preservação dos filtros durante a navegação entre páginas.

#### ✅ Testes

Todos os cenários de pesquisa, combinação de filtros, ordenação e paginação foram executados e aprovados.
