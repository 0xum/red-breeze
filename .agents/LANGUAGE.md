# Language policy

## English by default

Use English for canonical Markdown, contributor instructions, code comments,
docstrings, CLI menus/help/errors, test diagnostics, authored metadata descriptions,
and new commit/PR descriptions. Keep command names, flags, theme IDs, file formats,
configuration keys, and public profile names stable unless changing them is part
of the task. Communicate with users in their preferred language.

## Optional Brazilian Portuguese

`README.pt-BR.md` is an optional translated quick-start guide. Link it from the
English README and link it back to the English source. It must say that installer
output is English and link to English technical docs for untranslated details.
Additional pt-BR guides may use an explicit `.pt-BR.md` suffix or `docs/pt-BR/`
directory and must link to their English source. Do not place Portuguese prose in
an unmarked canonical English document.

When changing behavior covered by an existing translation, update its instructions
or clearly mark the affected translation as outdated. Translation coverage may be
partial; do not imply that every guide or CLI message has a Portuguese version.
Avoid creating duplicate translations of the same guide in different locations.

## Preserve provenance

Do not translate or rewrite third-party license texts, original author names,
source URLs, historical Git commits, recorded generation prompts, or upstream
localized metadata as part of a language cleanup. English metadata defaults may
coexist with upstream localized entries. Translate project-authored explanatory
prose while retaining legal notices and the meaning of historical records.

## Review

Check default help and menu output, Markdown links/anchors, standalone package
instructions, and references to renamed English headings. Refresh variant
manifests after changing covered docs/scripts, and rebuild archives so distributed
instructions match the repository. Do not change desktop appearance for language-only edits.
