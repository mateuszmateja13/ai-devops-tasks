# Zadanie 26 – Znajdowanie i poprawianie błędów w Jenkinsfile

## Pliki

| Plik | Zawartość |
|------|-----------|
| `Jenkinsfile-with-errors` | Oryginalny pipeline z błędami |
| `Jenkinsfile-fixed` | Poprawiona wersja |

## Lista znalezionych problemów

| # | Problem | Miejsce | Waga | Skutek |
|---|---------|---------|------|--------|
| 1 | Literówka `stesp` zamiast `steps` | etap Build | 🔴 błąd krytyczny | Jenkins odrzuca cały plik, nie wykonuje się żaden etap |
| 2 | `npm build` zamiast `npm run build` | etap Build | 🔴 błąd | skrypt `build` z `package.json` się nie wykonuje |
| 3 | Push obrazu bez rejestru/konta i bez logowania | etap Deploy | 🔴 błąd | `docker push` kończy się odmową dostępu |
| 4 | Build przed testami | kolejność etapów | 🟠 logika | czas tracony na build kodu, który nie przejdzie testów |
| 5 | Blok `when` po `steps` | etap Deploy | 🟡 konwencja | warunek wykonania etapu ukryty na jego końcu |
| 6 | Gałąź `master` | etap Deploy | 🟠 do sprawdzenia | przy repozytorium z gałęzią `main` etap jest zawsze cicho pomijany |
| 7 | Myląca nazwa etapu Deploy | etap Deploy | 🟡 czytelność | etap niczego nie wdraża, tylko buduje i publikuje obraz |
| 8 | Wyłącznie tag `latest` | etap Deploy | 🟠 dobra praktyka | brak możliwości identyfikacji wersji i wycofania zmian |
| 9 | `npm install` zamiast `npm ci` | etap Build | 🟡 dobra praktyka | buildy niepowtarzalne – wersje zależności mogą się zmieniać |
| 10 | Brak `timeout`, rotacji buildów i sprzątania | cały pipeline | 🟡 dobra praktyka | zawieszony build blokuje agenta, obrazy zapełniają dysk |

## Błędy uniemożliwiające działanie

### 1. Literówka `stesp`

```groovy
stage('Build') {
    stesp {          // ❌
```

Składnia deklaratywna jest walidowana **przed** uruchomieniem. Nieznana sekcja `stesp` powoduje błąd kompilacji (`Unknown stage section "stesp"`) i odrzucenie całego pliku – nie wykonują się nawet poprawne etapy Test i Deploy.

**Poprawka:** `steps`.

### 2. `npm build` zamiast `npm run build`

Własne skrypty z sekcji `scripts` w `package.json` uruchamia się przez `npm run <nazwa>`. Skróty bez `run` istnieją tylko dla kilku wbudowanych poleceń (`test`, `start`, `stop`, `restart`). `npm build` było wewnętrznym poleceniem npm, które **nie uruchamia** skryptu `build`, a w nowszych wersjach npm zostało usunięte. Zależnie od wersji polecenie kończy się błędem albo przechodzi bez zbudowania aplikacji – drugi przypadek jest groźniejszy, bo do obrazu trafia niezbudowany kod i nikt tego nie zauważa.

**Poprawka:** `npm run build`.

### 3. `docker push myapp:latest` bez rejestru i logowania

Nazwa obrazu bez prefiksu jest rozwijana do `docker.io/library/myapp` – przestrzeni oficjalnych obrazów Docker Hub, do której zwykły użytkownik nie ma prawa zapisu. Dodatkowo w pipeline nie ma `docker login`. Wynik: `denied: requested access to the resource is denied`.

**Poprawka:**
- pełna nazwa obrazu z rejestrem i kontem w zmiennej `IMAGE_NAME = 'docker.io/mojafirma/myapp'`,
- logowanie przez `withCredentials` z poświadczeniami zapisanymi w Jenkinsie,
- przekazanie hasła przez `--password-stdin` w bloku `'''` (zmienne rozwija powłoka, a nie Groovy, więc hasło nie trafia do logu ani listy procesów).

## Problemy logiczne i dobre praktyki

### 4. Kolejność etapów

Oryginał: **Build → Test → Deploy**. Testy powinny być bramką jakości, więc kolejność została zmieniona na **Install → Test → Build → Build Docker image → Push Docker image**. Przy niezdanych testach pipeline kończy się przed buildem.

### 5. Położenie bloku `when`

Umieszczenie `when` po `steps` nie jest błędem składni, ale wbrew konwencji. Warunek przeniesiono na początek etapu, aby od razu było widać, kiedy etap się wykonuje.

### 6. Gałąź `master`

Większość nowych repozytoriów używa gałęzi `main`. Przy niezgodności nazw etap publikacji jest **zawsze pomijany bez żadnego błędu** – pipeline świeci na zielono, a obraz nigdy nie trafia do rejestru. W poprawionej wersji użyto `main`; jeśli repozytorium faktycznie używa `master`, należy go zostawić. Warunek `branch` działa wyłącznie w zadaniu typu Multibranch Pipeline.

### 7. Nazwa etapu Deploy

Etap budował i publikował obraz, ale niczego nie wdrażał. Rozdzielono go na **Build Docker image** (wykonywany na każdej gałęzi – sprawdza, czy `Dockerfile` się buduje) i **Push Docker image** (tylko na `main`).

### 8. Tagowanie obrazu

Sam tag `latest` nie mówi, która wersja kodu jest w obrazie, i uniemożliwia wycofanie zmian. Dodano niezmienny tag `<numer buildu>-<hash commita>`, np. `42-a1b2c3d`, publikowany razem z `latest`.

### 9. `npm ci`

`npm ci` instaluje dokładnie wersje z `package-lock.json`, przerywa build przy niezgodności locka z `package.json` i działa szybciej niż `npm install` – buildy są powtarzalne.

### 10. Higiena pipeline'u

- `timeout(time: 30, unit: 'MINUTES')` – zawieszony build nie blokuje agenta.
- `buildDiscarder(logRotator(numToKeepStr: '10'))` – przechowywanie 10 ostatnich buildów.
- `post { always { ... } }` – wylogowanie z rejestru i usunięcie lokalnych obrazów po każdym buildzie, także nieudanym (`|| true` zapobiega błędowi, gdy obrazu nie ma).

## Porównanie struktury

| Oryginał | Poprawiona wersja |
|----------|-------------------|
| Build (`npm install`, `npm build`) | Install (`npm ci`) |
| Test (`npm test`) | Test (`npm test`) |
| — | Build (`npm run build`) |
| Deploy (`docker build`, `docker push`, `when` na końcu) | Build Docker image (dwa tagi) |
| — | Push Docker image (`when` na początku, logowanie przez poświadczenia) |
| — | `environment`, `options`, `post` |

## Uwagi

- Nazwę obrazu (`mojafirma/myapp`), ID poświadczeń (`docker-registry-creds`) i nazwę gałęzi należy dopasować do własnego środowiska.
- Pliki nie zostały uruchomione w Jenkinsie. Przed użyciem warto zwalidować składnię:

  ```bash
  curl -X POST -F "jenkinsfile=<Jenkinsfile-fixed" "$JENKINS_URL/pipeline-model-converter/validate"
  ```

## Wnioski

Najgroźniejsze okazały się błędy, które nie dają wyraźnego sygnału: `npm build` w niektórych wersjach npm przechodzi bez zbudowania aplikacji, a niezgodna nazwa gałęzi powoduje ciche pomijanie publikacji. Literówka `stesp` jest łatwa do wykrycia, bo Jenkins od razu odrzuca plik. Walidacja Jenkinsfile przed commitem i świadome sprawdzanie, czy każdy etap faktycznie robi to, co sugeruje jego nazwa, pozwalają wychwycić oba rodzaje problemów.
