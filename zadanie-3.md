# Zadanie 3: Dockerfile dla aplikacji Node.js – prompt ogólny a prompt precyzyjny

Modelowi zadano dwa prompty dotyczące tego samego problemu: najpierw bardzo krótki i ogólny, a następnie szczegółowy, z wymienionymi wymaganiami.

## Prompt 1 (ogólny)

```
dockerfile node
```

### Odpowiedź modelu

```dockerfile
# syntax=docker/dockerfile:1

# ---------- Etap 1: instalacja zależności i build ----------
FROM node:24-alpine AS build
WORKDIR /app

# Kopiujemy najpierw manifesty, aby wykorzystać cache warstw Dockera
COPY package*.json ./
RUN npm ci

# Kopiujemy kod źródłowy i budujemy (jeśli projekt ma skrypt "build")
COPY . .
RUN npm run build --if-present

# Usuwamy zależności deweloperskie przed przeniesieniem do obrazu produkcyjnego
RUN npm prune --omit=dev

# ---------- Etap 2: lekki obraz produkcyjny ----------
FROM node:24-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

# Przenosimy tylko to, co potrzebne do uruchomienia
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package*.json ./
COPY --from=build /app/dist ./dist
# Jeśli projekt nie ma kroku build, zamień powyższą linię na: COPY --from=build /app/src ./src

# Uruchamiamy jako nieuprzywilejowany użytkownik (dobra praktyka bezpieczeństwa)
USER node

EXPOSE 3000

# Prosty healthcheck endpointu /health (dostosuj ścieżkę lub usuń)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "dist/index.js"]
```

Komentarz modelu: Dockerfile jest dwuetapowy. Pierwszy etap instaluje zależności przez `npm ci` i buduje projekt, drugi tworzy lekki obraz na `node:24-alpine` (aktualna linia LTS) z samymi zależnościami produkcyjnymi, uruchamiany jako użytkownik `node` na porcie 3000. Model zasugerował dodanie pliku `.dockerignore` (`node_modules`, `.git`, `.env`) i podał polecenia `docker build -t epgd-app .` oraz `docker run -p 3000:3000 epgd-app`. Na końcu dopytał, czy aplikacja Node ma tylko wywoływać API w Pythonie (wtedy przydałby się `docker-compose`), czy serwować pliki statyczne.

## Prompt 2 (precyzyjny)

```
Napisz prosty Dockerfile dla aplikacji Node.js, który:
- używa Node 18 jako obrazu bazowego
- kopiuje pliki package.json i package-lock.json
- instaluje zależności
- kopiuje resztę plików aplikacji
- wystawia port 3000
- uruchamia aplikację poleceniem "npm start"
```

### Odpowiedź modelu

```dockerfile
# Obraz bazowy z Node.js 18
FROM node:18

# Katalog roboczy wewnątrz kontenera
WORKDIR /app

# Kopiowanie manifestów zależności (osobno, aby wykorzystać cache warstw)
COPY package.json package-lock.json ./

# Instalacja zależności zgodnie z package-lock.json
RUN npm install

# Kopiowanie pozostałych plików aplikacji
COPY . .

# Port, na którym nasłuchuje aplikacja
EXPOSE 3000

# Uruchomienie aplikacji
CMD ["npm", "start"]
```

Komentarz modelu: plik realizuje dokładnie wymienione kroki. Manifesty są kopiowane przed resztą kodu, więc warstwa z zależnościami jest odtwarzana tylko po ich zmianie. Obraz buduje się poleceniem `docker build -t moja-aplikacja .`, a uruchamia poleceniem `docker run -p 3000:3000 moja-aplikacja`. Model zwrócił uwagę, że Node 18 nie ma wsparcia od kwietnia 2025 roku (brak poprawek bezpieczeństwa), i zaproponował zmianę na `FROM node:24` oraz zastąpienie `npm install` poleceniem `npm ci`.

## Wnioski

Przy ogólnym prompcie model musiał sam uzupełnić brakujące założenia i wybrał rozwiązanie „produkcyjne”: budowanie wieloetapowe, obraz Alpine, użytkownika bez uprawnień roota, healthcheck i aktualną wersję LTS. Wynik jest bogatszy i bliższy dobrym praktykom, ale opiera się na zgadywaniu struktury projektu (katalog `dist`, plik `dist/index.js`, endpoint `/health`), więc bez dopasowania może nie zadziałać w konkretnej aplikacji. Model sam to dostrzegł, bo dodał komentarze o tym, co trzeba dostosować, i zadał pytanie doprecyzowujące.

Przy precyzyjnym prompcie odpowiedź jest krótka, przewidywalna i w pełni zgodna z wymaganiami punkt po punkcie. Działa dla typowej aplikacji z `npm start` bez żadnych zmian. Model nie zrezygnował jednak z oceny merytorycznej: wykonał polecenie dosłownie, a ryzyko (przestarzały Node 18, `npm install` zamiast `npm ci`) zgłosił osobno w komentarzu, zamiast samowolnie zmieniać wymagania.

Najważniejszy wniosek jest taki, że im dokładniej opisane są wymagania, tym mniej model zgaduje i tym łatwiej zweryfikować wynik. Ogólny prompt przydaje się, gdy chcemy poznać dobre praktyki i możliwe warianty, a precyzyjny, gdy potrzebujemy konkretnego, sprawdzalnego rezultatu. W praktyce DevOps dobrze sprawdza się połączenie obu podejść: precyzyjne wymagania w prompcie oraz prośba o wskazanie ryzyk i usprawnień w osobnym komentarzu.
