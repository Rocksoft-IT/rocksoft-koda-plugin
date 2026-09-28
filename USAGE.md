# rocksoft-koda — przewodnik użytkownika

Plugin `rocksoft-koda` pozwala zgłosić Rocksoftowi nową funkcjonalność lub zmianę bezpośrednio z rozmowy z Claude. Efektem jest kompletne issue w Twoim repozytorium, od którego zespół Rocksoft (i jego automatyka) zaczyna pracę.

Po instalacji w Claude dostępne są dwie rzeczy:

1. **Skill `rs-feature`** — prowadzi rozmowę i tworzy issue.
2. **Konnektor `rocksoft-mcp`** — połączenie z Rocksoft Flow (`flow.rocksoft.co`), które listuje Twoje repozytoria, czyta kontekst projektu i zakłada issue.

---

## Instalacja i pierwsze uruchomienie

Plugin instaluje się **bezpośrednio z repozytorium GitHub** `Rocksoft-IT/rocksoft-koda-plugin`, które jest jego marketplace'em. Nie ma żadnej paczki zip do pobrania; aktualizacje również przychodzą z repozytorium.

### Claude Desktop lub claude.ai

1. Otwórz Ustawienia → Plugins → Browse plugins.
2. Dodaj marketplace z GitHuba: `Rocksoft-IT/rocksoft-koda-plugin`.
3. Zainstaluj i włącz plugin `rocksoft-koda`, a przy konnektorze Rocksoft Flow kliknij **Connect**.

Na planach Team i Enterprise plugin i konnektor dodaje administrator Twojej organizacji. Poproś go o instalację, jeśli nie widzisz pluginu na liście.

### Claude Code

```bash
claude plugin marketplace add https://github.com/Rocksoft-IT/rocksoft-koda-plugin
claude plugin install rocksoft-koda@rocksoft-koda
```

---

## Jak zgłosić funkcjonalność

Napisz w czacie, czego potrzebujesz, własnymi słowami. Skill aktywuje się na zwykłe prośby, np.:

```text
Chcę, żeby klienci mogli pobierać faktury jako PDF z panelu.
```

```text
Potrzebujemy powiadomień SMS o zmianie statusu zamówienia.
```

```text
Popraw komunikat błędu przy nieudanym logowaniu — jest niezrozumiały.
```

Możesz też wywołać skill wprost: `/rs-feature` i opisać pomysł.

Rozmowa toczy się **w Twoim języku**. Issue powstaje **po angielsku**, żeby zespół i narzędzia Rocksoft mogły na nim polegać.

---

## Przebieg rozmowy

### 1. Kto zgłasza

Skill prosi o Twój e-mail (albo proponuje ten, który już zna) i potwierdza go. E-mail jest kluczem do listy repozytoriów, do których masz dostęp w Rocksoft Flow.

### 2. Które repozytorium

Skill pobiera Twoje repozytoria. Jeśli jest jedno, potwierdza je jednym zdaniem. Jeśli kilka, pokazuje listę do wyboru. Bez repozytorium nie da się iść dalej.

### 3. Kontekst projektu

Skill czyta pliki kontekstowe repozytorium po stronie Rocksoft Flow (jeśli istnieją) i streszcza w kilku zdaniach, jak rozumie projekt. Popraw go, jeśli coś się nie zgadza. Od tego momentu nie musisz opisywać rzeczy, które są w repozytorium.

### 4. Dobór głębokości rozmowy

Skill ocenia wielkość prośby i mówi wprost, który tor wybrał. Możesz go zmienić.

| Tor | Kiedy | Ile pytań |
|---|---|---|
| **quick** | drobna, lokalna zmiana: tekst, wygląd, jedno pole, oczywisty błąd | 2–4 |
| **feature** | nowa możliwość albo istotna zmiana w istniejącym produkcie | ok. 6–12 plus jedna runda „adwokata diabła” |
| **initiative** | nowy moduł, nowy produkt, zmiana architektury | pełny wywiad, ze słownikiem pojęć i decyzjami |

### 5. Pytania — jedno na raz

Zawsze jedno pytanie, zawsze z rekomendowaną odpowiedzią na początku i opcją „nie wiem, wróćmy do tego” na końcu. Skill dopytuje, gdy odpowiedź jest ogólna („wszyscy”, „zawsze”), i nie wymyśla niczego, czego nie powiedziałeś.

### 6. Szkic issue

Skill pokazuje **cały** szkic issue i pyta, co dodać, zmienić lub usunąć. Wskaże też braki, które utrudnią realizację (np. brak kryterium dla przypadku błędu). Możesz je uzupełnić albo świadomie zaakceptować.

### 7. Utworzenie issue

Skill pyta wprost: „Utworzyć to issue w `<repozytorium>`?”. Dopiero po Twoim „tak” woła Rocksoft Flow i podaje link oraz numer issue. Od tej pory postępy widać na samym issue.

Jeśli w danej chwili Rocksoft Flow nie ma jeszcze narzędzia do zakładania issue, skill wydrukuje gotowy tytuł i treść, żebyś mógł przekazać je swojemu opiekunowi w Rocksoft.

---

## Co zawiera issue

Stały układ, żeby czytał je zarówno człowiek, jak i automat:

- **Summary** — czego chcesz i dlaczego teraz,
- **Problem & context** — kto odczuwa problem, kiedy, ile to kosztuje; obecny stan systemu,
- **Scope** — pierwszy przyrost end-to-end oraz jawna lista rzeczy poza zakresem,
- **Requirements** i **Acceptance criteria** — wymagania z priorytetami i kryteria w formie Given/When/Then,
- **Constraints & preserved behavior** — co nie może się zepsuć,
- **Non-functional requirements**, **Open questions**,
- dla większych tematów: **Access & roles**, **Success criteria**, **Business rule**, **Glossary**, **Decisions**,
- **Metadata** — klient, repozytorium, tor, wersja pluginu.

---

## Zasady, na które możesz liczyć

- **Nic nie jest wysyłane bez Twojej zgody.** Najpierw pełny szkic, potem pytanie, potem jedno wywołanie.
- **Skill niczego nie wymyśla.** Brakujące informacje dopytuje albo zostawia w Open questions.
- **Bez technologii.** Skill nie pyta o framework, bazę czy hosting. Jeśli sam masz zdanie, trafi ono do osobnej sekcji notatek technicznych.
- **Bez plików i gita po Twojej stronie.** Wszystko dzieje się w rozmowie i po stronie Rocksoft Flow.

---

## Rozwiązywanie problemów

| Sytuacja | Co się dzieje | Co zrobić |
|---|---|---|
| Konnektor Rocksoft Flow niepołączony | Skill nie może pobrać repozytoriów | Ustawienia → Plugins → Rocksoft Flow → Connect; na Team/Enterprise poproś administratora |
| Brak repozytoriów dla e-maila | Skill zatrzymuje się po kroku 1 | Poproś opiekuna w Rocksoft o przypisanie repozytorium do Twojego e-maila |
| Narzędzie `create_feature_issue` niedostępne | Skill drukuje gotową treść issue | Prześlij ją opiekunowi w Rocksoft |
| Błąd „repository not assigned” | E-mail i repozytorium nie pasują do siebie | Sprawdź e-mail, wróć do wyboru repozytorium |
| Brak plików kontekstu w repozytorium | Normalne — skill oprze się na rozmowie | Nic |

---

## Wersja

Dokument dotyczy pluginu `rocksoft-koda` w wersji `0.2.0`.
