# Papirus Breeze

Temas pessoais **Light e Dark para KDE Plasma 6**, reunidos em um único
repositório. Versão dos pacotes: **1.0.13**.

O conjunto usa Breeze, ícones Papirus com variantes vermelhas e destaque
**vermelho `#E93D58`**. Inclui desktop, painéis, wallpaper adaptativo, bloqueio,
configuração de wallpaper do login, Konsole e Fish.

![Ícone do lançador: hexágono vermelho com centro transparente](light/assets/icons/PapirusBreezeLight/scalable/apps/papirus-breeze-launcher.svg)

| Recurso | Light | Dark |
| --- | --- | --- |
| Tema global | `com.delta.papirus-breeze-light` | `com.delta.papirus-breeze-dark` |
| Paleta / ícones | `PapirusBreezeLight` | `PapirusBreezeDark` |
| Estilo Qt / Plasma | Breeze / `PapirusBreezeRed` | Breeze / `PapirusBreezeRed` |
| Decoração | Amy Light Aurorae | Amy Papirus Dark |
| GTK | Breeze | Breeze-Dark |
| Wallpaper | Moe, pacote adaptativo | MoeDark, pacote adaptativo |
| Cursor do mouse | Breeze Light, 18 px | Breeze escuro, 18 px |
| Konsole | Fundo branco | Fundo escuro |

As duas variantes têm pastas e ícones do sistema vermelhos, Dolphin vermelho,
lançador em SVG com centro transparente e cursor de texto vermelho animado.
O layout incluído cria um painel de **32 px por monitor, sem aplicativos fixados**.
O Fish mostra três linhas sobre o sistema, com prompt Pure compacto quando disponível.

## Começar

Requisitos: KDE Plasma 6, Python 3.9+, Breeze/Aurorae, Papirus/Papirus-Dark e as
ferramentas de configuração do KDE. Fish e JetBrainsMono Nerd Font são necessários
para o terminal incluído. Veja a lista completa em [Instalação](docs/INSTALLATION.md).

Execute a partir desta pasta, como usuário normal, dentro da sessão Plasma:

```bash
# Disponibilizar os dois temas, sem aplicar aparência ou redefinir painéis.
python3 light/install.py
python3 dark/install.py

# Aplicar uma variante; o ícone dos lançadores existentes também é atualizado.
python3 light/install.py --apply
# Ou: python3 dark/install.py --apply
```

Para também recriar os painéis conforme o pacote:

```bash
python3 light/install.py --apply --layout
```

**`--layout` remove os painéis atuais.** Sem essa opção, a estrutura dos painéis
é preservada. A aparência do login tem instalação administrativa separada. Para acompanhar
as trocas Light/Dark de um usuário, instale os dois perfis e o observador:

```bash
python3 tools/install-login.py --follow-user "$USER" --dry-run
sudo python3 tools/install-login.py --follow-user "$USER"
```

Veja as diferenças entre Plasma Login Manager e SDDM no guia de instalação.

## Documentação

- [Instalação, troca de tema e login](docs/INSTALLATION.md).
- [Aparência, painéis, ícones, Konsole e Fish](docs/APPEARANCE.md).
- [Personalizar SVG, cores, wallpaper e terminal](docs/CUSTOMIZATION.md).
- [Arquitetura e arquivos de configuração](docs/ARCHITECTURE.md).
- [Backups, restauração e solução de problemas](docs/RESTORE_AND_TROUBLESHOOTING.md).
- [Desenvolvimento, testes, distribuição e GitHub Desktop](docs/DEVELOPMENT.md).
- [Históricos anteriores e migração das pastas](docs/MIGRATION.md).
- [Alterações conhecidas](CHANGELOG.md) e [créditos/licenças](THIRD_PARTY.md).
- Guias independentes das variantes: [Light](light/README.md) e [Dark](dark/README.md).

## Organização

```text
papirus-breeze/
├── light/             # Pacote Light independente, instalador e manifesto próprios
├── dark/              # Pacote Dark independente, instalador e manifesto próprios
├── docs/              # Documentação compartilhada
├── tools/project.py   # Manutenção das duas variantes
├── CHANGELOG.md
├── THIRD_PARTY.md
└── LICENSE
```

Há somente um repositório Git, nesta raiz. As variantes continuam instaláveis e
empacotáveis separadamente. Os assets iguais permanecem em ambos os pacotes para
que cada arquivo de distribuição seja autossuficiente.

## Verificar e distribuir

```bash
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
```

Os arquivos são gerados em `light/dist/` e `dark/dist/`. A ação `check` valida
integridade; a verificação das dependências da sessão é feita com
`python3 light/install.py --check` ou o equivalente Dark.

Os scripts e a composição própria usam GPL-3.0-only. Componentes de terceiros
mantêm suas licenças, incluindo as imagens CC-BY-SA-4.0 e recursos KDE LGPL.
Confira [THIRD_PARTY.md](THIRD_PARTY.md) antes da redistribuição.
