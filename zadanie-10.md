Ignorowanie tych plików wynika z kilku powodów.

**Bezpieczeństwo** jest najważniejsze. Pliki `.env`, klucze `*.key` i certyfikaty zawierają hasła, connection stringi do MongoDB i klucze API. Raz wypchnięte do Gita zostają w historii repozytorium na zawsze, nawet po usunięciu pliku w kolejnym commicie. W publicznym repozytorium boty skanujące GitHub potrafią wyłapać taki sekret w ciągu kilku minut. Jedynym pewnym ratunkiem jest wtedy natychmiastowa zmiana hasła lub klucza.

**Rozmiar i wydajność repozytorium.** Katalog `node_modules/` potrafi mieć setki megabajtów i dziesiątki tysięcy plików. Pliki danych MongoDB (WiredTiger) są binarne, duże i zmieniają się przy każdym zapisie do bazy, więc każdy commit dokładałby kolejne megabajty. Klonowanie, pobieranie i przeglądanie zmian byłoby przez to wolne. W dodatku diff binarnych plików i tak niczego nie mówi.

**Odtwarzalność zamiast kopiowania.** Wszystko, co jest ignorowane, da się wygenerować na nowo. Zależności odtwarza `npm ci` na podstawie `package-lock.json`, katalog `dist/` powstaje z kodu źródłowego, a bazę uruchamia `docker compose up`. Dlatego w repozytorium trzymamy przepis, czyli `package.json`, `Dockerfile`, `docker-compose.yml` i `.env.example`, a nie gotowe wyniki.

**Zgodność środowisk.** `node_modules` zawiera czasem moduły natywne skompilowane pod konkretny system. Moduły zbudowane na macOS czy Windowsie nie zadziałają w kontenerze Linux. Każde środowisko, w tym obraz Dockera, powinno więc instalować zależności samodzielnie.

**Brak konfliktów w zespole.** Logi, cache, ustawienia edytora czy lokalny `docker-compose.override.yml` różnią się u każdej osoby. Gdyby były wersjonowane, ciągle powodowałyby konflikty przy merge'u i zaśmiecały historię zmianami, które nie dotyczą kodu.

**Ochrona danych.** Lokalna baza i zrzuty z `mongodump` mogą zawierać dane osobowe użytkowników, a ich publikacja może naruszać RODO.
