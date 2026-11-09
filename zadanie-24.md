# Zadanie 24 – Analiza metryk wydajnościowych serwera API

## Dane wejściowe (ostatnie 24h)

| Metryka | Wartość |
|---------|---------|
| Średni czas odpowiedzi | 230 ms |
| 95. percentyl czasu odpowiedzi (p95) | 450 ms |
| 99. percentyl czasu odpowiedzi (p99) | 1200 ms |
| Liczba zapytań | 15 000 |
| Liczba błędów 5xx | 120 |
| Użycie CPU | średnio 45%, maksymalnie 80% |
| Użycie pamięci | średnio 2,1 GB, maksymalnie 3,5 GB (z 4 GB dostępnych) |

## Wskaźniki pochodne

| Wskaźnik | Obliczenie | Wynik | Ocena |
|----------|------------|-------|-------|
| Średni ruch | 15 000 / 24 h | ~625 zapytań/h ≈ **0,17 zapytania/s** | bardzo mały |
| Odsetek błędów 5xx | 120 / 15 000 | **0,8%** (co ~125. zapytanie) | 🔴 ok. 8× powyżej typowego SLO (< 0,1%) |
| Stosunek p99 / p95 | 1200 / 450 | **2,7×** | 🔴 długi ogon |
| Stosunek p99 / średnia | 1200 / 230 | **5,2×** | 🔴 długi ogon |
| Zapytania wolniejsze niż p99 | 1% × 15 000 | **~150 dziennie** powyżej 1,2 s | 🟠 |
| Szczytowe zużycie pamięci | 3,5 / 4 GB | **87,5%** | 🔴 mały zapas |
| Skok pamięci | 3,5 − 2,1 GB | **~1,4 GB** | 🟠 podejrzanie duży |
| CPU w szczycie | — | **80%** przy < 1 zapytaniu/s | 🟠 nieproporcjonalne do ruchu |

## Interpretacja

**Podsumowanie:** typowe zapytanie działa przyzwoicie, ale serwer ma trzy realne problemy – za dużo błędów, długi ogon wolnych odpowiedzi i bardzo mały zapas pamięci. Obciążenie zasobów jest przy tym nieproporcjonalnie wysokie w stosunku do ruchu.

### Ruch jest bardzo mały

Mniej niż 0,2 zapytania na sekundę to kontekst dla wszystkich pozostałych metryk. Przy takim ruchu serwer z 4 GB pamięci nie powinien zbliżać się do limitów. Jeśli się zbliża, przyczyną nie jest skala, lecz sposób działania aplikacji.

### Odsetek błędów jest za wysoki

0,8% zapytań kończy się błędem serwera. Typowe cele SLO dla API to poniżej 0,1%, więc wynik jest ok. ośmiokrotnie gorszy. To **najważniejszy problem**, ponieważ błędy 5xx bezpośrednio dotykają użytkowników.

### Czasy odpowiedzi mają długi ogon

Średnia (230 ms) i p95 (450 ms) są akceptowalne dla większości API. Niepokoi p99 (1200 ms) – 2,7 razy wyższe niż p95. Oznacza to istnienie osobnej grupy bardzo wolnych żądań, a nie równomierne spowolnienie. Średnia ukrywa ten problem, dlatego p99 jest tu kluczową metryką. Typowe przyczyny:

- wolne zapytania do bazy (brak indeksu, problem N+1, pobieranie dużych zbiorów bez stronicowania),
- wywołania zewnętrznych usług bez timeoutu,
- pauzy garbage collectora przy wysokim zużyciu pamięci,
- oczekiwanie na wolne połączenie w puli połączeń do bazy.

### Pamięć jest na granicy

Szczyt 3,5 GB z 4 GB to 87,5% zajętości, a skok o ~1,4 GB ponad średnią przy tak małym ruchu sugeruje:

- wyciek pamięci,
- jednorazowe wczytywanie dużych danych (eksport, raport, zapytanie bez limitu),
- cache bez ograniczenia rozmiaru.

Kolejny podobny skok może skończyć się zabiciem procesu przez OOM killer lub limit kontenera, co daje błędy 502/503.

### Szczyty CPU są podejrzane

45% średnio i 80% w szczycie to dużo jak na mniej niż jedno zapytanie na sekundę. Wskazuje to na kosztowne operacje: zadania w tle (cron, raporty), intensywną pracę garbage collectora przy zapełnionej pamięci, kosztowne obliczenia (serializacja dużych odpowiedzi, hashowanie, wyrażenia regularne) albo krótkie skoki ruchu niewidoczne w średniej dobowej.

## Hipoteza robocza

Objawy prawdopodobnie mają **wspólną przyczynę**:

```
kosztowna operacja (zadanie w tle / zapytanie zwracające duży zbiór danych)
        │
        ▼
pamięć rośnie do ~3,5 GB
        │
        ▼
garbage collector intensywnie pracuje → CPU do 80%
        │
        ├──► zapytania obsługiwane w tym czasie trafiają do p99 (> 1,2 s)
        │
        └──► część kończy się timeoutem lub restartem procesu → błędy 5xx
```

Hipotezę można potwierdzić tylko na wykresach w czasie – dane dobowe uśredniają wszystko w jedną liczbę i nie pokazują korelacji.

## Rekomendacje

### Etap 1 – diagnoza (bez zmian w kodzie)

| Działanie | Cel |
|-----------|-----|
| Nałożenie wykresów p99, liczby 5xx, CPU i pamięci na jedną oś czasu | Sprawdzenie, czy szczyty występują jednocześnie i czy pokrywają się np. z harmonogramem zadań cron |
| Rozbicie błędów 5xx na kody i endpointy | `500` – wyjątek w kodzie; `502`/`503` – restart lub przeciążenie procesu; `504` – timeout zależności |
| Sprawdzenie logów systemowych i restartów kontenera | Wykrycie zabić przez OOM (`dmesg`, `docker inspect` → `OOMKilled`) |
| Włączenie logu wolnych zapytań w bazie danych | Identyfikacja zapytań odpowiedzialnych za p99 |
| Wdrożenie tracingu (OpenTelemetry, APM) | Ustalenie, w której warstwie mija czas wolnych żądań |

### Etap 2 – poprawki (zależnie od wyników diagnozy)

| Obszar | Działania |
|--------|-----------|
| Baza danych | indeksy, eliminacja N+1, stronicowanie, pobieranie tylko potrzebnych pól, odpowiedni rozmiar puli połączeń |
| Pamięć | porównanie heap snapshotów sprzed i z czasu skoku, przetwarzanie strumieniowe zamiast wczytywania całości, cache z limitem (LRU) |
| Zależności zewnętrzne | timeouty, retry z wykładniczym backoffem, circuit breaker |
| Zadania w tle | przeniesienie do osobnego workera lub kolejki, aby nie konkurowały z obsługą zapytań |
| Cache | przechowywanie często odczytywanych, rzadko zmienianych danych, np. w Redisie |

### Etap 3 – zabezpieczenia

| Działanie | Szczegóły |
|-----------|-----------|
| Alerty | p99 > 1 s, odsetek 5xx > 0,5%, pamięć > 80% – wykrycie problemu, zanim zauważą go użytkownicy |
| Limit sterty procesu | ustawienie wyraźnie poniżej limitu kontenera (w Node.js `--max-old-space-size`), aby aplikacja nie była zabijana bez ostrzeżenia |
| Skalowanie | dodatkowa pamięć lub skalowanie poziome tylko doraźnie – przy 0,17 zapytania/s to leczenie objawów, nie przyczyny |

## Wnioski

1. Najpilniejszy problem to **0,8% błędów 5xx** – ośmiokrotnie powyżej typowego celu.
2. **p99 = 1,2 s** przy p95 = 450 ms wskazuje na wąską grupę bardzo wolnych żądań, której nie widać w średniej.
3. **87,5% zajętości pamięci** w szczycie grozi restartami procesu i może być bezpośrednią przyczyną części błędów.
4. Wysokie zużycie zasobów przy bardzo małym ruchu oznacza, że **źródło problemu leży w aplikacji**, a nie w niewystarczającej infrastrukturze – dokładanie zasobów nie rozwiąże go trwale.
5. Dane zagregowane z 24 godzin nie wystarczą do postawienia diagnozy – potrzebne są szeregi czasowe i rozbicie metryk według endpointów.
