# Créditos e licenças

Este pacote reúne configurações pessoais e componentes independentes. Cada
componente mantém a licença indicada abaixo.

| Componente | Origem / autor | Licença | Alterações nesta exportação |
| --- | --- | --- | --- |
| Wallpaper Moe | jomada, versão 1.1, conforme os metadados originais incluídos | CC-BY-SA-4.0 | Imagem e metadados sem alteração; também usada como preview |
| Amy-Light-Aurorae-6 | l4k1, versão 1.2, conforme os metadados originais incluídos | GPL-3.0 (metadados: `GPLv3`) | Arquivos originais sem alteração |
| Esquema Breeze Light | KDE, autores preservados no cabeçalho do `.colors` | LGPL-2.0-or-later | Exportada a paleta atual com destaque `#E93D58`; novo nome PapirusBreezeLight |
| Ícones de pastas Papirus / Catppuccin | [Papirus Development Team](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), [Catppuccin papirus-folders](https://github.com/catppuccin/papirus-folders) | GPL-3.0 e aviso MIT do Catppuccin | 835 aliases vermelhos exportados como SVGs (539 Papirus Red nativos e 7 derivados Copy Cloud recoloridos); tema novo herda o Papirus instalado |
| Instaladores, scripts e composição do tema | Delta, 2026 | GPL-3.0-only | Arquivos novos desta exportação |

Os textos das licenças e a lista de autores do Papirus estão em `LICENSES/`.
Os créditos originais da decoração e do wallpaper estão nos próprios metadados.
O pacote não inclui a biblioteca completa de ícones Papirus, o Breeze, as fontes
Noto ou o tema de sons Ocean; esses componentes vêm do sistema de destino.

O wallpaper adaptativo inclui o Moe Light original de jomada e o Moe Dark adaptado por Delta com ImageGen. Ambas as variantes são distribuídas sob CC-BY-SA-4.0; o modo escuro está em `contents/images_dark/`.

Pastas vermelhas: 539 aliases usam os SVGs Papirus Red sem alteração. Os 7 ícones Copy Cloud preservam a geometria Catppuccin/Papirus e foram recoloridos para a paleta Papirus Red (#e25252, #bf4b4b).

Incluídos 289 aliases adicionais resolvidos para os SVGs vermelhos, entre eles inode-directory, gtk-directory, stock_folder e atalhos entre categorias.

Ícones do sistema: variantes dos SVGs Papirus (GPL-3.0), com glifos neutros convertidos para #E93D58. O estilo Plasma PapirusBreezeRed contém adaptações dos sprites Breeze do KDE Visual Design Group, cuja identificação original de licença é LGPL. Os metadados originais foram preservados em LICENSES/Breeze-original-metadata.json. As superfícies e os demais recursos do estilo são herdados do Breeze instalado.

Dolphin: SVGs Papirus originais recoloridos de azul para vermelho (#E93D58 e sombra #a62a3e), com forma e recortes preservados. Licença GPL-3.0.

Os perfis e paletas do Konsole e a configuração compacta do Fish em `assets/konsole/` e `assets/fish/` são adaptações próprias deste pacote sob GPL-3.0-only. O prompt Pure e os programas Fish/Konsole são dependências externas e não são redistribuídos.
