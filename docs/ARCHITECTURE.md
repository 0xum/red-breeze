# Arquitetura e configurações

## Um Git, dois pacotes

A raiz contém documentação, licença e ferramenta de manutenção. `light/` e `dark/`
são pacotes autossuficientes com seus próprios assets, testes, instaladores,
manifestos e `build.py`. Não há repositórios Git aninhados.

Os IDs das variantes diferem para que elas coexistam. O estilo Plasma
`PapirusBreezeRed`, o ícone lógico do lançador e os nomes dos perfis Konsole são
compartilhados. Por isso, cada pacote inclui cópias desses recursos; mantenha-as
sincronizadas quando alterar comportamento comum.

## Conteúdo de uma variante

| Caminho | Responsabilidade |
| --- | --- |
| `assets/plasma/look-and-feel/<ID>/` | Metadados, defaults, cores, preview e layout nativo |
| `assets/plasma/desktoptheme/PapirusBreezeRed/` | Sprites vermelhos; herança das superfícies Breeze |
| `assets/icons/PapirusBreezeLight/` ou `PapirusBreezeDark/` | Pastas, sistema, Dolphin, lançador e herança Papirus |
| `assets/color-schemes/` | Paleta Light ou Dark |
| `assets/aurorae/themes/` | Decoração Amy da variante |
| `assets/wallpapers/` | Pacote adaptativo com imagens, metadados e procedência |
| `assets/konsole/` | Ambos os perfis e paletas do terminal |
| `assets/fish/` | Saudação e cores compactas |
| `config/settings.json` | Chaves de aparência portáveis aplicadas com KConfig |
| `scripts/layout.js` | Reconstrução dos painéis por monitor |
| `scripts/launcher.js` | Atualização de ícones nos lançadores existentes |
| `scripts/wallpaper.js` | Aplicação do wallpaper aos desktops existentes |
| `scripts/red_icons.py` | Transformações dos SVGs de origem |
| `install.py` | Instalação de usuário, aplicação e backups |
| `install-login.py`, `scripts/login.py` | Aparência completa de Plasma Login Manager ou SDDM e sincronização opcional |
| `restore.py` | Restauração de snapshots de arquivos completos |
| `manifest.json` | Metadados da versão e hashes SHA-256 distribuídos |
| `build.py` | Arquivo independente `.tar.gz` |
| `tests/` | Integridade, portabilidade, layout, instalação e terminal |
| `LICENSES/`, `THIRD_PARTY.md` | Textos de licença e autoria |

## O que é alterado com `--apply`

| Configuração | Chaves ou efeito |
| --- | --- |
| `kdeglobals` | Paleta, destaque, ícones, fonte, Breeze, tema global, animações e contraste |
| `kwinrc` | Decoração Aurorae, botões e alternador Breeze |
| `plasmarc` | Estilo `PapirusBreezeRed` |
| `kcminputrc` | Tema e tamanho do cursor do mouse |
| `auroraerc` | Tamanho dos botões da decoração |
| `ksplashrc` | Splash Breeze |
| `kscreenlockerrc` | URI do pacote de wallpaper de bloqueio, calculada no destino |
| `konsolerc` | Perfis claro/escuro, sincronização e perfil padrão |
| `gtk-3.0/settings.ini`, `gtk-4.0/settings.ini` | Preferência clara/escura, tema, ícones, fonte, cursor e integração |
| `fish/config.fish` | Bloco gerenciado ao final, preservando configuração anterior |
| `fish/papirus-breeze.fish` | Helper instalado com saudação e ajustes de prompt |
| Estado do Plasma Shell | Wallpaper dos desktops e ícones dos lançadores; painéis somente com `--layout` |

As ferramentas KDE também podem sincronizar arquivos auxiliares de GTK; o
instalador salva snapshots adicionais antes de aplicar. Os perfis Konsole são
copiados individualmente para preservar perfis de terceiros na mesma pasta.

Os defaults do tema global não executam o helper Fish ou toda a integração extra
do instalador. Por isso o guia diferencia selecionar um tema na interface de
aplicar o pacote completo com `--apply`.

## Instalação e integridade

O instalador verifica os hashes antes de copiar. Os destinos são derivados de XDG,
e não do caminho pessoal usado na criação do tema. O manifesto de uma variante
cobre somente sua própria pasta, incluindo seus documentos e scripts; não cobre
a documentação e ferramenta da raiz. Git registra o conjunto completo.

`build.py` exclui `.git`, `dist`, `__pycache__` e `.pyc`. O arquivo resultante contém
uma pasta de versão que funciona sem a outra variante ou as ferramentas da raiz.
Os testes de cada variante executam em processos separados, evitando colisões
entre módulos de mesmo nome, como `install` e `restore`.

## Limites da exportação

O pacote não reproduz contas, autenticação, atividades, IDs de monitores,
resoluções, favoritos pessoais, atalhos gerais ou programas padrão. Night Color,
escalas e tiling continuam sob controle do sistema. A instalação não muda o shell
de login nem instala dependências. Configurar o login aplica sua aparência e, com acompanhamento, habilita as
unidades próprias de sincronização. Não altera autenticação ou o display manager habilitado.

A configuração legível de login do sistema original foi exportada. Ajustes que
existissem somente no diretório privado do greeter original não foram lidos.
O splash salvo originalmente não tinha animação própria; o conjunto usa Breeze.

## Integração administrativa do login

`tools/install-login.py` instala os dois perfis por processos separados. O helper
`scripts/login.py` é idêntico nas variantes e pode ser distribuído com cada pacote.
Sua cópia instalada em `/usr/local/libexec/` executa `--sync` sem importar código
do repositório pessoal. O observador systemd acorda o serviço quando o arquivo
de paleta indicado muda; a unidade também aplica o último perfil no boot antes
do display manager. O próprio display manager nunca é reiniciado pelo instalador.

O serviço aceita somente dois valores conhecidos de paleta, verifica a origem
como arquivo regular do usuário indicado e escolhe payloads administrativos fixos.
Escritas de configuração são atômicas; alvos simbólicos são recusados. Os arquivos
de greeter preservam chaves externas à aparência, e `/etc/plasmalogin.conf` ou
`/etc/sddm.conf` mantêm os grupos de autenticação e sessão. O cache do greeter é
limpo ao aplicar uma paleta nova, seguindo a necessidade documentada pelo helper
nativo do KDE. Nenhum cache do usuário da sessão é removido.

Os recursos são copiados para fora da pasta pessoal privada do usuário. A conta
do login recebe somente o complemento de ícones fornecido aqui e usa o Breeze
instalado como fallback; a biblioteca Papirus completa não é duplicada.

A integração foi conferida com o código KDE da versão 6.8.0:
[sincronizador nativo](https://github.com/KDE/plasma-login-manager/blob/v6.8.0/src/frontend/kcm/auth/plasmaloginauthhelper.cpp)
e [greeter e grupo Complementary](https://github.com/KDE/plasma-login-manager/blob/v6.8.0/src/frontend/greeter/qml/Main.qml).
