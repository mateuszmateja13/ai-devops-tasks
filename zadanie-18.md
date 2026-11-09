# Zadanie 18 – Bezpieczeństwo aplikacji Dockerowych w produkcji

## Część 1. Pięć kluczowych praktyk bezpieczeństwa

### 1. Uruchamianie kontenera bez roota i z minimalnymi uprawnieniami

Domyślnie proces w kontenerze działa jako root, więc ucieczka z kontenera daje atakującemu roota na hoście. W Dockerfile należy dodać instrukcję `USER` z nieuprzywilejowanym kontem. Przy uruchamianiu trzeba odebrać zbędne capabilities (`--cap-drop ALL`, a następnie dodać tylko niezbędne), włączyć `--security-opt no-new-privileges`, zamontować system plików jako `--read-only` i nigdy nie używać `--privileged` ani nie montować `/var/run/docker.sock`, bo to w praktyce pełna kontrola nad hostem.

### 2. Minimalne, przypięte i skanowane obrazy

Każdy zbędny pakiet w obrazie zwiększa powierzchnię ataku. Pomagają tu obrazy bazowe typu distroless lub alpine, budowanie wieloetapowe (multi-stage), w którym kompilatory i narzędzia buildu zostają w etapie budowania, oraz przypinanie wersji, najlepiej przez digest (`image@sha256:...`) zamiast tagu `latest`. Obraz należy skanować w CI (Trivy, Grype, Docker Scout), blokować wdrożenie przy krytycznych podatnościach i regularnie przebudowywać obrazy, aby pobierały poprawki bezpieczeństwa.

### 3. Właściwe zarządzanie sekretami

Hasła i klucze nie powinny trafiać do `ENV` w Dockerfile ani do warstw obrazu, ponieważ można je odczytać przez `docker history` lub `docker inspect`. Sekrety należy przekazywać w czasie działania przez Docker secrets, Kubernetes Secrets lub zewnętrzny sejf (HashiCorp Vault, AWS Secrets Manager), a sekrety potrzebne przy budowaniu podawać przez BuildKit `RUN --mount=type=secret`. Plik `.dockerignore` powinien wykluczać `.env`, klucze i katalog `.git`.

### 4. Limity zasobów i izolacja sieci

Kontener bez limitów może zająć całą pamięć i CPU hosta, celowo (atak DoS) lub w wyniku błędu. Należy ustawić `--memory`, `--cpus` i `--pids-limit`. W warstwie sieciowej warto używać osobnych sieci zdefiniowanych przez użytkownika (np. baza danych dostępna tylko dla backendu), publikować wyłącznie niezbędne porty, a usługi wewnętrzne wiązać z `127.0.0.1` zamiast `0.0.0.0`.

### 5. Zaufany łańcuch dostaw, aktualny host i monitoring

Obrazy warto podpisywać (cosign, Docker Content Trust) i dopuszczać do wdrożenia tylko podpisane obrazy z zaufanego rejestru. Silnik Dockera i jądro hosta muszą być aktualizowane, a tam, gdzie to możliwe, należy stosować tryb rootless lub user namespaces. W czasie działania pomagają centralne logowanie, `HEALTHCHECK` oraz wykrywanie anomalii (np. Falco – alarm, gdy w kontenerze nagle uruchamia się powłoka).

### Przykład łączący praktyki

```yaml
services:
  api:
    image: registry.example.com/api@sha256:<digest>   # przypięty, podpisany obraz
    user: "10001:10001"                               # bez roota
    read_only: true
    tmpfs: [/tmp]
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    secrets: [db_password]                            # zamiast ENV
    ports: ["127.0.0.1:8080:8080"]                    # tylko lokalnie, dalej przez reverse proxy
    networks: [backend]
    deploy:
      resources:
        limits: { cpus: "1.0", memory: 512M, pids: 200 }

networks:
  backend:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

## Część 2. Implementacja praktyki nr 1 – kontener bez roota

Praktyka ma dwie warstwy: w **Dockerfile** tworzy się nieuprzywilejowanego użytkownika i przełącza na niego, a w **docker-compose.yml** odbiera się kontenerowi uprawnienia w czasie działania. Przykład dotyczy aplikacji Node.js, ale zasada jest taka sama dla każdego języka.

### Dockerfile

```dockerfile
# ---------- Etap budowania ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .

# ---------- Etap produkcyjny ----------
FROM node:22-alpine

# Użytkownik systemowy bez powłoki i katalogu domowego, ze stałym UID/GID
RUN addgroup -S -g 10001 app && \
    adduser  -S -u 10001 -G app -H -s /sbin/nologin app

WORKDIR /app

# Pliki należą do roota i są tylko do odczytu dla aplikacji,
# więc nawet przejęty proces nie podmieni kodu
COPY --from=build --chown=root:root --chmod=755 /app /app

# Jedyny katalog, do którego aplikacja może pisać
RUN mkdir -p /app/data && chown app:app /app/data

ENV NODE_ENV=production
# Port powyżej 1024 – użytkownik bez roota nie może nasłuchiwać na 80/443
EXPOSE 8080

USER 10001:10001

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:8080/health || exit 1

CMD ["node", "server.js"]
```

### docker-compose.yml

```yaml
services:
  app:
    build: .
    user: "10001:10001"                 # wymusza UID nawet przy obcym obrazie
    read_only: true                     # system plików kontenera tylko do odczytu
    tmpfs:
      - /tmp:size=64m,noexec,nosuid     # zapisywalne katalogi tymczasowe
    volumes:
      - app-data:/app/data              # trwałe dane w osobnym wolumenie
    cap_drop:
      - ALL                             # odebranie wszystkich capabilities
    # cap_add:
    #   - NET_BIND_SERVICE              # tylko gdy aplikacja MUSI słuchać na porcie < 1024
    security_opt:
      - no-new-privileges:true          # blokuje eskalację przez setuid/sudo
    privileged: false
    ports:
      - "8080:8080"
    # Celowo brak montowania /var/run/docker.sock

volumes:
  app-data:
```

### Na co uważać

| Kwestia | Wyjaśnienie |
|---------|-------------|
| Stały UID/GID | Uprawnienia do wolumenów i plików hosta są sprawdzane po numerze, a nie po nazwie użytkownika, dlatego ten sam UID (10001) ustawia się w Dockerfile i w Compose. |
| `read_only: true` | Aplikacja zgłosi błąd przy każdej próbie zapisu poza `tmpfs` i wolumenami. Pozwala to wykryć wszystkie miejsca zapisu (cache, pliki PID, logi do pliku). Logi najlepiej kierować na stdout. |
| Istniejące wolumeny | Wolumen utworzony wcześniej przez roota wymaga jednorazowej zmiany właściciela: `docker run --rm -v app-data:/data alpine chown -R 10001:10001 /data`. |
| Porty < 1024 | Użytkownik bez roota nie może ich otworzyć. Aplikacja słucha na 8080, a port 80/443 obsługuje reverse proxy lub mapowanie portów. |
| Obrazy Debian/Ubuntu | Zamiast `addgroup -S` / `adduser -S` stosuje się `groupadd -r -g 10001 app` i `useradd -r -u 10001 -g app -M -s /usr/sbin/nologin app`. |
| Gotowy użytkownik | Oficjalne obrazy Node mają użytkownika `node` (UID 1000), którego można użyć zamiast tworzyć własnego. |

### Weryfikacja

```bash
docker compose exec app id                      # oczekiwane: uid=10001(app) gid=10001(app)
docker compose exec app touch /app/test         # oczekiwane: Read-only file system
docker compose exec app grep Cap /proc/1/status # CapEff: 0000000000000000 = brak capabilities
docker inspect --format '{{.HostConfig.SecurityOpt}}' $(docker compose ps -q app)
```
