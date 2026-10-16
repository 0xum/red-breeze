# Personalização

Edite os arquivos no repositório e reinstale a variante desejada. As cópias em
`~/.local/share/` são os arquivos instalados; alterar apenas essas cópias não
atualiza o que será enviado ao GitHub ou distribuído para outro sistema.

Quando uma mudança deve valer para Light e Dark, faça-a nas duas variantes.
Os assets compartilhados são duplicados intencionalmente para manter pacotes independentes.

## Lançador em SVG

Arquivos:

- `light/assets/icons/PapirusBreezeLight/scalable/apps/papirus-breeze-launcher.svg`
- `dark/assets/icons/PapirusBreezeDark/scalable/apps/papirus-breeze-launcher.svg`

O SVG tem `viewBox="0 0 128 128"`. O `path` identificado como `hexagon` combina o
contorno externo com o recorte circular. O atributo `fill="#E93D58"` define a cor;
as curvas `Q` definem os cantos arredondados.

O segundo trecho do caminho é o círculo transparente, centrado em `(64,64)`:

```text
M 89 64 A 25 25 0 1 0 39 64 A 25 25 0 1 0 89 64 Z
```

Para raio 20, por exemplo, substitua esse trecho por:

```text
M 84 64 A 20 20 0 1 0 44 64 A 20 20 0 1 0 84 64 Z
```

Mantenha `fill-rule="evenodd"` para que o centro continue vazado. Um círculo com
`fill="none"` sobre um hexágono preenchido não recorta a forma abaixo. Um editor
vetorial pode editar o caminho composto diretamente. O desenho não contém imagem
rasterizada, filtro ou máscara dependente de suporte específico do renderizador.

## Paleta e ícones

As paletas ficam em `assets/color-schemes/PapirusBreezeLight.colors` e no equivalente
Dark. Cada tema global também inclui uma cópia em `contents/colors`; mantenha-a
idêntica à paleta da respectiva variante, como os testes exigem.

O destaque também está em `config/settings.json`. Os ícones do sistema e os sprites
do estilo Plasma têm vermelho fixo, portanto alterar somente `AccentColor` não os
recolore. Para mudar a identidade completa, revise também:

- `assets/icons/PapirusBreezeLight/` e `assets/icons/PapirusBreezeDark/`.
- `assets/plasma/desktoptheme/PapirusBreezeRed/`.
- SVG do lançador e perfis/paletas em `assets/konsole/`.

`scripts/red_icons.py` contém as transformações usadas nos SVGs de origem. Não é
executado pelo instalador: os SVGs finais já estão incluídos. Preserve autoria,
licenças, papéis de sucesso/aviso/erro e a herança do tema de ícones.

## Painéis

A lógica compartilhada de cada variante fica em `scripts/layout.js`. A cópia
nativa é `assets/plasma/look-and-feel/<ID>/contents/layouts/org.kde.plasma.desktop-layout.js`.

O script de instalação usa `__WALLPAPER_URI__`, substituído pelo destino real.
Na cópia nativa, use a expressão `"file://" + userDataPath("data") + "/wallpapers/Moe"`
(ou `MoeDark`), sem caminho pessoal absoluto. Os testes comparam essas duas formas.

A altura está em `panel.height = 32`; a lista vazia de tarefas em
`tasks.writeConfig("launchers", "")`. O ícone é configurado tanto nesse layout
quanto em `scripts/launcher.js`, que atualiza os painéis existentes sem recriá-los.

Alterar o script não muda painéis já existentes até aplicá-lo. Use `--layout`
quando realmente quiser recriar todos os painéis. Para trocar somente o ícone,
a aplicação normal `--apply` já atualiza os lançadores.

## Wallpaper e bloqueio

Os pacotes ficam em `light/assets/wallpapers/Moe/` e `dark/assets/wallpapers/MoeDark/`.
Mantenha as imagens claras em `contents/images/` e as escuras em
`contents/images_dark/`. Revise metadados, previews, licenças e o registro de
adaptação quando substituir imagens. Referencie a pasta do pacote para preservar
o comportamento adaptativo no desktop e bloqueio.

O instalador de login usa um arquivo específico e seu tamanho aparece em
`install-login.py`. Ao mudar o nome/tamanho do arquivo, atualize também essa referência.

## Konsole e Fish

Cada variante inclui os dois `.profile` e os dois `.colorscheme` em `assets/konsole/`.
Mantenha ambas as cópias sincronizadas ao personalizar o terminal.

Nos perfis, `[Appearance]` seleciona fonte e paleta; `[General]` define shell e
tamanho inicial. Em `[Cursor Options]`, `CustomCursorColor` é RGB e
`UseCustomCursorColor=true` habilita a cor. `[Terminal Features]` controla
`BlinkingCursorEnabled` e `AnimatingCursorEnabled`.

Os nomes de exibição dos perfis são usados por `LightThemeProfile` e
`DarkThemeProfile` em `config/settings.json`. `DefaultProfile` usa o nome do arquivo.
Ao renomear um perfil, ajuste essas referências também.

A saudação, cores ANSI e ajustes do Pure ficam em `assets/fish/papirus-breeze.fish`.
Não substitua o arquivo completo de configuração pessoal ou a configuração da
distribuição para mudar apenas a apresentação.

## Validar e reinstalar

Depois de revisar as alterações intencionais:

```bash
python3 tools/project.py manifest
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
python3 light/install.py --apply
```

A atualização de manifesto aceita o conteúdo local como a nova referência de
integridade; não corrige um download corrompido. Para alterar só uma variante,
use `--variant light` ou `--variant dark` nas ações de manutenção.

Ícones já carregados podem exigir nova sessão gráfica para atualizar o cache.
Reabra o Konsole para carregar perfis modificados. Veja os procedimentos de
[restauração](RESTORE_AND_TROUBLESHOOTING.md) antes de reverter snapshots completos.
