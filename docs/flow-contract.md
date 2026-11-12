# Kontrakt rs-feature ↔ Rocksoft Flow (n8n)

Skill `rs-feature` używa wyłącznie narzędzi MCP z Rocksoft Flow, wystawionych
przez bramkę `https://mcp.rocksoft.pl/koda/`. Ten dokument opisuje, czego
skill oczekuje od serwera, żeby można było zbudować lub zmienić workflow-y w
n8n niezależnie od pluginu. Plan całości: issue #1 w tym repo.

## Tożsamość klienta

Żadne z narzędzi poniżej nie przyjmuje `email` jako argumentu. Tożsamość
klienta pochodzi z zweryfikowanego tokenu Microsoft Entra, który bramka
dołącza do każdego wywołania po zalogowaniu przez `/mcp` — katalog
repozytoriów klienta jest kluczowany dokładnie tym adresem logowania (bez
przemapowania UPN). `list_repositories` nadal zwraca ten e-mail w swojej
odpowiedzi, żeby skill mógł go użyć jako wartość metadanych `client:`.

## Odmowy dostępu na poziomie dzierżawcy (tenant)

Każde z trzech narzędzi poniżej może, zamiast zwykłej odpowiedzi, zwrócić
odmowę dostępu dla zalogowanej dzierżawcy:

```json
{ "error": "pending" }
```
```json
{ "error": "not_allowed" }
```
```json
{ "error": "revoked" }
```

- `pending` — pierwsze logowanie tej dzierżawcy; bramka założyła wiersz
  `mcp_tenant_access` (`plugin = koda`) i czeka na ręczną akceptację przez
  Rocksoft.
- `not_allowed` — dzierżawca nigdy nie miał dostępu.
- `revoked` — dostęp był przyznany i został cofnięty.

Zwykłe błędy (np. repozytorium nie znalezione) zachowują dotychczasowy
kształt `{ error: "<czytelny komunikat>" }`.

## Narzędzia używane przez skill

### `list_repositories` (istnieje)

Wejście: `{}` (brak argumentów). Wyjście: `{ repositories: [{ name, git_url,
description }], email, count }` — `email` to zalogowany adres, wstrzyknięty
przez bramkę.

### `get_repository_context` (istnieje)

Wejście: `{ git_url }`. Wyjście: `{ repository: { owner, repo, git_url },
files: {...}, missing: [...] }`.
Bez zmian poza usunięciem `email`. W kolejnej fazie warto dołożyć
`README.md` i listę plików w `context/`.

### `create_feature_issue` (NOWE — do zbudowania)

Tworzy issue w repozytorium klienta. Nie tworzy gałęzi ani PR-a.

Wejście:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `git_url` | string | tak | Dokładnie to, co zwróciło `list_repositories`. Jedyne źródło prawdy o repozytorium, żadnego fallbacku. |
| `title` | string | tak | Tytuł issue, ≤ 80 znaków. |
| `body` | string | tak | Treść w markdownie, po angielsku, wg `skills/rs-feature/references/issue-template.md`. |
| `track` | `quick` \| `feature` \| `initiative` | tak | Głębokość rozmowy; trafia do etykiet i metadanych. |
| `labels` | string[] | nie | Skill wysyła `["rs-feature", "<track>"]`. Workflow zawsze dokłada `rs-feature`, nawet gdy pole jest puste. |

`email` nie jest już polem wejściowym — tożsamość klienta pochodzi z
zalogowanej sesji (patrz "Tożsamość klienta" powyżej).

Zachowanie workflow-u:

1. **Autoryzacja:** sprawdź, że zalogowana dzierżawca ma dostęp (patrz
   "Odmowy dostępu" powyżej) i że `git_url` należy do repozytoriów
   przypisanych do tej dzierżawcy. Jeśli nie, zwróć `{ error: "repository not
   assigned to this account" }` i nic nie twórz. To jedyny test
   bezpieczeństwa w fazie 0, więc nie może być pominięty.
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
