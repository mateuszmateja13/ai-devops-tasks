# Zadanie 29 – Jenkins Configuration as Code (JCasC)

## Pliki

| Plik | Zawartość |
|------|-----------|
| `jenkins-casc.yaml` | Szablon JCasC: ustawienia podstawowe, bezpieczeństwo, katalog narzędzi, poświadczenia, ustawienia wtyczek i przykładowe zadania pipeline |

## Zawartość szablonu

| Sekcja | Co konfiguruje |
|--------|----------------|
| `jenkins` | liczba wykonawców (2), tryb `EXCLUSIVE`, `quietPeriod`, ponowienia checkoutu, lokalne konto admina, autoryzacja, ochrona CSRF, zmienne globalne |
| `tool` | JDK 17, Maven 3.9, Node.js 20, klient Docker, Git – z automatyczną instalacją przy pierwszym użyciu |
| `credentials` | poświadczenia do rejestru Docker i GitHuba (wartości ze zmiennych środowiskowych) |
| `unclassified` | adres Jenkinsa, globalna rotacja buildów, znaczniki czasu w logach |
| `jobs` | dwa pipeline'y przez Job DSL: `simple-task-api` (Jenkinsfile z repozytorium) i `hello-pipeline` (kod inline, sprawdza wersje narzędzi) |
| komentarz na początku pliku | lista 13 podstawowych wtyczek do zainstalowania |

## Jak działa JCasC

Wtyczka **Configuration as Code** przy starcie Jenkinsa czyta plik YAML wskazany zmienną `CASC_JENKINS_CONFIG` i ustawia według niego całą konfigurację – bezpieczeństwo, narzędzia, poświadczenia, ustawienia wtyczek. Sekcję `jobs` przekazuje wtyczce **Job DSL**, która tworzy zadania.

Wyrażenia `${NAZWA}` są podstawiane wartościami zmiennych środowiskowych, więc **sekrety nie trafiają do pliku** i można go bezpiecznie trzymać w repozytorium.

**JCasC nie instaluje wtyczek** – tylko je konfiguruje. Wtyczki muszą być zainstalowane, zanim Jenkins wystartuje, dlatego instaluje się je przy budowaniu obrazu.

```
plugins.txt ──► jenkins-plugin-cli (build obrazu) ──► wtyczki w obrazie
                                                           │
jenkins-casc.yaml + .env (sekrety) ──► start Jenkinsa ──► JCasC ──► konfiguracja + zadania (Job DSL)
```

## Instalacja i uruchomienie (Docker)

### Wymagania

- Docker z Docker Compose (w Windows i macOS – Docker Desktop)
- ok. 2 GB wolnej pamięci RAM

### Krok 1. Struktura katalogu

```
jenkins/
├── Dockerfile
├── docker-compose.yml
├── plugins.txt
├── .env              ← sekrety, NIE commitować
└── jenkins-casc.yaml
```

### Krok 2. Lista wtyczek – `plugins.txt`

Ta sama lista co w komentarzu na początku `jenkins-casc.yaml`:

```
configuration-as-code
workflow-aggregator
job-dsl
git
github
credentials-binding
nodejs
docker-workflow
pipeline-maven
timestamper
ws-cleanup
build-timeout
matrix-auth
```

Bez numerów wersji instalowane są najnowsze. W produkcji warto je przypiąć (np. `git:5.5.2`), aby każdy build obrazu dawał ten sam wynik.

### Krok 3. `Dockerfile`

```dockerfile
FROM jenkins/jenkins:lts-jdk17

# Wyłączenie kreatora pierwszego uruchomienia – konfigurację dostarcza JCasC
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Instalacja wtyczek podczas budowania obrazu
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Plik JCasC i wskazanie go wtyczce
COPY --chown=jenkins:jenkins jenkins-casc.yaml /var/jenkins_home/casc/jenkins-casc.yaml
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc/jenkins-casc.yaml
```

### Krok 4. Sekrety – `.env`

Docker Compose wczytuje ten plik automatycznie i przekazuje zmienne do kontenera.

```env
JENKINS_ADMIN_PASSWORD=zmien-na-silne-haslo
DOCKER_REGISTRY_USER=twoj-login
DOCKER_REGISTRY_TOKEN=token-z-docker-hub
GITHUB_USER=twoj-login-github
GITHUB_TOKEN=ghp_token-z-github
```

- Plik `.env` należy dopisać do `.gitignore`.
- Wszystkie zmienne muszą istnieć – bez nich JCasC zgłosi błąd przy starcie. Jeśli rejestr lub GitHub nie są używane, wystarczą dowolne wartości.

### Krok 5. `docker-compose.yml`

```yaml
services:
  jenkins:
    build: .
    container_name: jenkins
    ports:
      - "8080:8080"     # interfejs WWW
      - "50000:50000"   # połączenia agentów
    env_file: .env
    volumes:
      - jenkins_home:/var/jenkins_home
    restart: unless-stopped

volumes:
  jenkins_home:
```

### Krok 6. Dopasowanie szablonu do środowiska

W `jenkins-casc.yaml`:

| Miejsce | Zmiana |
|---------|--------|
| `unclassified.location.url` | `http://localhost:8080/` przy uruchomieniu lokalnym |
| zadanie `simple-task-api` → `url(...)` | adres rzeczywistego repozytorium (w przeciwnym razie build zakończy się błędem checkoutu) |
| sekcja `tool` | wersje narzędzi zgodne z potrzebami projektu |

### Krok 7. Budowanie i uruchomienie

```bash
docker compose up -d --build
docker compose logs -f jenkins
```

Pierwsze budowanie trwa kilka minut (pobieranie wtyczek). Start jest udany, gdy w logach pojawi się `Jenkins is fully up and running`. Błędy JCasC są zgłaszane jako `ConfiguratorException`.

### Krok 8. Weryfikacja

Otwórz `http://localhost:8080` i zaloguj się jako `admin` z hasłem z `.env`. Kreator instalacji nie powinien się pojawić.

| Gdzie | Oczekiwany wynik |
|-------|------------------|
| Strona główna | komunikat systemowy z szablonu, zadania `simple-task-api` i `hello-pipeline` |
| Manage Jenkins → Tools | JDK, Maven, Node.js, Docker, Git |
| Manage Jenkins → Credentials | `docker-registry-creds`, `github-creds` |
| Manage Jenkins → Configuration as Code | ścieżka do `jenkins-casc.yaml` |
| Build `hello-pipeline` | w logu wersje Node.js, npm i Mavena (pierwszy build pobiera narzędzia, więc trwa dłużej) |

Udany build `hello-pipeline` potwierdza, że katalog narzędzi działa.

## Wprowadzanie zmian w konfiguracji

Konfigurację zmienia się **wyłącznie w pliku**, nie w interfejsie – zmiany z interfejsu zostaną nadpisane przy kolejnym wczytaniu pliku.

| Sposób | Jak |
|--------|-----|
| Plik skopiowany do obrazu | edycja pliku → `docker compose up -d --build` |
| Plik zamontowany (wygodne przy nauce) | dodać w `volumes`: `- ./jenkins-casc.yaml:/var/jenkins_home/casc/jenkins-casc.yaml:ro`; po edycji Manage Jenkins → Configuration as Code → **Reload existing configuration** – bez restartu |

Przycisk **View Configuration** na tej samej stronie pokazuje bieżącą konfigurację Jenkinsa jako YAML – przydaje się, gdy trzeba sprawdzić, jak zapisać ustawienie wyklikane w interfejsie.

## Typowe problemy

| Objaw | Przyczyna | Rozwiązanie |
|-------|-----------|-------------|
| `No configurator for the following root elements` / `Invalid configuration elements` | brak wtyczki obsługującej sekcję (np. `nodejs`) | dopisać wtyczkę do `plugins.txt`, przebudować obraz |
| Błąd nierozwiązanej zmiennej `${...}` | brak wpisu w `.env` | uzupełnić `.env`, zrestartować kontener |
| Zadania nie zostały utworzone | błąd w skrypcie Job DSL | sprawdzić logi – literówka w Groovy zatrzymuje tworzenie zadań |
| `hello-pipeline` nie pobiera narzędzi | brak internetu w kontenerze lub nieistniejąca wersja | sprawdzić sieć i wersje w sekcji `tool` |
| Pipeline nie może użyć `docker` | brak dostępu do demona Dockera | patrz sekcja niżej |

## Docker w buildach

Narzędzie `docker` z szablonu instaluje tylko **klienta CLI**. Do budowania obrazów potrzebny jest dostęp do demona Dockera:

- **Nauka, lokalny komputer:** zamontowanie gniazda hosta `- /var/run/docker.sock:/var/run/docker.sock`. Daje to kontenerowi Jenkinsa pełną kontrolę nad hostem, więc nie nadaje się do produkcji.
- **Produkcja:** buildy z Dockerem na osobnych agentach, a na kontrolerze `numExecutors: 0`.

## Wariant: istniejąca instalacja Jenkinsa

1. Zainstalować wtyczki z listy przez Manage Jenkins → Plugins.
2. Skopiować plik na serwer, np. `/var/lib/jenkins/casc/jenkins-casc.yaml`.
3. Ustawić zmienne z sekretami w środowisku usługi. Dla systemd: `systemctl edit jenkins` i w sekcji `[Service]` linie `Environment="JENKINS_ADMIN_PASSWORD=..."`, następnie `systemctl restart jenkins`.
4. W Manage Jenkins → Configuration as Code wpisać ścieżkę do pliku i kliknąć **Apply new configuration**.

> ⚠️ Sekcja `securityRealm` zastąpi istniejące konta – administratorem zostanie użytkownik `admin` z pliku. Przed zastosowaniem należy wykonać kopię katalogu `JENKINS_HOME`.

## Korzyści z JCasC

| Korzyść | Wyjaśnienie |
|---------|-------------|
| Powtarzalność | identyczna konfiguracja na każdej instancji (dev, test, produkcja) |
| Historia zmian | konfiguracja w Git – wiadomo, kto, kiedy i dlaczego coś zmienił |
| Code review | zmiany konfiguracji przechodzą przez pull requesty |
| Odtwarzanie po awarii | nowa instancja jest gotowa w kilka minut, bez ręcznego klikania |
| Bezpieczeństwo sekretów | hasła i tokeny ze zmiennych środowiskowych, nie z pliku |

## Uwagi

Szablon i pliki pomocnicze nie zostały uruchomione na rzeczywistym Jenkinsie. Poprawność składni YAML została sprawdzona parserem. Ostateczną weryfikację zapewnia start Jenkinsa – JCasC zgłasza błędy konfiguracji w logach i na stronie Configuration as Code przed jej zastosowaniem.
