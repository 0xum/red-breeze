# Instalação

Todos os exemplos partem da raiz do repositório unificado. Substitua `light` por
`dark` quando quiser a variante escura. Os pacotes também funcionam extraídos
separadamente; nesse caso execute `install.py` dentro da pasta extraída.

## Dependências

- Linux, KDE Plasma 6 e Python 3.9 ou superior.
- Breeze para Qt/Plasma, suporte Aurorae e tema GTK Breeze/Breeze-Dark.
- Papirus e Papirus-Dark; cursores `Breeze_Light` e `breeze_cursors`.
- Noto Sans, tema de sons Ocean; Fish e JetBrainsMono Nerd Font para os perfis do Konsole.
- Para aplicar na sessão: `kwriteconfig6`, `qdbus6`, `plasma-apply-lookandfeel`,
  `plasma-apply-colorscheme`, `plasma-apply-desktoptheme` e `plasma-apply-cursortheme`.
- Konsole com sincronização nativa Light/Dark; ela foi validada no Konsole 26.08.2
  instalado no sistema de origem. Em versões sem o recurso, selecione o perfil manualmente.
- Para o login: Plasma Login Manager, ou SDDM com o tema Breeze instalado.

Instale as dependências pelo gerenciador de pacotes da distribuição. Os scripts
não instalam programas nem fazem downloads. A checagem do instalador cobre temas
base de ícones/cursores e ferramentas de aplicação; não substitui toda a lista acima.

## Conferir antes de aplicar

```bash
python3 light/install.py --check
python3 light/install.py --apply --dry-run
```

`--check` valida hashes e dependências para a sessão. Pode falhar fora de uma
sessão Plasma acessível por D-Bus. `--dry-run` mostra ações sem gravar arquivos.
O instalador de usuário deve rodar como usuário normal.

## Disponibilizar ambas as variantes

```bash
python3 light/install.py
python3 dark/install.py
```

Os temas aparecem em Configurações do Sistema → Cores e temas → Tema global.
Essa instalação copia assets e gera backups; não aplica configurações do usuário.
Cada pacote inclui os dois perfis do Konsole para permitir a sincronização.

## Aplicar uma variante

```bash
python3 light/install.py --apply
# Ou:
python3 dark/install.py --apply
```

Aplica paleta, decoração, fonte, cursor do mouse, estilo Plasma, integração GTK,
wallpaper, bloqueio, configuração de Konsole/Fish e ícone dos lançadores existentes.
Mantém a estrutura dos painéis, inclusive sua altura e aplicativos fixados atuais.
Reabra o Konsole após a primeira aplicação. Aplicativos já abertos podem precisar
ser reabertos ou de uma nova sessão gráfica para atualizar todos os componentes.

A seleção do tema global pela interface aplica os defaults e o layout nativo
quando solicitado. Para reproduzir também as configurações complementares de
GTK, Fish e Konsole, use o instalador com `--apply` pelo menos uma vez.

## Recriar painéis

```bash
python3 light/install.py --apply --layout
```

Esse comando remove os painéis atuais e cria um painel de 32 px por monitor
conectado, sem apps fixados. O layout contém lançador, paginador, tarefas por
ícones, separador, bandeja, relógio e mostrar desktop. Na interface do tema global,
a opção **Desktop and window layout** carrega o mesmo layout nativo.

O pacote configura os monitores presentes no momento da aplicação. Não instala
um serviço para criar painéis quando um novo monitor é conectado posteriormente.

## Login

O wallpaper do login tem configuração própria e não acompanha automaticamente
a troca de tema da sessão. Execute o instalador correspondente à imagem desejada:

```bash
python3 light/install-login.py --dry-run
sudo python3 light/install-login.py
# Para Moe Dark, use dark/install-login.py.
```

O script detecta o gerenciador pelo serviço habilitado. Para selecionar explicitamente:

```bash
python3 dark/install-login.py --manager plasma-login --dry-run
sudo python3 dark/install-login.py --manager plasma-login

python3 dark/install-login.py --manager sddm --dry-run
sudo python3 dark/install-login.py --manager sddm
```

No Plasma Login Manager, copia o wallpaper para a conta `plasmalogin` e altera
somente sua referência em `/etc/plasmalogin.conf`. No SDDM, cria uma cópia do
Breeze, configura a imagem/cursor e seleciona essa cópia em `/etc/sddm.conf.d/`.
Não troca o gerenciador habilitado nem reinicia serviços. Não distribui uma nova
interface de autenticação: ela segue o Breeze e o gerenciador instalados.

## Diretórios alternativos

São respeitados `XDG_DATA_HOME`, `XDG_CONFIG_HOME` e `XDG_STATE_HOME`.
Para instalar somente arquivos em uma área de teste:

```bash
python3 light/install.py --data-dir /tmp/papirus-share --config-dir /tmp/papirus-config --state-dir /tmp/papirus-state
```

Essas opções são recusadas com `--apply`, para evitar misturar um destino de teste
com a sessão atual. A instalação imprime o caminho do backup; conserve-o para
[restauração](RESTORE_AND_TROUBLESHOOTING.md).
