# rocksoft-shape

Claude Code plugin łączący Rocksoftowy skill discovery (`rs-shape`) z serwerem MCP `Rocksoft Flow`.

## Co zawiera

- **Skill `rs-shape`** — ustrukturyzowana rozmowa discovery, która zamienia surowy pomysł (greenfield lub brownfield) w zestaw artefaktów w `context/discovery/`. Wykrywa typ projektu po markerach w katalogu roboczym i dopasowuje fazy.
- **MCP `rocksoft-flow`** — połączenie HTTP do `https://flow.rocksoft.co/mcp/...` udostępniające narzędzia Rocksoft Flow w sesji Claude.

## Instalacja

### Z lokalnej ścieżki

```bash
claude plugin marketplace add /Users/jaroslawkrakowka/Desktop/Rocksoft/rocksoft-plugin-claude
claude plugin install rocksoft-shape@rocksoft
```

### Z repozytorium git

```bash
claude plugin marketplace add <git-url>
claude plugin install rocksoft-shape@rocksoft
```

Po instalacji Claude Code automatycznie:
- załaduje skill `rs-shape` (dostępny przez Skill tool lub frazy typu „shape an idea", „greenfield", „discovery session"),
- podłączy serwer MCP `rocksoft-flow` z konfiguracji `.mcp.json`.

## Użycie

W dowolnej sesji Claude Code napisz np.:

```
Pomóż mi zaszejpować nowy moduł autoryzacji — discovery session.
```

Claude wywoła `rs-shape` i poprowadzi przez fazy discovery, korzystając z narzędzi Rocksoft Flow przez MCP.

## Struktura

```
.
├── .claude-plugin/
│   ├── plugin.json          # manifest pluginu
│   └── marketplace.json     # definicja marketplace
├── .mcp.json                # serwer MCP rocksoft-flow
├── skills/
│   └── rs-shape/
│       ├── SKILL.md
│       └── references/
└── README.md
```

## Wersja

`0.1.0`