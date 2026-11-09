# Zadanie 14 – analiza logów Dockera

## Logi

```
May 19 10:15:32 server dockerd[1234]: time="2025-05-19T10:15:32.123456789Z" level=info msg="Container 78a2b3c4 health status changed from starting to healthy"
May 19 10:16:45 server dockerd[1234]: time="2025-05-19T10:16:45.987654321Z" level=info msg="Container 78a2b3c4 failed to connect to 172.17.0.3:5432: connection refused"
May 19 10:16:47 server dockerd[1234]: time="2025-05-19T10:16:47.246813579Z" level=warning msg="Container 78a2b3c4 health status changed from healthy to unhealthy"
```

## Co się dzieje

O 10:15:32 kontener `78a2b3c4` kończy fazę startową i healthcheck zgłasza stan `healthy`, czyli aplikacja początkowo działa poprawnie. Po około 73 sekundach (10:16:45) pojawia się nieudana próba połączenia z `172.17.0.3:5432`, a dwie sekundy później Docker oznacza kontener jako `unhealthy`. Kontener nadal działa, ale przestał spełniać warunek zdrowia, który najpewniej zależy od dostępu do bazy danych.

## Zidentyfikowane problemy

**Niedostępność bazy PostgreSQL.** Port 5432 to domyślny port PostgreSQL. Komunikat `connection refused` oznacza, że host jest osiągalny, ale nic nie nasłuchuje na tym porcie (to nie timeout ani blokada firewalla). Baza mogła się zatrzymać lub zrestartować (np. przez OOM), nie zdążyła się uruchomić albo nasłuchuje tylko na `localhost`. Skoro na starcie wszystko działało, najbardziej prawdopodobny jest upadek lub restart kontenera bazy.

**Połączenie po stałym adresie IP.** Adres `172.17.0.x` pochodzi z domyślnej sieci `bridge`. Po restarcie kontener bazy może otrzymać inny adres, a aplikacja nadal będzie łączyć się ze starym.

**Zbyt wrażliwy healthcheck.** Zmiana na `unhealthy` dwie sekundy po pierwszym błędzie sugeruje bardzo niski próg `retries`. Chwilowe zakłócenie bazy od razu oznacza całą aplikację jako niesprawną.

**Brak automatycznej reakcji.** Samodzielny Docker (bez Swarma lub narzędzia typu autoheal) jedynie zmienia status na `unhealthy`, nie restartuje kontenera. W logach nie widać też ponawiania połączeń przez aplikację.

**Ograniczona widoczność.** Błąd połączenia jest logowany przez `dockerd` (wynik polecenia healthchecka), a nie przez samą aplikację. Pełnej przyczyny trzeba szukać w logach kontenerów.

## Diagnostyka

```bash
docker ps -a                                   # czy baza działa, liczba restartów
docker logs <kontener_db>                      # przyczyna zatrzymania bazy
docker inspect <kontener_db> \
  --format '{{.State.OOMKilled}} {{.NetworkSettings.IPAddress}}'
docker exec 78a2b3c4 nc -zv 172.17.0.3 5432    # test portu z kontenera aplikacji
docker inspect 78a2b3c4 --format '{{json .State.Health}}'
```

## Rekomendowane rozwiązanie

Przenieść usługi do własnej sieci (docker-compose), łączyć się po nazwie usługi zamiast po IP, uzależnić start aplikacji od zdrowia bazy i złagodzić healthcheck.

```yaml
services:
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    image: moja-aplikacja
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/postgres
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
```

Dodatkowo aplikacja powinna ponawiać połączenia z bazą (retry z backoffem) i logować błędy połączenia we własnych logach.
