# FALAE - Arquitetura Oficial

Versão: 1.0
Data: Junho/2026

---

# Objetivo

O FALAE é uma plataforma SaaS para Gestão de Ética, Compliance e Riscos Psicossociais.

Sua arquitetura foi projetada para ser:

* Escalável
* Multiempresa
* Segura
* Auditável
* Fácil de manter

---

# Arquitetura

Toda requisição obrigatoriamente seguirá o fluxo abaixo.

```
Browser

↓

Blueprint

↓

Service

↓

Repository

↓

Banco de Dados
```

---

# Responsabilidade de cada camada

## Blueprint

Responsável apenas por:

* receber a requisição
* validar acesso
* chamar o Service
* retornar Template ou JSON

Nunca deverá possuir SQL.

Nunca deverá conter regra de negócio.

---

## Service

Responsável por:

* regras de negócio
* validações
* cálculos
* integração entre módulos

Nunca deverá conhecer HTML.

---

## Repository

Responsável exclusivamente por acessar o banco de dados.

Todo SQL ficará nesta camada.

---

## Core

Contém recursos compartilhados:

* Logger
* Request Context
* Exception Handler
* Segurança
* Permissões
* Validadores

---

# Multiempresa

Toda consulta deverá respeitar o isolamento por empresa.

Nenhuma empresa poderá visualizar dados de outra empresa.

---

# Auditoria

Toda ação crítica deverá gerar auditoria.

Exemplos:

* Login
* Criação de ocorrência
* Alteração de status
* Exclusões
* Atualizações

---

# Logs

Todo erro deverá ser registrado.

Toda requisição possuirá Request-ID.

Nunca exibir traceback ao usuário.

---

# Princípios

1. Segurança antes da conveniência.
2. Código simples.
3. Separação de responsabilidades.
4. Arquitetura preparada para crescimento.
5. Valor para o cliente acima de quantidade de funcionalidades.
