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

## Narzędzia, których skill już NIE używa

`create_spec_pr`, `create_change_pr`. Mogą zostać wystawione do czasu wycofania
starych wersji pluginu; `rs-feature` ma zakaz ich wołania.

## Zachowanie skilla, gdy `create_feature_issue` nie istnieje

Skill informuje klienta, że narzędzie nie jest wystawione, i drukuje gotowy
tytuł oraz treść issue w jednym bloku do przekazania opiekunowi z Rocksoft.
Dzięki temu plugin da się oddać klientom, zanim workflow będzie gotowy.

## Sygnał dla automatyki

Etykieta `rs-feature` na issue jest sygnałem, że treść powstała w
ustrukturyzowanym procesie i może być podjęta automatycznie. Etykieta toru
(`quick` / `feature` / `initiative`) pozwala dobrać ścieżkę realizacji.
