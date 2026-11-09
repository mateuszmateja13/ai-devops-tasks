# Simple Task API

## Opis

Simple Task API to REST API do zarządzania zadaniami, napisane w Node.js z wykorzystaniem frameworka Express i bazy danych MongoDB.

Funkcje:

- tworzenie, odczytywanie, aktualizacja i usuwanie zadań (CRUD),
- filtrowanie zadań według statusu i priorytetu,
- prosta autoryzacja użytkowników oparta na tokenach JWT.

## Instalacja

### Wymagania

- Node.js w wersji 18 lub nowszej
- MongoDB (lokalnie lub w chmurze, np. MongoDB Atlas)

### Kroki

1. Sklonuj repozytorium i przejdź do katalogu projektu:

   ```bash
   git clone https://github.com/<uzytkownik>/simple-task-api.git
   cd simple-task-api
   ```

2. Zainstaluj zależności:

   ```bash
   npm install
   ```

3. Utwórz plik `.env` w katalogu głównym:

   ```env
   PORT=3000
   MONGODB_URI=mongodb://localhost:27017/simple-task-api
   JWT_SECRET=zmien-na-dlugi-losowy-ciag
   ```

4. Uruchom serwer:

   ```bash
   npm start
   ```

   API będzie dostępne pod adresem `http://localhost:3000`.

## Użycie

1. Zarejestruj użytkownika:

   ```bash
   curl -X POST http://localhost:3000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "jan", "password": "tajne-haslo"}'
   ```

2. Zaloguj się i zapisz otrzymany token:

   ```bash
   curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "jan", "password": "tajne-haslo"}'
   ```

   Odpowiedź: `{ "token": "eyJhbGciOiJIUzI1NiIs..." }`

3. Dodaj zadanie, przekazując token w nagłówku `Authorization`:

   ```bash
   curl -X POST http://localhost:3000/api/tasks \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"title": "Przygotować raport", "status": "todo", "priority": "high"}'
   ```

4. Pobierz zadania o wysokim priorytecie, które są w toku:

   ```bash
   curl "http://localhost:3000/api/tasks?status=in-progress&priority=high" \
     -H "Authorization: Bearer <token>"
   ```

## Endpointy API

### Autoryzacja

| Metoda | Endpoint | Opis |
|--------|----------|------|
| `POST` | `/api/auth/register` | Rejestracja nowego użytkownika |
| `POST` | `/api/auth/login` | Logowanie, zwraca token JWT |

### Zadania

Wszystkie endpointy wymagają nagłówka `Authorization: Bearer <token>`.

| Metoda | Endpoint | Opis |
|--------|----------|------|
| `GET` | `/api/tasks` | Lista zadań, opcjonalne filtry `status` i `priority` |
| `GET` | `/api/tasks/:id` | Szczegóły jednego zadania |
| `POST` | `/api/tasks` | Utworzenie zadania |
| `PUT` | `/api/tasks/:id` | Aktualizacja zadania |
| `DELETE` | `/api/tasks/:id` | Usunięcie zadania |

### Model zadania

| Pole | Typ | Wymagane | Dozwolone wartości |
|------|-----|----------|--------------------|
| `title` | string | tak | — |
| `description` | string | nie | — |
| `status` | string | nie | `todo` (domyślnie), `in-progress`, `done` |
| `priority` | string | nie | `low`, `medium` (domyślnie), `high` |

### Kody odpowiedzi

| Kod | Znaczenie |
|-----|-----------|
| `200` | Operacja zakończona sukcesem |
| `201` | Zasób został utworzony |
| `400` | Nieprawidłowe dane wejściowe |
| `401` | Brak lub nieprawidłowy token |
| `404` | Zadanie nie istnieje |
| `500` | Błąd serwera |
