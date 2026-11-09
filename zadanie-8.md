# Zadanie 8: diagnoza błędu Docker – zajęty port 3000

Model poproszono o wyjaśnienie komunikatu błędu zgłoszonego przez Docker Compose przy uruchamianiu usługi `app` oraz o wskazanie sposobów jego rozwiązania.

## Prompt

````
```
ERROR: for app  Cannot start service app: driver failed programming external connectivity on endpoint app (172.18.0.2): Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use
```

Co oznacza ten błąd i jak mogę go rozwiązać?
````

## Komunikat błędu

```
ERROR: for app  Cannot start service app: driver failed programming external connectivity on endpoint app (172.18.0.2): Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use
```

## Wyjaśnienie

Błąd oznacza, że Docker próbuje opublikować port 3000 kontenera `app` na hoście (mapowanie typu `3000:3000` w pliku docker-compose), ale port 3000 na komputerze jest już zajęty przez inny proces. Na jednym porcie hosta może nasłuchiwać tylko jedna aplikacja, dlatego komunikat `bind: address already in use` blokuje start kontenera. Fragment `0.0.0.0:3000` oznacza, że Docker chciał nasłuchiwać na porcie 3000 na wszystkich interfejsach sieciowych hosta, a `172.18.0.2` to wewnętrzny adres kontenera w sieci Dockera.

Najczęstsze przyczyny to inny kontener korzystający z tego samego portu (np. pozostały po poprzednim uruchomieniu lub należący do innego projektu), lokalnie uruchomiony serwer deweloperski (Node.js, React, a także Grafana, która domyślnie używa portu 3000) albo proces, który nie został poprawnie zamknięty po wcześniejszej sesji.

## Sugerowane rozwiązania

### 1. Ustalenie, co zajmuje port

Sprawdzenie, czy port zajmuje inny kontener:

```bash
docker ps --filter "publish=3000"
```

Jeśli kontener zostanie znaleziony, należy go zatrzymać:

```bash
docker stop <id_kontenera>
# lub w katalogu projektu, do którego należy kontener:
docker compose down
```

Jeśli port nie jest zajęty przez kontener, należy znaleźć proces systemowy.

Linux / macOS:

```bash
sudo lsof -i :3000
# albo
sudo ss -ltnp | grep 3000
kill <PID>
```

Windows:

```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

Po zwolnieniu portu usługę uruchamia się ponownie:

```bash
docker compose up
```

### 2. Zmiana portu po stronie hosta

Jeśli usługi zajmującej port 3000 nie należy zamykać, można zmienić mapowanie portów w pliku docker-compose:

```yaml
services:
  app:
    ports:
      - "3001:3000"   # port_hosta:port_kontenera
```

Lewa liczba to port hosta, a prawa to port wewnątrz kontenera. Aplikacja nadal działa w kontenerze na porcie 3000, ale z przeglądarki otwiera się ją pod adresem `http://localhost:3001`.

## Podsumowanie

Błąd nie wynika z wadliwej konfiguracji samej aplikacji, lecz z konfliktu portów na hoście. Rozwiązaniem jest zwolnienie portu 3000 (zatrzymanie kolidującego kontenera lub procesu) albo przypisanie usłudze innego portu hosta w pliku docker-compose.
