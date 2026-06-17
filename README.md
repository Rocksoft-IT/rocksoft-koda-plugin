# Rocksoft Koda

Claude Code plugin łączący Rocksoftowy skill discovery (`rs-shape`) z serwerem MCP `Rocksoft Flow` flow.rocksoft.co.

## Co zawiera

- **Skill `rs-shape`** — ustrukturyzowana rozmowa discovery, która zamienia surowy pomysł (greenfield lub brownfield) w zestaw artefaktów w `context/discovery/`. Wykrywa typ projektu po markerach w katalogu roboczym i dopasowuje fazy.
- **MCP `rocksoft-flow`** — połączenie HTTPS do `https://flow.rocksoft.co/mcp/...` udostępniające narzędzia Rocksoft Flow w sesji Claude.

## Instalacja

### Z repozytorium git

```bash
claude plugin marketplace add https://github.com/Rocksoft-IT/claude-plugin
claude plugin install rocksoft-koda@rocksoft
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

`0.1.8`
