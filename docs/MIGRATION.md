# Migração para o repositório unificado

Em 16 de outubro de 2026, as pastas locais foram reorganizadas:

| Antes, dentro de `Projects/` | Agora, dentro de `Projects/papirus-breeze/` |
| --- | --- |
| `papirus-breeze-light/` | `light/` |
| `papirus-breeze-dark/` | `dark/` |

Os conteúdos foram movidos, incluindo arquivos de distribuição locais ignorados
pelo Git. As cópias instaladas em `~/.local/share/` e as configurações da sessão
não dependem do caminho do repositório e não foram alteradas por essa migração.

## Histórico preservado

Antes de mover as pastas, os dois repositórios estavam sem alterações pendentes.
Foram criados e verificados bundles completos, além de preservados os diretórios
Git originais e logs em:

```text
~/.local/state/papirus-breeze/repository-backups/20261016-141813/
├── papirus-breeze-light.bundle
├── papirus-breeze-dark.bundle
├── light.git/
├── dark.git/
├── light-history.txt
├── dark-history.txt
└── migration.json
```

Esse backup fica fora do repositório e não será publicado. `migration.json`
registra caminhos originais/novos e os HEADs anteriores. Os HEADs na migração eram:

| Variante | Commit anterior |
| --- | --- |
| Light | `57c76d5` — Torna transparente o centro do ícone do lançador |
| Dark | `8aeb91a` — Torna transparente o centro do ícone do lançador |

Para consultar o histórico antigo em uma pasta separada, pode-se clonar um bundle:

```bash
git clone ~/.local/state/papirus-breeze/repository-backups/20261016-141813/papirus-breeze-light.bundle /caminho/novo/historico-light
```

Escolha um destino novo. Não restaure os diretórios Git antigos dentro das
variantes atuais: o conjunto usa somente o `.git` da raiz.

## Histórico novo

O Git unificado foi iniciado na branch `main`, com commits separados para
estrutura do repositório, importação Light, importação Dark, manutenção e docs.
O conteúdo importado corresponde à versão 1.0.11 e mantém a instalação independente
de cada pacote. Nenhum remoto foi criado ou publicação feita nessa etapa.

Use a nova pasta raiz no GitHub Desktop e atualize atalhos locais que apontavam
para as pastas antigas. Os instaladores resolvem seus assets em relação ao próprio
arquivo, portanto continuam funcionando a partir de qualquer diretório de execução.
