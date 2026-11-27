# Rocksoft Koda

Plugin do Claude (Claude Desktop, claude.ai, Claude Code) i OpenAI Codex (CLI, rozszerzenie IDE, Codex cloud), który zamienia prośbę klienta o nową funkcjonalność lub zmianę w gotowe do realizacji issue w jego repozytorium. Dwa skille (`rs-feature` i `rs-status`) plus bramka MCP Rocksoft (`mcp.rocksoft.pl`).

## Co zawiera

- **Skill `rs-feature`** — jedyny punkt wejścia. Po zalogowaniu wybiera repozytorium, czyta kontekst projektu, dobiera głębokość rozmowy (quick / feature / initiative), prowadzi brainstorming i planowanie, a na końcu — po jawnym potwierdzeniu — tworzy issue przez Rocksoft Flow. Rozmowa w języku klienta, issue po angielsku.
- **Skill `rs-status`** — wszystko, co dzieje się po utworzeniu issue, w czterech przepływach: status („co na mnie czeka”), decyzja w pull requeście (omówienie w Twoim czacie, potem zaakceptowanie, prośba o zmiany albo odpowiedzi na otwarte pytania), wyjaśnienie nieudanego lub zablokowanego przebiegu i jego wznowienie z Twoim komentarzem oraz opinia o pluginie lub Kodzie. Każda akcja zmieniająca coś wykonuje się dopiero po Twoim jawnym „tak” na pokazanym tekście. Skill nie scala pull requestów i nie tworzy issue.
- **MCP `rocksoft-koda`** — połączenie HTTPS z `https://mcp.rocksoft.pl/koda/`, uwierzytelnione logowaniem Microsoft (konto służbowe) — w Claude Code przez `/mcp`, w Codex przez `codex mcp login rocksoft-koda`. `rs-feature` używa trzech narzędzi: `list_repositories`, `get_repository_context`, `create_feature_issue`, a `rs-status` narzędzi statusu, decyzji, wznawiania przebiegów i `send_feedback` — żadne nie przyjmuje e-maila, tożsamość klienta wstrzykuje bramka. Kontrakt: [docs/flow-contract.md](docs/flow-contract.md). Po aktualizacji pluginu konnektor zmienił nazwę — zaloguj się ponownie (w Claude Code przez `/mcp`, w Codex przez `codex mcp login rocksoft-koda`).

Plugin nie czyta ani nie zapisuje plików na komputerze klienta i nie potrzebuje gita. Cały dostęp do repozytoriów odbywa się po stronie Rocksoft Flow.

## Instalacja

Plugin jest dystrybuowany **wyłącznie przez to repozytorium GitHub**, które pełni rolę marketplace'u. Nie ma paczek zip do pobierania ani wgrywania; każda instalacja i aktualizacja pochodzi bezpośrednio z repozytorium.

Konfigurację zespołu w repozytorium klienta (Claude Code i Codex, razem z rs-skills) opisuje [docs/client-setup.md](docs/client-setup.md).

### Claude Desktop / claude.ai

1. Ustawienia → Plugins → Browse plugins → dodaj marketplace z repozytorium GitHub `Rocksoft-IT/rocksoft-koda-plugin`.
2. Zainstaluj i włącz plugin `rocksoft-koda`. Przy konnektorze Rocksoft Flow kliknij **Connect**.
3. Na planach Team i Enterprise kroki 1 i 2 wykonuje administrator organizacji.

### Claude Code

```bash
claude plugin marketplace add https://github.com/Rocksoft-IT/rocksoft-koda-plugin
claude plugin install rocksoft-koda@rocksoft-koda
```

### Codex CLI

```bash
codex plugin marketplace add Rocksoft-IT/rocksoft-koda-plugin
codex plugin add rocksoft-koda@rocksoft-koda
codex mcp login rocksoft-koda
```

Plugin można też zainstalować z poziomu Codex poleceniem `/plugins`. Na maszynie bez przeglądarki użyj `codex mcp login rocksoft-koda --no-browser`. Stan logowania sprawdzisz przez `codex mcp list`; po zalogowaniu uruchom nową sesję Codex.

Aktualizacja do nowej wersji:

```bash
codex plugin marketplace upgrade rocksoft-koda
codex plugin add rocksoft-koda@rocksoft-koda
```

i nowa sesja Codex.

### Codex — rozszerzenie IDE

Rozszerzenie IDE nie ma przeglądarki pluginów, ale współdzieli z CLI konfigurację MCP i skille. Skonfiguruj serwer i zaloguj się:

```bash
codex mcp add rocksoft-koda --url https://mcp.rocksoft.pl/koda/
codex mcp login rocksoft-koda
```

Następnie skopiuj foldery `skills/rs-feature` i `skills/rs-status` z tego repozytorium do `~/.agents/skills/rs-feature` i `~/.agents/skills/rs-status`. Nie łącz tego z instalacją pluginu przez CLI — serwer `rocksoft-koda` zostałby zdublowany.

### Codex cloud / ChatGPT

Administrator workspace'u importuje marketplace z `https://github.com/Rocksoft-IT/rocksoft-koda-plugin` (Admin → Plugins → Import marketplace, bez podawania ścieżki). Członkowie workspace'u instalują plugin `rocksoft-koda` i klikają **Connect**. Plugin z serwerem MCP może być oznaczony jako „Desktop only”.

Dostęp do repozytoriów i organizacji egzekwuje bramka Rocksoft, nie plugin — instalacja w Codex niczego nie odblokowuje bez aktywnego dostępu organizacji.

## Użycie

W czacie wystarczy opisać, czego potrzebujesz:

```text
Chcę, żeby klienci mogli pobierać faktury jako PDF z panelu.
```

Claude lub Codex uruchomi `rs-feature`, potwierdzi repozytorium (na podstawie Twojego logowania do konnektora), dobierze tor rozmowy, zada pytania po kolei, pokaże pełny szkic issue i zapyta, czy je utworzyć. Szczegóły w [USAGE.md](USAGE.md).

Po utworzeniu issue zapytaj w czacie, co dalej:

```text
Co na mnie czeka?
```

Uruchomi się `rs-status`: pokaże Twoje zgłoszenia i decyzje czekające na Ciebie, pomoże zaakceptować pull request lub poprosić o zmiany, wyjaśni i wznowi zatrzymany przebieg albo przyjmie Twoją opinię (`Chcę dać opinię o Kodzie`).

## Struktura

```
.
├── .claude-plugin/
│   ├── plugin.json            # manifest pluginu (Claude)
│   └── marketplace.json       # definicja marketplace (Claude)
├── .codex-plugin/
│   └── plugin.json            # manifest pluginu (Codex)
├── .agents/
│   └── plugins/
│       └── marketplace.json   # definicja marketplace (Codex)
├── .mcp.json                  # serwer MCP rocksoft-koda (wspólny dla Claude i Codex)
├── docs/
│   ├── client-setup.md        # konfiguracja zespołu: Koda + rs-skills
│   └── flow-contract.md       # kontrakt narzędzi MCP (dla n8n)
├── skills/
│   ├── rs-feature/
│   │   ├── SKILL.md
│   │   └── references/        # tory rozmowy, szablon issue, glosariusz, ADR
│   └── rs-status/
│       ├── SKILL.md
│       └── references/        # status, decyzja, wznowienie, opinia
├── README.md
└── USAGE.md
```

## Plan rozwoju

Uwierzytelnianie klienta przez bramkę MCP z logowaniem Microsoft — patrz [issue #1](https://github.com/Rocksoft-IT/rocksoft-koda-plugin/issues/1) — już działa. Dostęp dla nowej organizacji wymaga ręcznej akceptacji przez Rocksoft: pierwsze logowanie zakłada wpis w stanie oczekującym, a skill informuje o tym klienta zamiast kontynuować.

## Wersja

`0.7.0`
