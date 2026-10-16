# Papirus Breeze Light

Este pacote faz parte do repositório unificado **Papirus Breeze**, na pasta
`light/`. Os exemplos abaixo partem desta pasta; da raiz do repositório,
prefixe os caminhos dos scripts com `light/`. A documentação compartilhada
fica em `docs/` na raiz. O arquivo de distribuição continua instalável sozinho.

Pacote portátil do desktop pessoal Papirus Breeze Light, exportado de um Plasma 6
em 16 de outubro de 2026. Inclui o visual atual, o wallpaper e a configuração de
bloqueio e de login.

![Wallpaper Moe](assets/wallpapers/Moe/contents/images/3073x1420.png)

## Aparência incluída

| Item | Configuração |
| --- | --- |
| Tema global | Papirus Breeze Light, ID `com.delta.papirus-breeze-light` |
| Estilo dos aplicativos / Plasma | Breeze / `PapirusBreezeRed` |
| Cores | Breeze Light com destaque vermelho `#E93D58`, paleta exportada |
| Ícones | Papirus, com as pastas Papirus Red presentes no desktop original |
| Decoração das janelas | Amy-Light-Aurorae-6, botões pequenos; menu à esquerda, minimizar/maximizar/fechar à direita |
| Cursor | Breeze Light, 18 px |
| Fonte geral / GTK | Noto Sans, 10 pt |
| Animações KDE | Fator `0.25` |
| Alternador de janelas | Breeze |
| Wallpaper | Moe, 3073 × 1420, aplicado a todos os desktops existentes |
| Bloqueio | Mesmo wallpaper Moe |
| Painéis opcionais | Um por monitor conectado, inferiores, flutuantes, 32 px, largura total, opacidade adaptativa |
| Login original | Plasma Login Manager com wallpaper Moe |

O tema de ícones complementar `PapirusBreezeLight` inclui os 835 aliases de pastas
e as variantes vermelhas dos ícones do sistema; herda os demais ícones de `Papirus`. Isso mantém
a variante vermelha sem embutir a biblioteca completa de ícones.

## Dependências

- Linux com KDE Plasma 6 e Python 3.9 ou superior.
- Breeze, Breeze Light (cursor), suporte Aurorae e tema GTK Breeze.
- [Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), Noto Sans
  e tema de sons Ocean instalados pelo gerenciador de pacotes da distribuição.
- Para aplicar na sessão atual: `kwriteconfig6`, `qdbus6`,
  `plasma-apply-lookandfeel`, `plasma-apply-colorscheme`,
  `plasma-apply-desktoptheme` e `plasma-apply-cursortheme`.
- Para login: Plasma Login Manager; há uma alternativa para SDDM com Breeze.

Os nomes dos pacotes variam por distribuição. Os scripts não instalam programas
nem baixam arquivos. Todos os assets próprios do pacote já estão nesta pasta.

## Instalar e aplicar

Execute como usuário normal, em um terminal da sessão Plasma de destino:

```bash
python3 install.py --check
python3 install.py --apply --dry-run
python3 install.py --apply
```

O comando com `--apply` instala os arquivos, aplica o tema, ajusta a paleta, GTK,
fonte, cursor, decoração, wallpaper, bloqueio, Konsole e Fish. Mantém os painéis existentes.
Encerre e inicie a sessão depois para que todos os aplicativos atualizem o visual.

Para reproduzir também os painéis originais:

```bash
python3 install.py --apply --layout
```

**`--layout` remove os painéis atuais e cria um painel por monitor conectado.**
Reproduz lançador, paginador, tarefas por ícones, separador, bandeja, relógio e
mostrar desktop. O primeiro painel e os demais começam sem aplicativos fixados. O ícone do lançador usa o SVG próprio `papirus-breeze-launcher`, incluído no pacote. Atividades, IDs de monitores e resoluções são definidos no destino.

Para apenas disponibilizar os arquivos, sem aplicar configurações:

```bash
python3 install.py
```

O tema aparecerá em Configurações do Sistema → Cores e temas → Tema global.
Selecioná-lo pela interface aplica seus defaults. Use o instalador com `--apply`
para incluir wallpaper, bloqueio e integração GTK de forma completa. Na interface, marque **Desktop and window layout** para aplicar os painéis de 32 px, um por monitor e sem aplicativos fixados. Deixe essa opção desmarcada para preservar os painéis existentes. A instalação respeita `XDG_DATA_HOME`, `XDG_CONFIG_HOME` e
`XDG_STATE_HOME`.

## Tela de login

O instalador configura aparência completa para Plasma Login Manager ou SDDM:
paleta, destaque vermelho, ícones, cursor e wallpaper. Os recursos necessários
ficam acessíveis à conta do greeter, mesmo com a pasta pessoal do usuário privada.
A interface de autenticação continua sendo a nativa Breeze.

```bash
python3 install-login.py --dry-run
sudo python3 install-login.py
```

Para acompanhar as trocas entre Light/Dark de um usuário:

```bash
sudo python3 install-login.py --follow-user nome-do-usuario
```

Instale as duas variantes com essa opção. No repositório unificado, o comando
`sudo python3 tools/install-login.py --follow-user "$USER"` executado da raiz
instala ambas e o observador systemd. Uma instalação estática mantém a aparência
escolhida até a próxima aplicação; o observador seleciona a variante conforme
a paleta do usuário. Temas fora de Papirus Breeze são ignorados.

`--manager plasma-login` ou `--manager sddm` permite explicitar o backend.
A instalação não reinicia o display manager nem altera autenticação/autologin.
O resultado é usado na próxima tela de login. Para desabilitar acompanhamento,
execute `sudo systemctl disable --now papirus-breeze-login.path papirus-breeze-login.service`.
Faça isso também antes de restaurar snapshots; após restaurar unidades, execute
`sudo systemctl daemon-reload`.

## Backup e restauração

Cada instalação grava o estado anterior dos destinos e imprime o caminho do
backup. No perfil de usuário, os backups ficam em
`~/.local/state/papirus-breeze-light/backups/` ou no `XDG_STATE_HOME` correspondente.
Para login, ficam em `/var/lib/papirus-breeze-light/backups/`.

```bash
python3 restore.py /caminho/do/backup --dry-run
python3 restore.py /caminho/do/backup
```

Para backups do login, execute o segundo comando com `sudo`. Para restaurar
arquivos do Plasma, encerre a sessão gráfica e use um TTY: o Plasma em execução
pode sobrescrever esses arquivos. A restauração recupera os arquivos inteiros do
snapshot, incluindo configurações que tenham mudado depois da instalação.
Restaure backups de várias instalações na ordem inversa, começando pelo mais recente.

## Conteúdo e limites da exportação

- `assets/`: tema global, paleta, decoração, wallpaper e complemento de ícones.
- `config/settings.json`: somente as chaves de aparência portáveis.
- `install.py`: instalação de usuário, aplicação e backups.
- `install-login.py`: configuração do wallpaper do gerenciador de login.
- `restore.py`: restauração dos snapshots.
- `manifest.json`: versão e hashes SHA-256 dos arquivos distribuídos.
- `LICENSES/` e `THIRD_PARTY.md`: licenças e créditos dos componentes.

O wallpaper North do layout antigo foi substituído pelo Moe. O nome do usuário,
caminhos `/home/...`, atividades, IDs de monitores, favoritos pessoais, contas,
atalhos gerais, programas padrão e configurações de autenticação não fazem parte
do perfil. Recursos independentes do tema, como Night Color, escalas de monitores
e tiling, continuam sob controle do sistema de destino.

O pacote original selecionava a si próprio como splash, mas não continha uma
animação de splash. Este pacote usa explicitamente o splash padrão Breeze.

## Verificar e gerar arquivo para transferência

```bash
python3 -m unittest discover -s tests -v
python3 build.py
```

O segundo comando gera `dist/papirus-breeze-light-1.0.13.tar.gz`, com a mesma pasta
pronta para copiar, extrair e instalar. `dist/`, caches e backups não entram no Git.
Os testes usam diretórios temporários e não aplicam o tema à sessão atual.

## GitHub e licenças

No conjunto unificado, o repositório Git fica na pasta pai; esta pasta contém
somente o pacote Light. Nenhum remoto ou publicação é criado pelo instalador. Os componentes mantêm suas licenças: confira
[THIRD_PARTY.md](THIRD_PARTY.md) antes de redistribuir.

## Troca entre Light e Dark

O pacote de wallpaper contém `contents/images/` (Moe Light) e `contents/images_dark/` (Moe Dark). O instalador seleciona a pasta do wallpaper, permitindo que o Plasma acompanhe o esquema claro/escuro automaticamente. Uma imagem avulsa selecionada manualmente continua fixa. O tema global declara o wallpaper Moe e inclui o layout nativo. Marcar **Desktop and window layout** recria um painel de 32 px por monitor, sem aplicativos fixados; sem essa opção, os painéis são preservados. O instalador também oferece `python3 install.py --apply --layout`.

## Ícones vermelhos do sistema

Além das pastas, o tema inclui variantes vermelhas para ações, menus, categorias, dispositivos e bandeja. Os símbolos usam vermelho fixo sem alterar a paleta dos textos. O estilo Plasma `PapirusBreezeRed` contém os sprites vermelhos e herda as superfícies do Breeze, acompanhando Light/Dark. Indicadores de erro, aviso e sucesso preservam os papéis semânticos quando presentes; aplicativos e marcas fora das preferências do sistema mantêm seus ícones originais.

O ícone do Dolphin também usa a variante vermelha (#E93D58), preservando a forma Papirus, em todos os tamanhos e nos aliases org.kde.dolphin, dolphin e system-file-manager.

## Konsole e Fish

Os dois perfis `Papirus Breeze Light` e `Papirus Breeze Dark` acompanham cada
pacote. Usam JetBrainsMono Nerd Font 11 pt, janela inicial de 96 × 24 caracteres,
fundo branco ou escuro opaco e paletas ANSI com destaque vermelho.
O cursor de texto usa um bloco vermelho `#E93D58`, com piscar e animação habilitados.
`--apply` habilita a sincronização nativa do Konsole com o tema do sistema:
a troca entre Light/Dark atualiza o perfil automaticamente, inclusive nas sessões
abertas após essa configuração. O recurso foi validado no Konsole 26.08.2 instalado na origem, com a
sincronização configurada no grupo LightDarkTheme do konsolerc. Em versões sem esse recurso, selecione
um dos perfis manualmente. Instale Fish e JetBrainsMono Nerd Font no destino;
os perfis iniciam o Fish sem trocar o shell de login do usuário.

O Fish mostra somente três linhas: distribuição/arquitetura, kernel e
Plasma/versão do Fish. O prompt Pure, quando disponível, passa a uma linha com
vermelho. O instalador preserva a configuração da distribuição e acrescenta um
bloco identificado no final de `fish/config.fish`, que carrega
`fish/papirus-breeze.fish` somente em sessões interativas. Isso substitui a
saudação extensa do Fastfetch. Outros perfis do Konsole permanecem disponíveis.
Reabra o Konsole após a primeira aplicação para carregar os novos perfis.

## Ícone do lançador

![Ícone do lançador](assets/icons/PapirusBreezeLight/scalable/apps/papirus-breeze-launcher.svg)

O arquivo editável fica em `assets/icons/PapirusBreezeLight/scalable/apps/papirus-breeze-launcher.svg`.
O elemento `hexagon` define a forma vermelha e o recorte circular transparente.
Edite `fill` para mudar a cor. O segundo trecho de `d` recorta o círculo de raio 25,
centrado em 64,64; ajuste seus arcos e extremos para redimensioná-lo.
O atributo `fill-rule="evenodd"` mantém o centro vazado, mostrando o fundo real do painel.
A imagem usa fundo transparente e escala de 16 a 512 px. É uma recriação vetorial
própria do desenho, sob GPL-3.0-only.

`--apply` atualiza o ícone dos lançadores existentes. O layout nativo e `--layout`
também usam esse ícone nos painéis novos. Para atualizar o desenho após editá-lo,
reinstale os arquivos e recarregue o cache de ícones; a geração e verificação do
pacote exigem atualizar os hashes em `manifest.json`.
