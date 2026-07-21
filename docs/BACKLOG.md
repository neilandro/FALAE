# FALAE - Product Backlog

Versão: 1.0

---

# Visão do Produto

O FALAE é uma plataforma SaaS especializada em Ética, Compliance e Gestão de Riscos Psicossociais, desenvolvida para empresas, consultorias de SST e organizações que buscam atender às exigências legais, fortalecer sua cultura organizacional e transformar denúncias em ações de melhoria.

---

# Objetivo da Versão 1.0

Disponibilizar uma plataforma completa para:

* Receber denúncias anônimas.
* Gerenciar ocorrências.
* Acompanhar investigações.
* Produzir evidências.
* Gerar indicadores gerenciais.
* Manter histórico e auditoria completos.

---

# Roadmap

## Sprint 1 — Fundação

### Objetivo

Criar a base do sistema.

### Entregas

* [x] Estrutura Flask
* [x] Banco de Dados
* [x] Login
* [x] Multiempresa
* [x] Canal Público
* [x] Cadastro de Empresas
* [x] Cadastro de Usuários
* [x] Cadastro de Unidades
* [x] Cadastro de Setores

---

## Sprint 2 — Arquitetura Corporativa

### Objetivo

Preparar o sistema para crescer com segurança.

### Entregas

* [x] Application Factory
* [x] Blueprints
* [x] Config
* [x] Extensions
* [x] Logger
* [x] Request Context
* [x] Request-ID
* [x] Exception Handler
* [ ] Repository Pattern
* [ ] Service Pattern
* [ ] Audit Service
* [ ] Banco versionado (Migrations)

---

## Sprint 3 — Gestão de Ocorrências

### Objetivo

Transformar denúncias em ocorrências gerenciáveis.

### Funcionalidades

* [ ] Timeline da ocorrência
* [ ] Responsável
* [ ] Alteração de status
* [ ] Criticidade
* [ ] Categoria
* [ ] Histórico
* [ ] Comentários internos
* [ ] Encerramento

---

## Sprint 4 — Evidências

### Objetivo

Centralizar todas as informações da investigação.

### Funcionalidades

* [ ] Upload de documentos
* [ ] Fotos
* [ ] Vídeos
* [ ] Áudios
* [ ] Parecer técnico
* [ ] Plano de ação
* [ ] Pendências

---

## Sprint 5 — Dashboard Executivo

### Objetivo

Gerar inteligência para tomada de decisão.

### Funcionalidades

* [ ] Indicadores
* [ ] Gráficos
* [ ] Heatmap por unidade
* [ ] Heatmap por setor
* [ ] Ranking de categorias
* [ ] Tempo médio de resolução
* [ ] Exportação Excel
* [ ] Exportação PDF

---

## Sprint 6 — Compliance

### Objetivo

Garantir rastreabilidade.

### Funcionalidades

* [ ] Auditoria
* [ ] Histórico completo
* [ ] Logs inteligentes
* [ ] SLA
* [ ] Trilhas de aprovação

---

## Sprint 7 — Integrações

### Objetivo

Permitir comunicação com outros sistemas.

### Funcionalidades

* [ ] API REST
* [ ] Webhooks
* [ ] Importação de colaboradores
* [ ] Exportações
* [ ] Integrações com sistemas de SST

---

## Sprint 8 — Inteligência

### Objetivo

Agregar valor estratégico.

### Funcionalidades

* [ ] Classificação automática de ocorrências
* [ ] Índice de risco psicossocial
* [ ] Tendências
* [ ] Alertas inteligentes
* [ ] Relatórios gerenciais

---

# Backlog Futuro

## Aplicativo Mobile

* [ ] Android
* [ ] iOS

---

## Inteligência Artificial

* [ ] Sugestão automática de categoria
* [ ] Apoio à investigação
* [ ] Resumos de ocorrências
* [ ] Identificação de padrões

---

## Consultorias de SST

* [ ] Gestão de múltiplas empresas
* [ ] Painel consolidado
* [ ] Indicadores por cliente
* [ ] Portal da consultoria

---

# Critérios de Qualidade

Toda funcionalidade será considerada concluída somente quando possuir:

* Arquitetura compatível com o padrão do projeto.
* Service.
* Repository.
* Logs.
* Auditoria (quando aplicável).
* Tratamento de exceções.
* Isolamento entre empresas.
* Teste funcional realizado.

---

# Visão de Longo Prazo

O objetivo do FALAE é tornar-se uma plataforma de referência nacional em Gestão de Ética, Compliance e Riscos Psicossociais, atendendo empresas, consultorias e profissionais de SST com foco em segurança, rastreabilidade, inteligência e simplicidade.

## Sprint 7 — Produtividade

* [x] US-007.1 — Pesquisa por protocolo
* [x] US-007.2 — Filtro por status
* [x] US-007.3 — Filtro por categoria
* [x] US-007.4 — Filtro por criticidade
* [x] US-007.5 — Filtro por unidade
* [x] US-007.6 — Filtro por período
* [x] US-007.7 — Ordenação da listagem
* [x] US-007.8 — Paginação

## Sprint 8 — Refatoração Arquitetural

### Objetivo

Reorganizar a arquitetura do módulo de denúncias, separando responsabilidades entre Blueprint, Service e Repository, preservando integralmente o comportamento do sistema.

### User Stories

* [ ] US-008.1 — Criar DenunciaRepository
* [ ] US-008.2 — Criar DenunciaService
* [ ] US-008.3 — Refatorar empresa_denuncias()
* [ ] US-008.4 — Testes de regressão

## Sprint 9 — Qualidade e Confiabilidade

- [x] US-009.1 — Configurar pytest
- [x] US-009.2 — Teste de criação da aplicação
- [x] US-009.3 — Instalar pytest-mock

### Observação
A Sprint 9 criou a fundação inicial de testes automatizados. Testes mais completos de Repository, Service e rotas serão evoluídos em sprints futuras.