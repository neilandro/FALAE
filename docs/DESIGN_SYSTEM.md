# Padrões de Desenvolvimento

## Filosofia da FALAE UI

Antes de criar um novo componente, deve-se responder às seguintes perguntas:

1. Este componente será reutilizado em outras telas?
2. Ele possui uma única responsabilidade?
3. Existe algum componente semelhante que possa ser reutilizado?
4. A funcionalidade deve ser implementada primeiro e abstraída depois?

### Princípios

* Desenvolver primeiro a funcionalidade.
* Validar o funcionamento.
* Somente depois transformar em componente reutilizável.
* Cada componente deve possuir um único arquivo.
* Cada componente deve possuir uma única macro principal.
* Componentes devem seguir o princípio da responsabilidade única (Single Responsibility Principle).

# Estratégia de Desenvolvimento

O desenvolvimento do FALAE seguirá sempre a seguinte ordem:

1. Definir o problema de negócio.
2. Implementar a funcionalidade.
3. Validar com testes.
4. Refatorar quando necessário.
5. Transformar em componente reutilizável.
6. Atualizar a documentação.
7. Liberar a funcionalidade.

Esta estratégia tem como objetivo reduzir retrabalho, evitar abstrações prematuras e garantir que todos os componentes da FALAE UI representem necessidades reais do produto.
