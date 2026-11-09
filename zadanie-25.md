# Zadanie 25 – Pipeline Jenkins dla aplikacji Node.js

## Pliki

| Plik | Zawartość |
|------|-----------|
| `Jenkinsfile` | Deklaratywny pipeline: checkout, instalacja zależności, testy, build, budowanie i publikacja obrazu Docker |

## Przebieg pipeline'u

```
Checkout → Install dependencies → Test → Build → Build Docker image → Push Docker image (tylko main)
                                                                                    │
                                                                    post: sprzątanie + komunikat
```

Błąd w dowolnym etapie przerywa pipeline – kolejne etapy się nie wykonują, ale blok `post` zawsze tak.

## Bloki konfiguracyjne

### `agent any`

Pipeline może działać na dowolnym dostępnym agencie (węźle wykonawczym). Jenkins przydziela agentowi katalog roboczy (*workspace*), w którym odbywa się cały build.

### `tools { nodejs 'node-20' }`

Przed pierwszym etapem dodaje do `PATH` wersję Node.js skonfigurowaną w Manage Jenkins → Tools (wtyczka NodeJS pobierze ją, jeśli nie ma jej na agencie). Dzięki temu `npm` zawsze działa w tej samej wersji, niezależnie od tego, co jest zainstalowane w systemie agenta.

### `environment`

Definiuje zmienne dostępne we wszystkich etapach: adres rejestru, nazwę obrazu i ID poświadczeń. Zmiana rejestru wymaga edycji jednej linii. Blok zawiera tylko **identyfikator** poświadczeń, a nie samo hasło.

### `options`

| Opcja | Działanie | Po co |
|-------|-----------|-------|
| `timeout(time: 30, unit: 'MINUTES')` | przerywa build po 30 minutach | zawieszony test nie blokuje agenta na zawsze |
| `buildDiscarder(logRotator(numToKeepStr: '10'))` | przechowuje 10 ostatnich buildów | oszczędność miejsca na kontrolerze |
| `disableConcurrentBuilds()` | jeden build zadania naraz | dwa równoległe buildy nie wypchną `latest` w nieprzewidywalnej kolejności |

## Etapy

### 1. Checkout

`checkout scm` pobiera kod z repozytorium skonfigurowanego w zadaniu, dokładnie w rewizji, która uruchomiła build. Następnie blok `script` odczytuje skrócony hash commita (`git rev-parse --short HEAD`) i tworzy tag obrazu z numeru buildu i hasha, np. `42-a1b2c3d`. Blok `script` jest potrzebny, ponieważ przypisanie wyniku polecenia do zmiennej wymaga Groovy, którego sama składnia deklaratywna nie obsługuje.

### 2. Install dependencies

`npm install` czyta `package.json` i instaluje zależności do `node_modules`. Niepowodzenie (np. niedostępny rejestr npm) od razu kończy build.

### 3. Test

`npm test` uruchamia skrypt `test` z `package.json` (np. Jest, Mocha). Jenkins ocenia wyłącznie **kod wyjścia**: 0 oznacza sukces, każdy inny przerywa pipeline. Testy działają jak bramka jakości – obraz z niedziałającym kodem nigdy nie powstanie.

### 4. Build

`npm run build` uruchamia skrypt `build` – przy TypeScripcie kompiluje kod do JavaScriptu, przy frontendzie tworzy zminifikowane pliki. Wynik (zwykle `dist/`) trafia następnie do obrazu.

### 5. Build Docker image

`docker build` buduje obraz według `Dockerfile` i nadaje mu dwa tagi:

| Tag | Przykład | Rola |
|-----|----------|------|
| numer buildu + hash | `42-a1b2c3d` | niezmienny, jednoznacznie wskazuje build i commit – pozwala precyzyjnie wycofać zmiany |
| `latest` | `latest` | zawsze wskazuje najnowszy obraz |

Użyto podwójnych cudzysłowów (`"""`), bo Groovy ma wstawić wartości zmiennych przed wykonaniem polecenia – nie ma tu sekretów.

### 6. Push Docker image

1. **Warunek** `when { branch 'main' }` – na innych gałęziach etap jest pomijany (oznaczony jako *skipped*). Pull requesty są testowane i budowane, ale nie publikują obrazów. Warunek działa w zadaniu typu Multibranch Pipeline.
2. **`withCredentials`** pobiera login i hasło z magazynu poświadczeń Jenkinsa do zmiennych istniejących tylko wewnątrz bloku i maskowanych w logach jako `****`.
3. **`docker login --password-stdin`** przekazuje hasło przez standardowe wejście, a nie jako argument widoczny w liście procesów.
4. **`docker push`** wysyła oba tagi do rejestru.

Pojedyncze cudzysłowy (`'''`) powodują, że zmienne rozwija powłoka, a nie Groovy – hasło nie zostaje wklejone do treści skryptu ani do logu.

## Blok `post`

| Sekcja | Kiedy | Działanie |
|--------|-------|-----------|
| `always` | zawsze, także po błędzie | wylogowanie z rejestru i usunięcie lokalnych obrazów; `\|\| true` zapobiega błędowi, gdy obrazu nie ma (build padł wcześniej) |
| `success` | po udanym buildzie | komunikat z tagiem obrazu |
| `failure` | po nieudanym buildzie | komunikat o błędzie (w praktyce miejsce na powiadomienie Slack/e-mail) |

Bez sprzątania dysk agenta zapełniłby się obrazami po kilkudziesięciu buildach.

## Wymagania po stronie Jenkinsa

- Docker na agencie; użytkownik `jenkins` w grupie `docker`.
- Wtyczki: Pipeline, NodeJS, Credentials Binding.
- Narzędzie NodeJS o nazwie `node-20` w Manage Jenkins → Tools.
- Poświadczenia typu *Username with password* o ID `docker-registry-creds` (dla Docker Hub – token dostępu zamiast hasła).
- W repozytorium aplikacji: `Dockerfile` oraz skrypty `test` i `build` w `package.json`.

## Najlepsze praktyki tworzenia pipeline'ów Jenkins

### Pipeline jako kod

- **Jenkinsfile w repozytorium** razem z aplikacją, a nie w konfiguracji zadania w interfejsie – ma historię zmian, przechodzi code review, a każda gałąź może mieć własną wersję.
- **Składnia deklaratywna** zamiast skryptowej – czytelniejsza, walidowana przed uruchomieniem, wymusza spójną strukturę.
- **Minimum logiki w Groovy** – bloki `script` ograniczać do koniecznych przypadków, większą logikę przenosić do skryptów w repozytorium lub do **Shared Libraries** współdzielonych przez wiele projektów.

### Powtarzalne i bezpieczne środowisko

- **Etapy w kontenerach**, np. `agent { docker { image 'node:20-alpine' } }` – identyczne środowisko w każdym buildzie, agent nie potrzebuje zainstalowanego Node.js.
- **Nie budować na kontrolerze** – kod z repozytorium wykonany na kontrolerze ma dostęp do wszystkich sekretów i konfiguracji Jenkinsa.
- **`npm ci` zamiast `npm install`** – instaluje dokładnie wersje z `package-lock.json`, przerywa build przy niezgodności, jest szybsze. Cache katalogu npm między buildami.

### Sekrety

- Wyłącznie w magazynie poświadczeń Jenkinsa, pobierane przez `withCredentials` w możliwie wąskim zakresie.
- Nigdy w treści Jenkinsfile ani w `echo`.
- Tokeny z ograniczonymi uprawnieniami zamiast haseł do kont.

### Szybka informacja zwrotna i jakość

- **Fail fast** – najtańsze i najszybsze kontrole (lint, testy jednostkowe) na początku.
- **`parallel`** dla niezależnych etapów (np. lint i testy jednocześnie).
- **Publikacja wyników testów** krokiem `junit 'reports/*.xml'` – trendy i lista nieudanych testów zamiast samego czerwonego etapu.
- **Skanowanie bezpieczeństwa** przed publikacją: obrazu (Trivy) i zależności (`npm audit`).

### Artefakty i wdrożenia

- **Niezmienne, identyfikowalne tagi** – wdrażać po tagu z numerem buildu/hashem, nie po `latest`, który nie mówi, co faktycznie działa w produkcji.
- **Build once, deploy many** – ten sam obraz przechodzi przez kolejne środowiska bez przebudowywania.
- **Ręczne zatwierdzenie** (`input`) przed wdrożeniem produkcyjnym.

### Higiena

- Zawsze `timeout`, rotacja buildów i sprzątanie w `post { always }`.
- Powiadomienia o wyniku (Slack, e-mail) w `post`.
- Walidacja Jenkinsfile przed commitem:

  ```bash
  curl -X POST -F "jenkinsfile=<Jenkinsfile" "$JENKINS_URL/pipeline-model-converter/validate"
  ```

  lub testowanie zmian funkcją **Replay** w interfejsie Jenkinsa.

## Możliwe usprawnienia tego Jenkinsfile

| Usprawnienie | Zmiana |
|--------------|--------|
| Powtarzalne zależności | `npm ci` zamiast `npm install` |
| Środowisko w kontenerze | `agent { docker { image 'node:20-alpine' } }` dla etapów npm |
| Raporty testów | `junit` w `post` etapu Test |
| Bezpieczeństwo | etap `npm audit` i skan obrazu Trivy przed publikacją |
| Szybkość | `parallel` dla lintu i testów |
| Powiadomienia | Slack/e-mail w `post { failure }` |
