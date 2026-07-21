# Fluxo Git do FALAE

## Branches

- `main`: versão estável e preparada para produção.
- `develop`: integração das funcionalidades em desenvolvimento.
- `feature/*`: desenvolvimento de funcionalidades isoladas.
- `fix/*`: correções de erros.

## Fluxo de trabalho

1. Criar uma branch a partir de `develop`.
2. Desenvolver e testar a alteração.
3. Enviar a branch para o GitHub.
4. Abrir Pull Request para `develop`.
5. Após validação, integrar `develop` à `main` por Pull Request.

Não realizar push direto para a branch `main`.