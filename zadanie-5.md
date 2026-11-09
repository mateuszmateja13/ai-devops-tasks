# Zadanie 5: diagram ASCII Art – klient, serwer aplikacji i baza danych

Model poproszono najpierw o prosty diagram architektury trójwarstwowej, a następnie o jego rozbudowę o opisy elementów i kierunki przepływu danych.

## Prompt 1 (prosty diagram)

```
Stwórz prosty diagram ASCII Art przedstawiający połączenie klienta, serwera aplikacji i bazy danych.
```

### Odpowiedź modelu

```
+-------------+   HTTP/HTTPS    +---------------------+      SQL       +-----------------+
|   KLIENT    | --------------> |  SERWER APLIKACJI   | -------------> |   BAZA DANYCH   |
| (przeglądarka|                |  (logika biznesowa, |                |  (PostgreSQL,   |
|  / aplikacja)| <-------------- |   API, np. Flask)   | <------------- |   MySQL itp.)   |
+-------------+  odpowiedź HTML |                     |  wyniki zapytań|                 |
                   / JSON       +---------------------+                +-----------------+
   warstwa                            warstwa                              warstwa
 prezentacji                         aplikacji                              danych
```

Klient wysyła żądanie HTTP do serwera aplikacji, który przetwarza logikę biznesową i w razie potrzeby odpytuje bazę danych językiem SQL. Baza zwraca wyniki, serwer formuje z nich odpowiedź (HTML lub JSON) i odsyła ją klientowi. To klasyczna architektura trójwarstwowa, w której klient nigdy nie łączy się z bazą bezpośrednio.

## Prompt 2 (opisy elementów i przepływ danych)

```
Dodaj do diagramu opisy elementów i kierunki przepływu danych.
```

### Odpowiedź modelu

```
 ┌────────────────────────┐            ┌────────────────────────────┐            ┌────────────────────────┐
 │        KLIENT          │            │     SERWER APLIKACJI       │            │      BAZA DANYCH       │
 │------------------------│            │----------------------------│            │------------------------│
 │ Przeglądarka WWW lub   │  (1) żądanie HTTP/HTTPS                 │            │ System zarządzania     │
 │ aplikacja mobilna.     │  GET/POST + dane formularza             │            │ bazą danych (RDBMS),   │
 │ Wyświetla interfejs,   │ ─────────────────────────▶              │            │ np. PostgreSQL, MySQL. │
 │ zbiera dane od         │            │ Odbiera żądania, sprawdza  │ (2) zapytanie SQL       │
 │ użytkownika i wysyła   │            │ uprawnienia, wykonuje      │ SELECT/INSERT/UPDATE    │
 │ żądania.               │            │ logikę biznesową (API,     │ ─────────────────────▶  │
 │                        │            │ np. Flask, Node.js).       │            │ Trwale przechowuje     │
 │                        │            │                            │ (3) wynik zapytania     │
 │                        │            │                            │ rekordy / status        │
 │                        │ (4) odpowiedź HTTP      ◀─────────────────────────── │ dane, pilnuje ich      │
 │                        │ HTML / JSON + kod 200   │                            │ spójności i obsługuje  │
 │                        │ ◀─────────────────────────              │            │ transakcje.            │
 └────────────────────────┘            └────────────────────────────┘            └────────────────────────┘
   WARSTWA PREZENTACJI                       WARSTWA APLIKACJI                       WARSTWA DANYCH
     (port 443/80)                             (np. port 8000)                         (np. port 5432)

 Przepływ:  Klient ──(1)──▶ Serwer ──(2)──▶ Baza ──(3)──▶ Serwer ──(4)──▶ Klient
```

Strzałki pokazują jeden pełny cykl żądania: klient wysyła żądanie HTTP (1), serwer aplikacji przekłada je na zapytanie SQL do bazy (2), baza zwraca wynik (3), a serwer opakowuje go w odpowiedź HTML lub JSON i odsyła klientowi (4). Porty przy warstwach to typowe wartości domyślne, przydatne np. przy konfiguracji Docker Compose czy reguł firewalla.

## Wnioski

Pierwszy prompt dał czytelny, ale ogólny szkic połączeń między warstwami. Doprecyzowanie oczekiwań w drugim prompcie sprawiło, że model dodał opis roli każdego komponentu, ponumerowaną kolejność przepływu danych oraz przykładowe porty, dzięki czemu diagram nadaje się już jako materiał dokumentacyjny, a nie tylko poglądowy.
