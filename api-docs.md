# GET /api/users

## Opis

Zwraca stronicowaną listę użytkowników. Wyniki można zawęzić do użytkowników o określonej roli. Gdy parametry nie zostaną podane, endpoint zwraca pierwszą stronę z 10 wynikami.

## Parametry zapytania

| Parametr | Typ | Wymagany | Domyślnie | Ograniczenia | Opis |
|----------|-----|----------|-----------|--------------|------|
| `page` | integer | nie | `1` | ≥ 1 | Numer strony wyników |
| `limit` | integer | nie | `10` | od 1 do 100 | Liczba wyników na stronę |
| `role` | string | nie | — | np. `admin`, `editor`, `user` | Zwraca tylko użytkowników o podanej roli |

## Przykładowe żądanie

```http
GET /api/users?page=2&limit=20&role=admin HTTP/1.1
Host: api.example.com
Accept: application/json
```

To samo żądanie wykonane przez `curl`:

```bash
curl -X GET "https://api.example.com/api/users?page=2&limit=20&role=admin" \
  -H "Accept: application/json"
```

## Przykładowa odpowiedź

**Status:** `200 OK`

```json
{
  "data": [
    {
      "id": 21,
      "name": "Anna Kowalska",
      "email": "anna.kowalska@example.com",
      "role": "admin"
    },
    {
      "id": 22,
      "name": "Piotr Nowak",
      "email": "piotr.nowak@example.com",
      "role": "admin"
    }
  ],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 42,
    "totalPages": 3
  }
}
```

### Pola odpowiedzi

| Pole | Typ | Opis |
|------|-----|------|
| `data` | array | Lista użytkowników na bieżącej stronie |
| `data[].id` | integer | Identyfikator użytkownika |
| `data[].name` | string | Imię i nazwisko |
| `data[].email` | string | Adres e-mail |
| `data[].role` | string | Rola użytkownika |
| `pagination.page` | integer | Numer bieżącej strony |
| `pagination.limit` | integer | Liczba wyników na stronę |
| `pagination.total` | integer | Łączna liczba użytkowników spełniających kryteria |
| `pagination.totalPages` | integer | Łączna liczba stron |

Jeśli `page` przekracza liczbę stron, endpoint zwraca `200 OK` z pustą tablicą `data`.

## Błędy

| Status | Przyczyna | Przykładowa odpowiedź |
|--------|-----------|-----------------------|
| `400 Bad Request` | `page` < 1, `limit` spoza zakresu 1–100, wartość niebędąca liczbą całkowitą lub nieznana `role` | `{ "error": "INVALID_PARAMETER", "message": "limit musi być liczbą od 1 do 100" }` |
| `500 Internal Server Error` | Nieoczekiwany błąd serwera | `{ "error": "INTERNAL_ERROR", "message": "Wystąpił błąd serwera" }` |
