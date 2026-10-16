# Aparência e comportamento

## Identidade visual

O destaque é **vermelho `#E93D58`**, RGB `233,61,88`. Textos comuns mantêm suas cores
claras/escuras para leitura. A fonte geral é Noto Sans 10 pt; animações KDE usam
fator `0.25`; o alternador de janelas e o splash são Breeze.

| Componente | Light | Dark |
| --- | --- | --- |
| Cores | `PapirusBreezeLight`, base Breeze Light | `PapirusBreezeDark`, base Breeze Dark |
| Tema de ícones | `PapirusBreezeLight`, herda Papirus | `PapirusBreezeDark`, herda Papirus-Dark |
| Estilo Plasma | `PapirusBreezeRed` | `PapirusBreezeRed` |
| Estilo Qt | Breeze | Breeze |
| GTK | Breeze, preferência clara | Breeze-Dark, preferência escura |
| Aurorae | `Amy-Light-Aurorae-6` | `Amy-Papirus-Dark` |
| Mouse | `Breeze_Light`, 18 px | `breeze_cursors`, 18 px |
| Wallpaper registrado | `Moe` | `MoeDark` |

A decoração tem botões pequenos; menu à esquerda e minimizar, maximizar e fechar
à direita. A adaptação Dark preserva as proporções da Amy Light.

## Painéis

O layout nativo e o script de instalação criam um painel inferior por monitor,
altura de **32 px**, flutuante, com largura total, alinhamento central e opacidade
adaptativa. A sequência de widgets é lançador, paginador, tarefas por ícones,
separador, bandeja, relógio e mostrar desktop.

A lista de lançadores fixados das tarefas começa vazia. O primeiro lançador tem
atalho `Alt+F1`. A aplicação sem `--layout` atualiza o ícone dos lançadores existentes
sem recriar painéis ou apagar favoritos da taskbar. Layouts são aplicados aos
monitores conectados naquele momento; os IDs são resolvidos no destino.

## Ícones vermelhos

O complemento inclui **835 aliases de pastas**: 539 Papirus Red, 7 derivados
Copy Cloud recoloridos e 289 aliases adicionais. As referências genéricas
`inode-directory`, `gtk-directory` e `stock_folder` também apontam para pastas
vermelhas, cobrindo subpastas e atalhos entre categorias.

Ações, menus, categorias, dispositivos e bandeja têm variantes vermelhas. Nos
SVGs adaptados, glifos neutros usam vermelho fixo para evitar a recoloração
automática do KDE como texto. Indicadores semânticos de erro, aviso e sucesso
preservam seus papéis quando presentes. Outros aplicativos e marcas mantêm os
ícones herdados dos temas base.

A bandeja do Plasma também usa sprites próprios em `PapirusBreezeRed`, pois esses
ícones podem vir do estilo Plasma em vez do tema de ícones. As superfícies são
herdadas do Breeze e acompanham a paleta Light/Dark.

Dolphin usa vermelho `#E93D58` e sombra `#a62a3e`, preservando a forma Papirus.
Os aliases `org.kde.dolphin`, `dolphin` e `system-file-manager` estão incluídos.

## Lançador SVG

`papirus-breeze-launcher.svg` contém um hexágono vermelho arredondado com recorte
circular **transparente**, não branco. O centro deixa aparecer o fundo real do
painel. O arquivo é vetorial, sem bitmap incorporado, e usa `fill-rule="evenodd"`.
Está registrado no diretório `scalable/apps` dos dois temas de ícones.

O layout novo e a atualização de painéis existentes usam o nome lógico
`papirus-breeze-launcher`, sem caminho pessoal absoluto.

## Wallpaper, bloqueio e login

Cada pacote de wallpaper contém a imagem clara original em `contents/images/`
(3073 × 1420) e a escura em `contents/images_dark/` (1844 × 853). Desktop e bloqueio
referenciam a pasta do pacote, permitindo a seleção clara/escura pelo Plasma.
Selecionar uma imagem avulsa manualmente fixa essa imagem.

O login é independente: seu instalador usa um arquivo da variante escolhida.
A tela de autenticação não troca de wallpaper quando o usuário muda o tema da sessão.

## Konsole

Ambos os pacotes incluem os perfis `Papirus Breeze Light` e `Papirus Breeze Dark`.
A configuração `LightDarkTheme` do `konsolerc` ativa a sincronização nativa com a
paleta do sistema. Ela foi validada inclusive em uma sessão já aberta.

- Fundo branco no Light e carvão no Dark; opacidade 1, sem blur.
- JetBrainsMono Nerd Font, 11 pt; janela inicial de 96 colunas × 24 linhas.
- Paletas ANSI adaptadas para legibilidade e destaque vermelho.
- Cursor em bloco vermelho `#E93D58`, com piscar e animação habilitados.
- Texto sob o cursor em `20,22,24`; histórico de 10.000 linhas.
- Comando inicial `fish`; outros perfis existentes são preservados.

O cursor do terminal é independente do tema de cursor do mouse.

## Fish

A saudação tem três linhas: distribuição/arquitetura, kernel e desktop/versão do
Fish. Não usa logo ASCII ou Fastfetch. Um bloco gerenciado no fim de
`fish/config.fish` carrega `fish/papirus-breeze.fish` somente em sessões interativas,
depois da configuração da distribuição.

O prompt Pure existente, quando disponível, passa a uma linha com destaque
vermelho. Os ajustes usam variáveis globais da sessão, sem substituir
`fish_variables` ou alterar o shell de login do usuário. A configuração da
distribuição e seus aliases continuam sendo carregados.
