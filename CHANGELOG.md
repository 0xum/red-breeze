# Alterações

Este registro descreve as mudanças conhecidas do trabalho local. Não representa
releases ou tags já publicados no GitHub.

## Organização unificada — 16 de outubro de 2026

- Light e Dark reunidos em `light/` e `dark/`, com um Git na raiz.
- Históricos Git anteriores preservados fora do repositório, em bundles e metadados.
- Documentação central de instalação, aparência, personalização, manutenção e restauração.
- Ferramenta única para conferir integridade, executar testes, atualizar hashes e empacotar.
- Mantida a versão visual 1.0.11: a reorganização não altera o desktop instalado.

## 1.0.13

- Login passa a receber paleta, destaque vermelho, ícones, cursor e wallpaper.
- Corrigido o acesso a recursos que estavam somente na pasta pessoal privada.
- Paletas do greeter adaptam cores complementares para refletir Light/Dark.
- Adicionado acompanhamento opcional de um usuário via observador systemd, com
  perfis fixos administrativos e sem reiniciar o gerenciador de login.
- Suporte a Plasma Login Manager e SDDM, preservando autenticação e autologin.

## 1.0.12

- Corrigida a lixeira que aparecia como avatar no Dolphin: os nomes `user-trash`
  e `user-trash-full` agora têm ícones locais explícitos, incluindo aliases simbólicos.
- Incluídos os estados vazia/cheia vermelhos, preservando a forma Papirus em todos os tamanhos.
- Testes impedem a ausência desses aliases e sua troca pela geometria do ícone de usuário.

## 1.0.11

- Círculo central do lançador convertido em recorte transparente real.
- SVG usa `fill-rule="evenodd"`, mantendo o hexágono vermelho e o fundo vazado.

## 1.0.10

- Criado o lançador vetorial editável: hexágono vermelho arredondado com círculo central.
- Ícone incluído em ambos os temas de ícones, layouts nativos e atualização dos painéis existentes.

## 1.0.9

- Cursor do Konsole em bloco vermelho, com piscar e animação habilitados nos dois perfis.

## 1.0.8

- Perfis Konsole Light/Dark com sincronização nativa ao tema do sistema.
- Terminal com fundo branco/escuro, JetBrainsMono Nerd Font 11 pt e tamanho inicial de 96 × 24.
- Fish com saudação de três linhas e prompt Pure em uma linha, preservando configuração da distribuição.

## Base do conjunto

- Exportação das variantes Light/Dark, wallpaper e bloqueio adaptativos e instaladores de login.
- Layout nativo com um painel de 32 px por monitor, sem aplicativos fixados.
- Pastas, aliases genéricos, subpastas e ícones de sistema vermelhos.
- Estilo Plasma `PapirusBreezeRed` e ícone vermelho do Dolphin.
- Instaladores com backup, restauração, testes, manifestos SHA-256 e empacotamento independente.
