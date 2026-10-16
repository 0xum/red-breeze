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

## Login: acompanhar o tema global

O sistema de origem usa **Plasma Login Manager 6.8.0**. O instalador detecta o
serviço ativo e também suporta SDDM/Breeze em outros sistemas. A instalação de
usuário não pode gravar a aparência de outra conta; execute uma instalação
administrativa inicial para disponibilizar os assets e perfis no login.

A partir da raiz, simule e depois instale ambas as variantes com acompanhamento:

```bash
python3 tools/install-login.py --follow-user "$USER" --dry-run
sudo python3 tools/install-login.py --follow-user "$USER"
```

O nome deve ser o usuário normal da sessão, não `root`. O Polkit também pode
executar o mesmo comando quando a aplicação chama o instalador via `pkexec`.

O acompanhamento observa `~/.config/kdeglobals` do usuário indicado. Quando sua
paleta é `PapirusBreezeLight` ou `PapirusBreezeDark`, seleciona o perfil instalado
correspondente para a próxima tela de login. Outros temas são ignorados. Não há
consulta periódica nem execução de scripts dentro da pasta pessoal pelo serviço.

São instalados:

- Recursos de ícones e estilo na área de dados da conta `plasmalogin` ou `sddm`.
- Wallpapers e perfis fixos em `/usr/local/share/papirus-breeze-login/`.
- Paletas próprias `PapirusBreezeLoginLight/Dark` na conta do greeter, com cores
  complementares ajustadas para que o login claro seja realmente claro.
- `/usr/local/libexec/papirus-breeze-login.py`, cópia administrativa do sincronizador.
- `/etc/papirus-breeze-login.json`, indicando apenas o usuário, a origem e o gerenciador.
- `papirus-breeze-login.path` e `papirus-breeze-login.service`, habilitados no systemd.

O sincronizador usa apenas o nome da paleta para escolher os perfis fixos instalados
por root. Não copia todo o `kdeglobals` pessoal, não muda autenticação/autologin e
não reinicia o gerenciador de login. O estado aplicado fica em
`/var/lib/papirus-breeze-login/current.json`; a mesma paleta não é reaplicada a cada
escrita sem relação com o tema. A tela usa a identidade Breeze nativa, com recursos
Papirus vermelhos e o wallpaper da variante. Dependências de ícones não incluídas
no complemento continuam usando os fallbacks Breeze/hicolor do sistema.

### Aplicação estática de uma variante

Para aplicar uma aparência uma vez, sem instalar acompanhamento automático:

```bash
python3 light/install-login.py --dry-run
sudo python3 light/install-login.py
# Ou dark/install-login.py.
```

Para explicitar o gerenciador:

```bash
sudo python3 dark/install-login.py --manager plasma-login
sudo python3 dark/install-login.py --manager sddm
```

Um pacote independente pode usar `--follow-user nome`; instale ambos os pacotes
com essa opção para que as duas variantes estejam disponíveis ao observador.
No SDDM, o instalador cria temas Breeze dedicados e define sua seleção em
`/etc/sddm.conf`, que tem prioridade sobre arquivos antigos de `conf.d`.
No Plasma Login Manager, altera os campos de aparência em `/etc/plasmalogin.conf`.

Se já habilitou o acompanhamento, ele continua seguindo a paleta observada. Para
voltar à configuração estática, desabilite as unidades antes de aplicar uma variante:

```bash
sudo systemctl disable --now papirus-breeze-login.path papirus-breeze-login.service
```

O resultado será usado na próxima tela de login. Não saia da sessão apenas para
executar o instalador; ele não encerra a sessão atual.

## Diretórios alternativos

São respeitados `XDG_DATA_HOME`, `XDG_CONFIG_HOME` e `XDG_STATE_HOME`.
Para instalar somente arquivos em uma área de teste:

```bash
python3 light/install.py --data-dir /tmp/papirus-share --config-dir /tmp/papirus-config --state-dir /tmp/papirus-state
```

Essas opções são recusadas com `--apply`, para evitar misturar um destino de teste
com a sessão atual. A instalação imprime o caminho do backup; conserve-o para
[restauração](RESTORE_AND_TROUBLESHOOTING.md).
