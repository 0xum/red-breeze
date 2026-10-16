# Desenvolvimento e distribuição

## Estrutura do Git

O repositório fica na raiz `papirus-breeze/`, branch `main`. `light/` e `dark/`
são diretórios comuns, sem submódulos ou `.git` próprios. A importação e a
organização foram registradas em commits de escopo: repositório, Light, Dark,
ferramentas e documentação.

Nenhum remoto foi configurado ou envio ao GitHub realizado durante a organização.
Os diretórios `dist/`, caches Python e bundles de histórico são ignorados.

## Comandos de manutenção

A ferramenta usa somente a biblioteca padrão do Python:

```bash
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
```

| Ação | Efeito |
| --- | --- |
| `check` | Verifica os hashes dos arquivos de cada variante, sem aplicar tema |
| `test` | Executa os testes de Light e Dark em processos isolados |
| `build` | Verifica hashes e gera os dois arquivos independentes |
| `manifest` | Recalcula os hashes locais após alterações intencionais; não altera versões |

Para uma única variante:

```bash
python3 tools/project.py test --variant light
python3 tools/project.py build --variant dark
```

A verificação de dependências da sessão é diferente da integridade:

```bash
python3 light/install.py --check
python3 dark/install.py --check
```

Esses comandos verificam também acesso ao Plasma por D-Bus. Não são necessários
para gerar um arquivo em um ambiente que apenas tenha Python.

## Fluxo após editar arquivos

```bash
python3 tools/project.py manifest
python3 tools/project.py check
python3 tools/project.py test
python3 tools/project.py build
git diff --check
git status --short
```

Revise o diff antes do commit. Os testes validam integridade, portabilidade,
instalação/restauração, composição do layout e integração dos perfis Konsole/Fish.
Alguns checks são pulados se ferramentas opcionais como Node ou Fish estiverem
ausentes; consulte a saída para saber a cobertura efetiva. Na organização local,
os 30 testes passaram sem falhas.

Ao adicionar/remover SVGs, revise também os totais e diretórios esperados nos
checks de exportação. Os testes de layout devem continuar confirmando um painel
por monitor, altura de 32 px, lista de apps fixados vazia e o ícone próprio.

`manifest` recalcula somente o mapa SHA-256 de cada pacote. Quando publicar uma
nova versão visual, atualize também `manifest.json`, o `KPlugin.Version` do tema
global, referências de versão em docs/build e a expectativa de versão dos testes.
Mantenha o registro de alterações coerente com o conteúdo final.

## Arquivos de distribuição

A versão atual gera:

```text
light/dist/papirus-breeze-light-1.0.11.tar.gz
dark/dist/papirus-breeze-dark-1.0.11.tar.gz
```

Cada arquivo é instalável sozinho. O empacotador preserva as licenças e créditos
da respectiva variante e exclui Git, caches e outros arquivos de distribuição.
Esses arquivos não entram no Git; podem ser anexados a uma release quando houver
publicação. O repositório completo contém ambas as variantes e documentação comum.

## Commits de escopo

Use mensagens que indiquem a área afetada, por exemplo:

```text
feat(light): ajusta a paleta clara
fix(layout): mantém tarefas sem aplicativos fixados
feat(icons): atualiza o SVG do lançador nas duas variantes
build(tools): melhora a verificação dos pacotes
docs: registra instalação e personalização
```

Inclua o manifesto atualizado junto dos arquivos da variante modificados, pois
seu instalador recusa arquivos com hashes divergentes. Não edite automaticamente
a configuração do desktop ao executar testes de desenvolvimento.

## GitHub Desktop

Adicione a pasta **`papirus-breeze` como repositório local existente** no GitHub
Desktop. O Git já está inicializado; não crie outro repositório dentro de `light/`
ou `dark/`. Confira a branch `main`, o histórico de commits e as licenças.

Quando quiser publicar, use o fluxo de publicação do GitHub Desktop para escolher
nome, conta e visibilidade. Até essa ação, o trabalho permanece local e sem remoto.
Os históricos anteriores estão preservados conforme [Migração](MIGRATION.md).
