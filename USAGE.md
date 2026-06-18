# rocksoft-koda — przewodnik użytkownika

Plugin `rocksoft-koda` dodaje do Claude Code zestaw narzędzi discovery od Rocksoft. Po instalacji w sesji Claude Code dostępne są dwie rzeczy:

1. **Skill `rs-discovery`** — ustrukturyzowana rozmowa discovery, która zamienia surowy pomysł w jeden plik specyfikacji (`context/discovery/discovery-notes.md`) i — opcjonalnie — otwiera z nim Pull Request w wybranym repozytorium.
2. **Serwer MCP `rocksoft-mcp`** — połączenie HTTP z Rocksoft Flow (`https://flow.rocksoft.co/mcp/...`), z którego skill korzysta do listowania repozytoriów, pobierania kontekstu projektu i otwierania PR-ów.

---

## Instalacja

```bash
# z repozytorium git
claude plugin marketplace add https://github.com/Rocksoft-IT/rocksoft-koda-plugin
claude plugin install rocksoft-koda@rocksoft
```

Po instalacji Claude Code automatycznie ładuje skill `rs-discovery` i podłącza serwer MCP `rocksoft-flow`. Nie trzeba nic więcej konfigurować.

---

## Do czego służy `rs-discovery`

`rs-discovery` to **facylitator rozmowy discovery**, nie generator treści. Zadaje pytania — jedno na raz — i zapisuje wyłącznie to, co powiedział użytkownik. Efektem jest jeden, wspólny dla zespołu (ludzi i agentów) dokument kontekstowy, na którym można budować dalszą pracę.

Obsługuje dwa tryby, wykrywane automatycznie:

- **Greenfield** — nowy projekt od zera. Wykrywany, gdy katalog roboczy nie ma markerów istniejącego projektu (historii gita, lockfile'ów itp.).
- **Brownfield** — istotna zmiana w istniejącym systemie (nowy moduł, duża funkcja, zmiana architektoniczna). Wykrywany po markerach projektu; w tym trybie skill **najpierw czyta kod**, a dopiero potem pyta — nie każe użytkownikowi recytować faktów, które są w repozytorium.

### Kiedy używać

- Start nowego projektu lub aplikacji od zera.
- Nowy moduł, znacząca funkcja albo zmiana architektoniczna w istniejącym systemie.
- Chcesz „przemaglować" pomysł, zanim zaczniesz budować (stress-test planu).
- Wznowienie niedokończonej sesji discovery (skill sam wykrywa istniejący `discovery-notes.md` i proponuje kontynuację).

### Kiedy NIE używać

Do małych, lokalnych zmian: pojedynczy bugfix, szybki refactor, zmiana kolorów/odstępów/tekstów, poprawka jednego komponentu. Skill sam to rozpozna na etapie triage i odmówi pełnego discovery, wskazując lżejszą ścieżkę.

---

## Jak uruchomić

W dowolnej sesji Claude Code wystarczy opisać, co chcesz zrobić — skill aktywuje się na frazy typu:

- „nowy projekt", „od zera", „greenfield"
- „shape an idea", „discovery session", „grill me on this"
- „dodaj funkcję do mojej aplikacji", „brownfield", „istniejący projekt"

Przykłady:

```
Pomóż mi zaszejpować nowy moduł autoryzacji — discovery session.
```

```
rs-discovery aplikacja z przepisami, która podpowiada posiłki z tego, co masz w lodówce
```

```
rs-discovery @notes/pomysl.md
```

Trzy sposoby przekazania pomysłu:

| Sposób | Przykład | Zachowanie |
|---|---|---|
| Pomysł inline | `rs-discovery apka do przepisów...` | Pomysł zapisany dosłownie jako punkt wyjścia |
| Plik z notatkami | `rs-discovery @notes/idea.md` | Skill czyta plik w całości i traktuje go jako pomysł |
| Bez argumentu | „discovery session" | Skill poprosi o opisanie pomysłu własnymi słowami |

Rozmowa toczy się **w języku użytkownika** (np. po polsku), ale artefakty na dysku są **zawsze po angielsku** — żeby były przenośne między zespołami i narzędziami.

---

## Przebieg sesji — krok po kroku

### Krok 0 — triage zakresu

Skill ocenia, czy zmiana jest na tyle duża, że pełne discovery ma sens. Jeśli to drobiazg — odsyła do lżejszej ścieżki i kończy.

### Krok 0.5 — wykrycie wznowienia

Jeśli istnieje już `context/discovery/discovery-notes.md`, skill proponuje: **wznów od następnej fazy** (rekomendowane), **zacznij od nowa** (stara wersja trafia do archiwum) albo **anuluj**. Ukończone fazy nie są powtarzane — są streszczane jednym zdaniem.

### Krok 0.7 — tożsamość i repozytorium (WYMAGANE)

Przed pytaniami merytorycznymi skill zbiera trzy obowiązkowe pola — bez nich sesja nie idzie dalej:

1. **E-mail klienta** — identyfikuje osobę prowadzącą discovery i służy do pobrania listy repozytoriów z Rocksoft Flow.
2. **Repozytorium** — skill woła narzędzie MCP `list_repositories` i pokazuje listę repozytoriów przypisanych do e-maila; użytkownik wybiera jedno. Nie ma trybu „bez repozytorium".
3. **Nazwa projektu / zmiany** — robocza nazwa tego, co szejpujemy.

Po wyborze repozytorium skill pobiera jego kontekst serwer-side (narzędzie MCP `get_repository_context`): `CLAUDE.md`, `context/foundation/tech-stack.md`, `context/prd/prd.md` — o ile istnieją. **Nigdy nie klonuje repo lokalnie** — dostęp do GitHuba ma wyłącznie serwer Rocksoft Flow.

### Krok 1 — wykrycie typu kontekstu

Greenfield czy brownfield — na podstawie sygnałów w katalogu roboczym (historia gita, lockfile'y, manifesty). Wynik jest potwierdzany z użytkownikiem i można go nadpisać.

### Fazy discovery (1–6)

Każda faza działa w tej samej pętli: jedno pytanie na raz, rekomendowana odpowiedź zawsze pierwsza, zawsze dostępna opcja „nie wiem / wróćmy do tego", potwierdzenie decyzji przed zapisem.

| Faza | Co powstaje |
|---|---|
| 1. Problem i persona | Wizja, problem, kto go odczuwa i co go to dziś kosztuje. Brownfield: dodatkowo opis obecnego systemu i co **nie może się zepsuć**. |
| 2. Dostęp i role | Jak użytkownik dostaje się do produktu (login / profil lokalny / klucz / brak) i model ról. Brownfield: skill odczytuje obecny model z kodu i pyta tylko o zmiany. |
| 3. Pierwszy inkrement i kryteria sukcesu | Pierwszy przepływ end-to-end, który dostarcza realną wartość (może być duży — to nie jest spychanie do minimalnego MVP). Kryteria Primary / Secondary / Guardrails plus swobodna estymata czasowa. |
| 4. Wymagania funkcjonalne | Lista FR-ów (`FR-001: [Aktor] może [zdolność]`) z priorytetami; brownfield dodaje tag `new / modified / preserved`. Każdy FR przechodzi jedną rundę sokratejskiego challenge'u. Plus przynajmniej jedna user story w Given/When/Then. |
| 5. Logika biznesowa i ograniczenia | Jedna deklaratywna reguła domenowa, która odróżnia produkt od zwykłego CRUD-a (skill wykrywa anty-wzorzec „pustego CRUD-a" i nazywa go wprost). Plus wymagania niefunkcjonalne. Brownfield: dodatkowo zachowania i kontrakty do zachowania. |
| 6. Kadrowanie i non-goals | Typ produktu, skala docelowa i jawna lista rzeczy, których ten zakres **nie** buduje. |

Po drodze skill na bieżąco buduje **glosariusz** (język wspólny domeny) i — rzadko, tylko dla decyzji trudnych do odwrócenia — zapisuje **ADR-y**. Wszystko jako sekcje jednego pliku notatek.

### Krok 8 — miękka bramka jakości

Skill sprawdza kompletność notatek (access control, logika biznesowa, non-goals, glosariusz, a dla brownfield — zachowane zachowania) i drukuje scorecard. Braki są nazwane konkretnie, z konsekwencją. Użytkownik może je uzupełnić albo świadomie zaakceptować — bramka ostrzega, ale nie blokuje.

### Krok 9 — domknięcie

Finalny zapis `discovery-notes.md`, przegląd decyzji pod kątem ADR-ów i krótkie podsumowanie sesji.

### Krok 10 — Pull Request ze specyfikacją

Na koniec skill **zawsze pyta** (nigdy nie robi tego automatycznie), czy otworzyć Pull Request ze specyfikacją w repozytorium wybranym w kroku 0.7:

- **„Tak, otwórz PR"** — narzędzie MCP `create_spec_pr` tworzy serwer-side nową gałąź w repozytorium, dodaje do niej `discovery-notes.md` i otwiera PR do gałęzi domyślnej. Specyfikacja **nigdy nie trafia bezpośrednio na main** — zawsze przechodzi przez review. Po sukcesie dostajesz numer PR, nazwę gałęzi i link.
- **„Jeszcze nie — zostaw lokalnie"** — plik zostaje w `context/discovery/discovery-notes.md`; PR można otworzyć później, ponownie uruchamiając `rs-discovery`.

---

## Co dostajesz na końcu

Jeden plik: `context/discovery/discovery-notes.md` (w bieżącym katalogu roboczym). Zawiera:

- **frontmatter** — projekt, klient (e-mail), repozytorium, typ kontekstu, typ produktu, skala, estymata, checkpoint sesji,
- **sekcje produktowe** — Vision & Problem, User & Persona, Access Control, Success Criteria, Functional Requirements, User Stories, Business Logic, Non-Functional Requirements, Non-Goals (brownfield dodatkowo: Current System oraz Constraints & Preserved Behavior),
- **Glossary** — kanoniczne terminy domenowe z listą synonimów do unikania,
- **Decisions** — ADR-y (tylko decyzje trudne do odwrócenia, zaskakujące bez kontekstu i będące realnym trade-offem),
- bloki informacyjne — Open Questions, Quality cross-check, `Forward: tech-stack` (zaparkowane opinie o stacku — discovery samo **nigdy** nie rekomenduje frameworka, bazy ani platformy).

Plik jest checkpointowany po każdej fazie, więc sesję można przerwać w dowolnym momencie i wznowić później.

---

## Zasady, na które możesz liczyć

- **Skill niczego nie wymyśla** — zapisuje tylko to, co powiedziałeś; brakujące wartości dopytuje.
- **Jedno pytanie na raz** — żadnych ścian pytań.
- **Rekomendacja zawsze pierwsza** — plus opcja „nie wiem", więc nigdy nie musisz zgadywać.
- **Brownfield: kod przed pytaniem** — skill czyta repozytorium zamiast kazać Ci je opisywać.
- **Neutralność technologiczna** — żadnych pytań o framework, bazę czy hosting; to decyzje późniejsze.
- **Żadnych cichych wysyłek** — wszystko, co idzie do Rocksoft Flow (PR), jest jawnie potwierdzane przez Ciebie.
- **Brak lokalnego gita** — cały dostęp do repozytoriów (odczyt kontekstu, otwarcie PR) odbywa się serwer-side przez Rocksoft Flow.

---

## Wymagania i rozwiązywanie problemów

| Sytuacja | Co się dzieje | Co zrobić |
|---|---|---|
| Rocksoft Flow MCP nieosiągalny | Sesja zatrzymuje się na kroku 0.7b z komunikatem błędu | Sprawdź połączenie / ponów próbę |
| Brak repozytoriów dla e-maila | Sesja zatrzymuje się | Poproś admina Rocksoft o przypisanie repozytorium do Twojego e-maila |
| Narzędzie `list_repositories` / `create_spec_pr` niewystawione | Skill mówi o tym wprost i zatrzymuje się (bez obejść) | Poproś admina Rocksoft Flow o dopięcie narzędzia w n8n |
| Brak plików kontekstu w repo (`CLAUDE.md` itd.) | To normalne — discovery rusza od zera | Nic; skill o tym poinformuje |
| `Bad credentials` przy otwieraniu PR | Token GitHub po stronie n8n nie ma uprawnień do repo | Skontaktuj się z adminem Rocksoft |

---

## Wersja

Dokument dotyczy pluginu `rocksoft-koda` w wersji `0.1.9`.
