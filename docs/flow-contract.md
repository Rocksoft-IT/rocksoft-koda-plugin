# Kontrakt rs-feature ↔ Rocksoft Flow (n8n)

Skill `rs-feature` używa wyłącznie narzędzi MCP z Rocksoft Flow. Ten dokument
opisuje, czego skill oczekuje od serwera, żeby można było zbudować lub zmienić
workflow-y w n8n niezależnie od pluginu. Plan całości: issue #1 w tym repo.

## Narzędzia używane przez skill

### `list_repositories` (istnieje)

Wejście: `{ email }`. Wyjście: `{ repositories: [{ name, git_url, description }], email, count }`.
Bez zmian.

### `get_repository_context` (istnieje)

Wejście: `{ git_url, email }`. Wyjście: `{ repository: { owner, repo, git_url }, files: {...}, missing: [...] }`.
Bez zmian w fazie 0. W kolejnej fazie warto dołożyć `README.md` i listę plików
w `context/`.

### `create_feature_issue` (NOWE — do zbudowania)

Tworzy issue w repozytorium klienta. Nie tworzy gałęzi ani PR-a.

Wejście:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `git_url` | string | tak | Dokładnie to, co zwróciło `list_repositories`. Jedyne źródło prawdy o repozytorium, żadnego fallbacku. |
| `email` | string | tak | E-mail klienta. W fazie 0 deklarowany przez klienta; docelowo wstrzykiwany przez proxy OAuth. |
| `title` | string | tak | Tytuł issue, ≤ 80 znaków. |
| `body` | string | tak | Treść w markdownie, po angielsku, wg `skills/rs-feature/references/issue-template.md`. |
| `track` | `quick` \| `feature` \| `initiative` | tak | Głębokość rozmowy; trafia do etykiet i metadanych. |
| `labels` | string[] | nie | Skill wysyła `["rs-feature", "<track>"]`. Workflow zawsze dokłada `rs-feature`, nawet gdy pole jest puste. |

Zachowanie workflow-u:

1. **Autoryzacja:** zawołaj to samo źródło co `list_repositories` i sprawdź, że
   `git_url` należy do repozytoriów przypisanych do `email`. Jeśli nie, zwróć
   `{ error: "repository not assigned to <email>" }` i nic nie twórz. To jedyny
   test bezpieczeństwa w fazie 0, więc nie może być pominięty.
2. Sparsuj `git_url` na `owner/repo` (SSH i HTTPS).
3. Utwórz issue przez GitHub API z `title`, `body` i etykietami. Brakujące
   etykiety utwórz (`rs-feature`, `quick`, `feature`, `initiative`).
4. Dopisz na końcu `body` blok metadanych, jeśli go brakuje (klient, tor, wersja
   pluginu, data).
5. Zaloguj zdarzenie (kto, jakie repo, numer issue).

Wyjście:

```json
{
  "issue_url": "https://github.com/<owner>/<repo>/issues/<n>",
  "issue_number": 123,
  "repository": { "owner": "<owner>", "repo": "<repo>", "git_url": "<git_url>" },
  "labels": ["rs-feature", "feature"]
}
```

Błędy zwracaj jako `{ error: "<czytelny komunikat>" }`. Skill pokazuje komunikat
klientowi dosłownie, więc powinien być zrozumiały bez znajomości n8n.

### `get_issue_status` (NOWE — do zbudowania)

Zwraca postęp pracy Kody nad issue założonym przez `create_feature_issue`.
Tylko odczyt, niczego nie zmienia w repozytorium. Źródłem jest wyłącznie
GitHub: workflow czyta issue, komentarze Kody i PR-y przyrostów. Zmiany w
Cezarze nie są potrzebne.

Wejście:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `git_url` | string | tak | Dokładnie to, co zwróciło `list_repositories`. |
| `email` | string | tak | E-mail klienta (jak w `create_feature_issue`). |
| `issue_number` | integer | nie | Numer issue. Bez niego workflow zwraca listę ostatnich issue `rs-feature` w repozytorium. |

Zachowanie workflow-u:

1. **Autoryzacja:** identyczna jak w `create_feature_issue` — `git_url` musi
   należeć do repozytoriów przypisanych do `email`, inaczej
   `{ error: "repository not assigned to <email>" }`.
2. Sparsuj `git_url` na `owner/repo`.
3. **Z `issue_number`:** pobierz issue. Jeśli nie istnieje albo jest PR-em,
   zwróć `{ error: "issue #<n> not found in <owner>/<repo>" }`. Jeśli nie ma
   etykiety `rs-feature`, zwróć status i tak, ale z `status: "not_tracked"`
   (Koda nie pracuje nad takim issue).
4. **Bez `issue_number`:** pobierz issue z etykietą `rs-feature` (`state=all`,
   sortowane po `updated_at` malejąco, maksymalnie 10) i dla każdego policz
   status jak niżej.
5. Dla każdego issue zbierz:
   - **komentarze Kody** — komentarze pod issue, których treść zawiera
     znacznik `<!-- koda -->` (Cezar dokleja go do każdego swojego
     komentarza); „ostatni komentarz Kody” w regułach to najnowszy z nich,
   - **komentarze człowieka** — komentarze pod issue i pod PR-ami przyrostów
     bez tego znacznika, których autor nie jest botem (`user.type != "Bot"`),
   - **PR-y przyrostów** — PR-y w tym repozytorium, których tytuł zaczyna się
     od `[#<n> ` albo pierwsza linia treści to `Refs #<n>` / `Closes #<n>`
     (stan `all`, maksymalnie 20).
6. Wylicz `status` według reguł poniżej.

Reguły statusu (pierwsza pasująca wygrywa):

| `status` | Warunek |
|---|---|
| `done` | Issue zamknięte z `state_reason = completed`. |
| `closed` | Issue zamknięte z innym powodem (`not_planned`, `duplicate`, brak). |
| `queued` | Brak komentarzy Kody. Etykieta jest, praca jeszcze się nie zaczęła. |
| `in_progress` | Po ostatnim komentarzu Kody pojawił się komentarz człowieka na issue lub na PR-ze przyrostu albo został zmergowany PR przyrostu — to wznawia orkiestratora. |
| `failed` | Ostatni komentarz Kody to komunikat o niepowodzeniu (domyślnie zawiera „could not finish”; jeśli workspace ma własny `clientFailComment`, workflow porównuje z tym tekstem). |
| `ready_for_review` | Ostatni komentarz Kody zawiera linki do PR-ów (`/pull/`) i co najmniej jeden PR przyrostu jest otwarty. |
| `needs_input` | Ostatni komentarz Kody to numerowana lista pytań (linie `1. …`) bez linków do PR-ów — Koda czeka na odpowiedź klienta w komentarzu pod issue. |
| `in_progress` | Każdy inny przypadek (np. ostatni komentarz Kody to potwierdzenie startu). |

Wyjście z `issue_number`:

```json
{
  "repository": { "owner": "<owner>", "repo": "<repo>", "git_url": "<git_url>" },
  "issue": {
    "number": 123,
    "title": "Customers can export invoices as PDF",
    "url": "https://github.com/<owner>/<repo>/issues/123",
    "state": "open",
    "state_reason": null,
    "labels": ["rs-feature", "feature"],
    "created_at": "2026-09-20T10:00:00Z",
    "updated_at": "2026-09-22T14:30:00Z"
  },
  "status": "ready_for_review",
  "last_activity_at": "2026-09-22T14:30:00Z",
  "latest_koda_comment": {
    "created_at": "2026-09-22T14:30:00Z",
    "url": "https://github.com/<owner>/<repo>/issues/123#issuecomment-1",
    "body": "Work on this issue is ready: …"
  },
  "pull_requests": [
    {
      "number": 124,
      "title": "[#123 1/2] Invoice PDF export",
      "url": "https://github.com/<owner>/<repo>/pull/124",
      "state": "open",
      "draft": false,
      "merged_at": null
    }
  ]
}
```

- `latest_koda_comment` — `null`, gdy nie ma komentarzy Kody. `body` bez
  znacznika `<!-- koda -->`, przycięte do 2000 znaków.
- `pull_requests[].state` — `open` | `merged` | `closed` (zamknięty bez merge).
- `last_activity_at` — najnowszy z: `updated_at` issue, komentarze, zmiany PR-ów.

Wyjście bez `issue_number`:

```json
{
  "repository": { "owner": "<owner>", "repo": "<repo>", "git_url": "<git_url>" },
  "issues": [
    {
      "number": 123,
      "title": "Customers can export invoices as PDF",
      "url": "https://github.com/<owner>/<repo>/issues/123",
      "state": "open",
      "status": "ready_for_review",
      "last_activity_at": "2026-09-22T14:30:00Z",
      "pull_request_count": 2
    }
  ],
  "count": 1
}
```

Ograniczenia: status jest wyliczany z GitHuba, więc nie widać kolejki ani
bieżącego kroku agenta, a przejście do `in_progress` pojawia się dopiero
wraz z komentarzem startowym Kody. Dokładny status z Cezara (`workflow_runs`)
to osobny, późniejszy krok.

## Narzędzia, których skill już NIE używa

`create_spec_pr`, `create_change_pr`. Mogą zostać wystawione do czasu wycofania
starych wersji pluginu; `rs-feature` ma zakaz ich wołania.

## Zachowanie skilla, gdy `create_feature_issue` nie istnieje

Skill informuje klienta, że narzędzie nie jest wystawione, i drukuje gotowy
tytuł oraz treść issue w jednym bloku do przekazania opiekunowi z Rocksoft.
Dzięki temu plugin da się oddać klientom, zanim workflow będzie gotowy.

## Zachowanie skilla, gdy `get_issue_status` nie istnieje

Skill mówi klientowi, że sprawdzanie statusu nie jest jeszcze dostępne, i
podaje link do issue — postęp widać w komentarzach pod nim.

## Sygnał dla automatyki

Etykieta `rs-feature` na issue jest sygnałem, że treść powstała w
ustrukturyzowanym procesie i może być podjęta automatycznie. Etykieta toru
(`quick` / `feature` / `initiative`) pozwala dobrać ścieżkę realizacji.
