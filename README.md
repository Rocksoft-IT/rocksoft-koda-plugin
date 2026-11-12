# Rocksoft Koda

Plugin do Claude (Claude Desktop, claude.ai, Claude Code), który zamienia prośbę klienta o nową funkcjonalność lub zmianę w gotowe do realizacji issue w jego repozytorium. Jeden skill (`rs-feature`) plus bramka MCP Rocksoft (`mcp.rocksoft.pl`).

## Co zawiera

- **Skill `rs-feature`** — jedyny punkt wejścia. Po zalogowaniu wybiera repozytorium, czyta kontekst projektu, dobiera głębokość rozmowy (quick / feature / initiative), prowadzi brainstorming i planowanie, a na końcu — po jawnym potwierdzeniu — tworzy issue przez Rocksoft Flow. Rozmowa w języku klienta, issue po angielsku.
- **MCP `rocksoft-mcp`** — połączenie HTTPS z `https://mcp.rocksoft.pl/koda/`, uwierzytelnione logowaniem Microsoft (konto służbowe) przez `/mcp`. Skill używa trzech narzędzi: `list_repositories`, `get_repository_context`, `create_feature_issue` — żadne nie przyjmuje e-maila, tożsamość klienta wstrzykuje bramka. Kontrakt: [docs/flow-contract.md](docs/flow-contract.md).

Plugin nie czyta ani nie zapisuje plików na komputerze klienta i nie potrzebuje gita. Cały dostęp do repozytoriów odbywa się po stronie Rocksoft Flow.

## Instalacja

Plugin jest dystrybuowany **wyłącznie przez to repozytorium GitHub**, które pełni rolę marketplace'u. Nie ma paczek zip do pobierania ani wgrywania; każda instalacja i aktualizacja pochodzi bezpośrednio z repozytorium.

### Claude Desktop / claude.ai

1. Ustawienia → Plugins → Browse plugins → dodaj marketplace z repozytorium GitHub `Rocksoft-IT/rocksoft-koda-plugin`.
2. Zainstaluj i włącz plugin `rocksoft-koda`. Przy konnektorze Rocksoft Flow kliknij **Connect**.
3. Na planach Team i Enterprise kroki 1 i 2 wykonuje administrator organizacji.

### Claude Code

```bash
claude plugin marketplace add https://github.com/Rocksoft-IT/rocksoft-koda-plugin
claude plugin install rocksoft-koda@rocksoft-koda
```

## Użycie

W czacie wystarczy opisać, czego potrzebujesz:

```text
Chcę, żeby klienci mogli pobierać faktury jako PDF z panelu.
```

Claude uruchomi `rs-feature`, potwierdzi repozytorium (na podstawie Twojego logowania przez `/mcp`), dobierze tor rozmowy, zada pytania po kolei, pokaże pełny szkic issue i zapyta, czy je utworzyć. Szczegóły w [USAGE.md](USAGE.md).

## Struktura

```
.
├── .claude-plugin/
│   ├── plugin.json            # manifest pluginu
│   └── marketplace.json       # definicja marketplace
├── .mcp.json                  # serwer MCP rocksoft-mcp
├── docs/
│   └── flow-contract.md       # kontrakt narzędzi MCP (dla n8n)
├── skills/
│   └── rs-feature/
│       ├── SKILL.md
│       └── references/        # tory rozmowy, szablon issue, glosariusz, ADR
├── README.md
└── USAGE.md
```

## Plan rozwoju

Uwierzytelnianie klienta przez bramkę MCP z logowaniem Microsoft — patrz [issue #1](https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/1) — już działa. Dostęp dla nowej organizacji wymaga ręcznej akceptacji przez Rocksoft: pierwsze logowanie zakłada wpis w stanie oczekującym, a skill informuje o tym klienta zamiast kontynuować.

## Wersja

`0.3.0`
