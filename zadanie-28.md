# Zadanie 28 – Skrypt Python do zarządzania Jenkinsem przez API

## Pliki

| Plik | Zawartość |
|------|-----------|
| `jenkins-manager.py` | Klient Jenkins REST API: listowanie zadań, status ostatnich buildów, uruchamianie zadań |

## Architektura skryptu

Skrypt składa się z trzech warstw:

```
main()                      – argumenty wiersza poleceń, konfiguracja, kody wyjścia
  └── cmd_list / cmd_status / cmd_build   – formatowanie wyników dla użytkownika
        └── JenkinsClient                 – komunikacja z Jenkins REST API
              └── _request()              – jedno miejsce obsługi błędów HTTP i sieci
```

## Wykorzystane biblioteki

### Biblioteka zewnętrzna

| Biblioteka | Zastosowanie |
|------------|--------------|
| `requests` | Wysyłanie żądań HTTP, uwierzytelnianie Basic, weryfikacja certyfikatów SSL, timeouty, dekodowanie JSON |

Używany jest obiekt `requests.Session`, który przechowuje dane logowania i nagłówki między żądaniami oraz utrzymuje otwarte połączenie TCP – kolejne zapytania są szybsze. Instalacja: `pip install requests`.

### Biblioteka standardowa Pythona

| Moduł | Zastosowanie |
|-------|--------------|
| `argparse` | Interfejs wiersza poleceń z podpoleceniami `list`, `status`, `build` |
| `os` | Odczyt zmiennych środowiskowych z danymi logowania |
| `sys` | Kody wyjścia, wypisywanie błędów na stderr |
| `time` | Przerwy między zapytaniami przy oczekiwaniu na build, limit czasu |
| `datetime` | Zamiana znaczników czasu Jenkinsa (milisekundy) na czytelne daty |
| `urllib.parse.quote` | Kodowanie nazw zadań ze spacjami i znakami specjalnymi w URL |

Skrypt świadomie **nie używa** gotowych bibliotek typu `python-jenkins` czy `jenkinsapi`. Komunikuje się z REST API bezpośrednio – widać dokładnie, jakie żądania wysyła, a jedyną zależnością jest `requests`.

## Jak działa Jenkins REST API

Niemal każda strona Jenkinsa ma wersję maszynową pod tym samym adresem z dopiskiem `/api/json`.

| Metoda | Endpoint | Zastosowanie w skrypcie |
|--------|----------|-------------------------|
| `GET` | `/api/json` | Lista wszystkich zadań |
| `GET` | `/job/<nazwa>/api/json` | Dane jednego zadania z ostatnim buildem |
| `POST` | `/job/<nazwa>/build` | Uruchomienie zadania bez parametrów |
| `POST` | `/job/<nazwa>/buildWithParameters` | Uruchomienie zadania z parametrami |
| `GET` | `/queue/item/<id>/api/json` | Stan elementu w kolejce |
| `GET` | `/crumbIssuer/api/json` | Token CSRF (crumb) |

**Parametr `tree`** określa, które pola Jenkins ma zwrócić, np. `jobs[name,lastBuild[number,result]]`. Bez niego odpowiedź zawiera wszystkie dane i przy dużej instancji może mieć rozmiar rzędu megabajtów.

## Działanie klasy `JenkinsClient`

### Konstruktor

Tworzy sesję `requests.Session` z danymi logowania (`auth = (użytkownik, token)`), ustawieniem weryfikacji SSL i nagłówkiem `Accept: application/json`.

### `_request()` – centralna obsługa błędów

Wszystkie żądania przechodzą przez tę metodę. Łapie wyjątki sieciowe biblioteki `requests` i błędne kody HTTP, zamieniając je na jeden wyjątek `JenkinsError` z czytelnym komunikatem:

| Sytuacja | Komunikat |
|----------|-----------|
| `ConnectionError` | Nie można połączyć się z serwerem – sprawdź adres i sieć |
| `Timeout` | Przekroczono limit czasu |
| `SSLError` | Błąd certyfikatu SSL |
| HTTP 401 | Nieprawidłowy użytkownik lub token API |
| HTTP 403 | Brak uprawnień do operacji lub problem z tokenem CSRF |
| HTTP 404 | Nie znaleziono zasobu (np. zadanie nie istnieje) |
| inny kod błędu | Błąd HTTP z numerem kodu |

Dzięki temu reszta kodu nie musi obsługiwać błędów osobno, a użytkownik nie widzi stosu wywołań.

### `list_jobs()` – listowanie zadań

1. Buduje zagnieżdżony parametr `tree`, który w **jednym zapytaniu** schodzi trzy poziomy w głąb folderów i projektów Multibranch (zamiast osobnego zapytania na każdy folder).
2. Funkcja rekurencyjna `walk` przechodzi przez wynik: element z polem `jobs` to folder – trzeba wejść głębiej; element bez niego to zadanie – trafia na listę.

### `_job_path()` – adresowanie zadań w folderach

Zamienia nazwę `frontend/web app` na ścieżkę `/job/frontend/job/web%20app` – tak Jenkins adresuje zadania w folderach. Każdy segment jest kodowany przez `quote`.

### `get_job_status()` – status zadania

Pobiera dane jednego zadania razem z polem `lastBuild` (numer, wynik, czy trwa, czas startu i trwania).

### `trigger_build()` – uruchamianie zadania

1. Pobiera token CSRF przez `_get_crumb()`. Nowsze wersje Jenkinsa przy uwierzytelnianiu tokenem API go nie wymagają, więc odpowiedź 404 jest ignorowana.
2. Wysyła `POST` na `/build` albo – gdy podano parametry – na `/buildWithParameters`.
3. Zwraca adres z nagłówka `Location`. Jenkins nie podaje od razu numeru buildu, tylko adres elementu w **kolejce**, bo numer jest nadawany dopiero, gdy znajdzie się wolny agent.

### `wait_for_build()` – oczekiwanie na wynik

1. Odpytuje kolejkę, aż pojawi się pole `executable` z adresem buildu (lub `cancelled` – wtedy błąd).
2. Odpytuje build, aż pole `building` zmieni się na `false`, i zwraca wynik.
3. Całość ma limit 30 minut, żeby skrypt nie czekał w nieskończoność.

## Warstwa prezentacji i `main()`

- `describe_last_build()` zamienia dane buildu na jedną linię: ikona, numer, wynik, data startu, czas trwania. Osobno obsługuje build w trakcie (🔄) i zadanie bez buildów (⚪).
- `main()` sprawdza obecność zmiennych `JENKINS_URL`, `JENKINS_USER`, `JENKINS_TOKEN`, tworzy klienta, wywołuje odpowiednią funkcję `cmd_*` i zamienia `JenkinsError` na komunikat na stderr.

### Kody wyjścia

| Kod | Znaczenie |
|-----|-----------|
| `0` | Sukces (przy `--wait` – build zakończony wynikiem SUCCESS) |
| `1` | Błąd komunikacji lub nieudany build przy `--wait` |
| `2` | Brak wymaganych zmiennych środowiskowych |
| `130` | Przerwanie przez użytkownika (Ctrl+C) |

## Bezpieczeństwo

- **Token API zamiast hasła** – można go unieważnić w dowolnej chwili bez zmiany hasła do konta.
- **Dane logowania tylko ze zmiennych środowiskowych** – nie w kodzie i nie w argumentach, które trafiłyby do historii powłoki i listy procesów.
- **Weryfikacja SSL domyślnie włączona** – flaga `--insecure` istnieje wyłącznie do testów z certyfikatem self-signed.
- **Obsługa CSRF** – token crumb jest pobierany i dołączany automatycznie, gdy Jenkins go wymaga.

## Przygotowanie

Token API: w Jenkinsie kliknij swoją nazwę użytkownika (prawy górny róg) → **Security** → **API Token** → **Add new Token**.

```bash
pip install requests

export JENKINS_URL=https://jenkins.example.com
export JENKINS_USER=jan
export JENKINS_TOKEN=11a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7
```

W Windows PowerShell:

```powershell
$env:JENKINS_URL   = "https://jenkins.example.com"
$env:JENKINS_USER  = "jan"
$env:JENKINS_TOKEN = "11a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7"
```

## Przykłady użycia

Wyniki pochodzą z testu na lokalnej atrapie Jenkins API.

### Lista zadań

```bash
$ python jenkins-manager.py list
api
deploy
frontend/nowy
frontend/web app

Razem: 4
```

### Status ostatnich buildów

```bash
$ python jenkins-manager.py status
api               ✅ #12 SUCCESS (2025-11-09 15:53, 42 s)
deploy            🔄 #3 w trakcie
frontend/nowy     ⚪ brak buildów
frontend/web app  ❌ #7 FAILURE (2025-11-09 15:53, 42 s)
```

### Status jednego zadania w folderze

```bash
$ python jenkins-manager.py status "frontend/web app"
frontend/web app  ❌ #7 FAILURE (2025-11-09 15:53, 42 s)
```

Nazwę zawierającą spację należy wziąć w cudzysłów.

### Uruchomienie zadania

```bash
$ python jenkins-manager.py build api
Zadanie api dodane do kolejki: https://jenkins.example.com/queue/item/5
```

### Uruchomienie z parametrami i oczekiwaniem na wynik

```bash
$ python jenkins-manager.py build api --param ENV=staging --param VERSION=1.2.3 --wait
Zadanie api dodane do kolejki: https://jenkins.example.com/queue/item/5
W kolejce: Waiting for next available executor
Build wystartował: https://jenkins.example.com/job/api/13
Wynik: ✅ SUCCESS (31 s)
```

### Inne opcje

```bash
# Jenkins z certyfikatem self-signed – flaga przed podpoleceniem, tylko do testów
python jenkins-manager.py --insecure status

# Pomoc
python jenkins-manager.py --help
python jenkins-manager.py build --help
```

### Przykłady błędów

```bash
$ python jenkins-manager.py build nie-istnieje
Błąd: Nie znaleziono zasobu (404): https://jenkins.example.com/job/nie-istnieje/build

$ JENKINS_TOKEN=zly python jenkins-manager.py list
Błąd: Nieprawidłowy użytkownik lub token API (401)

$ python jenkins-manager.py build api --param ZLY
Błąd: Parametr musi mieć postać KLUCZ=WARTOŚĆ, otrzymano: 'ZLY'
```

### Użycie w automatyzacji

Przy `--wait` kod wyjścia zależy od wyniku buildu, więc skrypt można łączyć w łańcuchy:

```bash
python jenkins-manager.py build backend-tests --wait && \
python jenkins-manager.py build deploy-staging --param VERSION=1.2.3 --wait
```

Drugie zadanie uruchomi się tylko wtedy, gdy pierwsze zakończy się sukcesem.

## Weryfikacja

Skrypt przetestowano na lokalnej atrapie Jenkins API (serwer HTTP w Pythonie odwzorowujący endpointy Jenkinsa). Sprawdzono:

| Scenariusz | Wynik |
|------------|-------|
| Listowanie z zagnieżdżonym folderem i nazwą ze spacją | ✅ |
| Statusy: sukces, porażka, build w trakcie, brak buildów | ✅ |
| Uruchomienie bez parametrów i z parametrami (parametry dotarły do serwera) | ✅ |
| `--wait` – przejście przez kolejkę do wyniku SUCCESS | ✅ |
| Błędy 401, 403, 404, brak połączenia | ✅ czytelny komunikat, kod 1 |
| Niepoprawny format parametru | ✅ komunikat, kod 1 |
| Brak zmiennych środowiskowych | ✅ komunikat, kod 2 |
