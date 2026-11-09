# Zadanie 9: weryfikacja poprawności pliku docker-compose

Model poproszono o sprawdzenie, czy podany plik konfiguracyjny Docker Compose jest poprawny, oraz o wskazanie błędów i przygotowanie poprawionej wersji.

## Prompt

````
```yaml
services:
  web:
    image: nginx
    ports:
      - "80:80"
  app:
    build: .
    ports
      - "3000:3000"
    depends_on:
      - db
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD=password
```

Czy ten skrypt jest poprawny ?
````

## Oryginalny plik

```yaml
services:
  web:
    image: nginx
    ports:
      - "80:80"
  app:
    build: .
    ports
      - "3000:3000"
    depends_on:
      - db
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD=password
```

## Znalezione błędy

Plik nie jest poprawny. Docker Compose odrzuci go już na etapie parsowania YAML z powodu dwóch błędów składniowych.

### 1. Brak dwukropka po kluczu `ports` w usłudze `app`

```yaml
    ports
      - "3000:3000"
```

Bez dwukropka `ports` nie jest kluczem mapy, tylko zwykłym ciągiem znaków. Parser nie może więc powiązać z nim listy w kolejnej linii. Poprawny zapis to `ports:`.

### 2. Niepoprawny format zmiennej środowiskowej w usłudze `db`

```yaml
    environment:
      POSTGRES_PASSWORD=password
```

Sekcja `environment` przyjmuje mapę albo listę. Zapis `POSTGRES_PASSWORD=password` bez myślnika i bez dwukropka nie jest żadną z tych form. Dopuszczalne są dwa warianty:

```yaml
    environment:
      POSTGRES_PASSWORD: password      # mapa
```

```yaml
    environment:
      - POSTGRES_PASSWORD=password     # lista
```

## Poprawiona wersja

```yaml
services:
  web:
    image: nginx
    ports:
      - "80:80"
  app:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: password
```

Poprawność pliku można zweryfikować poleceniem:

```bash
docker compose config
```

## Dodatkowe uwagi (dobre praktyki)

Poniższe kwestie nie są błędami składni, ale warto je uwzględnić w konfiguracji docelowej.

`depends_on` w podstawowej formie zapewnia jedynie kolejność uruchamiania kontenerów. Nie czeka na gotowość bazy do przyjmowania połączeń. Do tego służy `healthcheck` w usłudze `db` połączony z `condition: service_healthy` w `depends_on`.

Baza danych nie ma przypisanego wolumenu, więc dane zostaną utracone po usunięciu kontenera.

Hasło zapisane jawnie w pliku powinno zostać przeniesione do pliku `.env` lub do mechanizmu sekretów.

Przykład uwzględniający te uwagi:

```yaml
services:
  web:
    image: nginx
    ports:
      - "80:80"
  app:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  db-data:
```

## Podsumowanie

Oryginalny plik zawiera dwa błędy składniowe: brak dwukropka po `ports` w usłudze `app` oraz niepoprawny zapis zmiennej `POSTGRES_PASSWORD` w usłudze `db`. Po ich poprawieniu plik jest prawidłową konfiguracją Docker Compose.
