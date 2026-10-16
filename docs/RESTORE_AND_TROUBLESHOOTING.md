# Backups, restauração e solução de problemas

## Onde ficam os backups

Cada instalação imprime o caminho do snapshot. Por padrão:

| Operação | Local |
| --- | --- |
| Usuário Light | `~/.local/state/papirus-breeze-light/backups/<data-hora>/` |
| Usuário Dark | `~/.local/state/papirus-breeze-dark/backups/<data-hora>/` |
| Login Light | `/var/lib/papirus-breeze-light/backups/<data-hora>/` |
| Login Dark | `/var/lib/papirus-breeze-dark/backups/<data-hora>/` |

O estado de usuário respeita `XDG_STATE_HOME`. `restore.json` lista os destinos,
se existiam e onde estão suas cópias. Recursos inexistentes antes da instalação
são removidos durante a restauração. Diretórios de assets do pacote são copiados
como unidades; não misture arquivos pessoais nesses diretórios dedicados.

## Restaurar

Para restaurar configurações do Plasma, encerre a sessão gráfica e execute em
um TTY, pois a sessão em execução pode gravar novamente seus arquivos:

```bash
python3 light/restore.py /caminho/do/backup --dry-run
python3 light/restore.py /caminho/do/backup
```

Para snapshots do login, execute a restauração com `sudo`. Ambos os restauradores
leem o mesmo formato de backup. A restauração recupera **arquivos inteiros**,
inclusive alterações pessoais feitas depois do snapshot. Se houve várias
instalações, restaure em ordem inversa, começando pela mais recente.

Para simplesmente escolher a outra aparência, prefira seu instalador com
`--apply`. Isso não é uma restauração do estado anterior. O wallpaper do login
continua separado e requer o instalador de login correspondente.

## O painel voltou ao padrão

Confirme que instalou esta versão do pacote e selecionou o tema pelo ID próprio,
`com.delta.papirus-breeze-light` ou `com.delta.papirus-breeze-dark`. O layout nativo
fica em `contents/layouts/org.kde.plasma.desktop-layout.js` e acompanha o pacote.
Na seleção do tema, **Desktop and window layout** recria os painéis. Pelo terminal,
use `--apply --layout`. Isso remove os painéis atuais.

Sem essa opção, a altura e os favoritos atuais são preservados. Um monitor ligado
após a aplicação não recebe painel automaticamente por um serviço deste pacote.

## Pastas ou ícones ainda aparecem roxos/azuis

Confira o tema de ícones ativo e a presença de Papirus/Papirus-Dark. O complemento
inclui aliases genéricos para subpastas e as variantes do Dolphin. Ícones antigos
podem estar no cache de aplicativos já abertos; reabra-os ou inicie nova sessão.

Ícones simbólicos da bandeja podem vir do estilo Plasma. Confira também
`PapirusBreezeRed`, além do tema de ícones. Aplicativos externos ao conjunto
continuam herdando seus ícones originais.

## A lixeira aparece como um usuário

Isso foi corrigido na versão 1.0.12. Sem os aliases explícitos `user-trash` e
`user-trash-full`, o KDE podia reduzir o nome para `user` e escolher o avatar do
complemento antes de consultar a lixeira do tema herdado. Os pacotes agora incluem
os dois estados e os aliases simbólicos em todos os tamanhos. Reinstale a variante
e atualize o cache da sessão ou reabra o aplicativo. O bookmark de lixeira deve
continuar usando `user-trash`; não é necessário alterar seus lugares pessoais.

## O centro do lançador parece branco ou preto

O SVG usa um recorte transparente real. O centro mostra o fundo sob ele; portanto
pode parecer branco, escuro ou translúcido conforme o painel e wallpaper. Não é
uma cor de preenchimento. Se aparece um desenho antigo, reinstale o SVG e atualize
a sessão para descartar cache. Mantenha `fill-rule="evenodd"` ao personalizar.

## Konsole não acompanha Light/Dark

Instale ambos os perfis, aplique o pacote com `--apply` e reabra o Konsole após a
primeira configuração. Confirme a sincronização em `konsolerc`, grupo
`LightDarkTheme`, e os nomes dos perfis. Versões sem suporte nativo podem usar
seleção manual. A versão validada na origem foi 26.08.2.

Cursor de texto vermelho é uma opção de cada `.profile`; não muda o cursor do
mouse. Fish e fonte precisam estar instalados para reproduzir todo o terminal.

## Fish continua mostrando Fastfetch

O bloco Papirus Breeze precisa estar ao final de `fish/config.fish`, depois de
carregar a configuração da distribuição. Ele carrega o helper apenas em sessões
interativas. Abra uma nova sessão Fish. Outra redefinição posterior de
`fish_greeting` pode substituir a saudação compacta.

## Wallpaper não troca ou o login usa outra imagem

Desktop e bloqueio devem referenciar a pasta do pacote adaptativo. Uma imagem
avulsa selecionada manualmente fica fixa. O login usa um arquivo próprio da
variante escolhida e não acompanha a paleta da sessão; execute seu instalador separado.

## Hash divergente ou dependência ausente

Se editou o código intencionalmente, siga a atualização dos manifestos em
[Personalização](CUSTOMIZATION.md). Se não editou, recupere a cópia correta pelo Git
ou pelo arquivo de distribuição. Os instaladores não baixam arquivos nem instalam
dependências automaticamente; use o gerenciador de pacotes da distribuição.
