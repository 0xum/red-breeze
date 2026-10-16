# Papirus Breeze — guia em português brasileiro

[English documentation](README.md) · Tradução opcional em pt-BR.

O inglês é o idioma padrão da documentação, dos comandos de ajuda e das mensagens
dos instaladores. Este guia resume a instalação em português; os guias técnicos
completos em inglês são a referência quando não houver uma tradução equivalente.

## Instalar e remover

O conjunto oferece temas Light e Dark para KDE Plasma 6, com destaque vermelho
`#E93D58`, ícones Papirus vermelhos, wallpapers adaptativos e perfis de terminal.
O ponteiro é escuro no Light e branco no Dark, sempre com 18 px.

Instale as dependências indicadas no [guia de instalação](docs/INSTALLATION.md).
Abra um terminal na raiz do repositório ou na pasta extraída do pacote completo
e execute como usuário normal, sem `sudo`:

```bash
python3 install.py
```

O menu, apresentado em inglês, permite instalar/atualizar, aplicar Light ou Dark,
remover e verificar dependências. Também há comandos diretos:

```bash
python3 install.py check
python3 install.py install
python3 install.py install --apply light
python3 install.py install --apply dark
python3 install.py status
python3 install.py remove --dry-run
python3 install.py remove
```

A instalação cadastra as duas variantes como o par claro/escuro em **Configurações
do Sistema → Configurações rápidas (Quick Settings)**. Reabra essa janela se ela
já estava aberta. Sem `--apply`, a aparência atual e os painéis são mantidos.

Para usar o layout incluído:

```bash
python3 install.py install --apply light --layout
```

**`--layout` remove os painéis atuais** e cria um painel flutuante de 32 px por
monitor conectado, sem aplicativos fixados. Omita essa opção para preservar seus
painéis. A remoção recupera o par anterior do Quick Settings quando disponível,
preserva recursos personalizados e backups e troca um tema Papirus ativo pelo
Breeze correspondente antes de remover os arquivos.

## Login e backups

A aparência do login tem instalação administrativa separada:

```bash
python3 tools/install-login.py --follow-user "$USER" --dry-run
sudo python3 tools/install-login.py --follow-user "$USER"
```

A remoção de usuário não desfaz essa integração administrativa. Consulte
[instalação](docs/INSTALLATION.md#login-appearance) e
[restauração](docs/RESTORE_AND_TROUBLESHOOTING.md#restore-a-snapshot).
Cada operação imprime seu backup. A restauração de snapshots recupera arquivos
inteiros e pode substituir mudanças posteriores; a remoção normal preserva as
configurações de terceiros.

## Desenvolvimento

Edite as fontes do repositório e mantenha as duas variantes coerentes. Depois de
alterações intencionais dentro de um pacote:

```bash
python3 tools/project.py manifest
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
git diff --check
```

O pacote completo fica em `dist/`; os independentes ficam em `light/dist/` e
`dark/dist/`. Os testes usam pastas temporárias e não aplicam temas à sessão.

Consulte os [guias em inglês](README.md#documentation), as
[orientações para agentes](AGENTS.md) e os [créditos/licenças](THIRD_PARTY.md).
Novas contribuições devem ser escritas em inglês. Traduções pt-BR são opcionais,
identificadas como traduções e ligadas à fonte correspondente em inglês.
