# Zadanie 10: plik .gitignore dla projektu Node.js z Dockerem i MongoDB

Model poproszono o przygotowanie pliku `.gitignore` dla projektu Node.js, który jest uruchamiany w kontenerach Docker i przechowuje dane w lokalnej bazie MongoDB.

## Prompt

```
Stwórz plik .gitignore dla projektu Node.js, który używa Docker i przechowuje dane w lokalnej bazie MongoDB.
```

## Plik .gitignore

```gitignore
# =========================================================
# Node.js
# =========================================================

# Zależności instalowane przez npm / yarn / pnpm
node_modules/
jspm_packages/

# Katalogi i pliki generowane podczas budowania
dist/
build/
out/
.next/
.nuxt/
*.tsbuildinfo

# Cache narzędzi
.npm/
.yarn/cache/
.yarn/install-state.gz
.pnpm-store/
.eslintcache
.cache/
.parcel-cache/

# Raporty testów i pokrycia kodu
coverage/
.nyc_output/
junit.xml

# Logi
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# =========================================================
# Zmienne środowiskowe i sekrety
# =========================================================

# Pliki .env zawierają hasła, connection stringi do MongoDB i klucze API
.env
.env.*
# Szablon bez sekretów powinien trafić do repozytorium
!.env.example

# Klucze i certyfikaty
*.pem
*.key
*.crt

# =========================================================
# Docker
# =========================================================

# Lokalne nadpisania konfiguracji Compose (ustawienia konkretnego dewelopera)
docker-compose.override.yml
compose.override.yml

# Katalogi montowane jako wolumeny (bind mounts) z danymi kontenerów
docker-data/
.docker/

# =========================================================
# MongoDB (lokalna baza danych)
# =========================================================

# Pliki danych bazy, gdy katalog /data/db jest zamontowany lokalnie
data/
mongo-data/
mongodb-data/
db-data/

# Kopie zapasowe tworzone przez mongodump i eksporty
dump/
backup/
*.bson
*.archive
*.gz

# Logi serwera mongod
mongod.log
mongo*.log

# =========================================================
# System operacyjny i edytory
# =========================================================

.DS_Store
Thumbs.db
desktop.ini

.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
.idea/
*.swp
*.swo
*~
```

## Omówienie sekcji

**Node.js.** Katalog `node_modules/` jest najważniejszą pozycją pliku. Zawiera tysiące plików zależności, które odtwarza się poleceniem `npm ci` na podstawie `package.json` i `package-lock.json`. Plik `package-lock.json` celowo nie jest ignorowany, ponieważ gwarantuje identyczne wersje pakietów lokalnie i w obrazie Docker. Ignorowane są także artefakty budowania (`dist/`, `build/`), cache narzędzi i raporty testów.

**Zmienne środowiskowe.** Pliki `.env` przechowują connection string do bazy (np. `MONGO_URI=mongodb://user:haslo@localhost:27017/app`) i nie mogą trafić do repozytorium. Wzorzec `!.env.example` wyłącza z ignorowania szablon, który pokazuje innym członkom zespołu, jakie zmienne należy ustawić.

**Docker.** Pliki `Dockerfile` i `docker-compose.yml` są częścią projektu, dlatego nie są ignorowane. Ignorowany jest tylko `docker-compose.override.yml`, który Compose wczytuje automatycznie i który zwykle zawiera lokalne ustawienia konkretnej osoby (porty, ścieżki).

**MongoDB.** Jeśli w `docker-compose.yml` dane bazy są montowane do katalogu projektu, np.:

```yaml
services:
  mongo:
    image: mongo:7
    volumes:
      - ./mongo-data:/data/db
```

to w katalogu `mongo-data/` pojawiają się binarne pliki silnika WiredTiger. Są one duże, zmieniają się przy każdym zapisie i nie nadają się do wersjonowania. Ignorowane są również zrzuty z `mongodump` (`dump/`, `*.bson`, `*.archive`).

## Uwagi

Plik `.gitignore` nie wpływa na to, co trafia do obrazu Docker. Do tego służy osobny plik `.dockerignore`, który powinien zawierać co najmniej `node_modules`, `.env`, `.git` oraz katalog z danymi MongoDB. Bez niego lokalne `node_modules` i dane bazy zostaną skopiowane do kontekstu budowania, co wydłuża budowanie obrazu i może nadpisać zależności zainstalowane w kontenerze.

Lepszym rozwiązaniem niż bind mount jest nazwany wolumen Dockera (`mongo-data:/data/db` z sekcją `volumes:` na końcu pliku Compose). Dane są wtedy przechowywane poza katalogiem projektu, więc problem ich przypadkowego commitowania w ogóle nie występuje.

Wzorzec `data/` jest szeroki. Jeśli projekt zawiera katalog `data/` z plikami, które mają być wersjonowane (np. dane startowe do seedowania bazy), należy tę pozycję usunąć i zostawić tylko `mongo-data/`.

Poprawność pliku można sprawdzić poleceniem:

```bash
git check-ignore -v node_modules/express .env mongo-data/WiredTiger
```

## Podsumowanie

Przygotowany `.gitignore` wyklucza z repozytorium zależności Node.js, artefakty budowania, logi, pliki z sekretami, lokalne nadpisania konfiguracji Docker Compose oraz pliki danych i zrzuty lokalnej bazy MongoDB, pozostawiając w repozytorium wszystkie pliki potrzebne do odtworzenia środowiska (`package-lock.json`, `Dockerfile`, `docker-compose.yml`, `.env.example`).
