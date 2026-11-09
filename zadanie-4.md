# Zadanie 4: zużycie pamięci przez kontener Docker – prompt bez roli a prompt z rolą eksperta

Modelowi zadano to samo pytanie dwukrotnie: najpierw bez żadnego kontekstu, a następnie z nadaną rolą doświadczonego DevOps Engineera.

## Prompt 1 (bez roli)

```
Jak rozwiązać problem z dużym zużyciem pamięci przez kontener Docker?
```

### Odpowiedź modelu

Zacznij od diagnozy, bo „duże zużycie” może mieć kilka źródeł. Polecenie `docker stats` pokaże bieżące zużycie RAM przez każdy kontener na tle limitu, a `docker inspect --format '{{.State.OOMKilled}}' nazwa_kontenera` powie, czy kontener był już ubijany przez brak pamięci. Warto też wejść do środka (`docker exec -it nazwa_kontenera top` lub `ps aux`) i sprawdzić, który proces faktycznie zajmuje pamięć. Pamiętaj, że część zużycia to pamięć podręczna plików (page cache), którą jądro zwalnia samo w razie potrzeby, więc rosnąca liczba nie zawsze oznacza wyciek.

Podstawowym rozwiązaniem jest ustawienie twardego limitu, bo domyślnie kontener może zająć całą pamięć hosta. Przy uruchamianiu robisz to tak:

```bash
# Limit 512 MB RAM, bez dodatkowego swapu (memory-swap = memory)
docker run -d --memory=512m --memory-swap=512m --name app moja-aplikacja

# Zmiana limitu w działającym kontenerze
docker update --memory=512m --memory-swap=512m app
```

A w `docker-compose.yml`:

```yaml
services:
  app:
    image: moja-aplikacja
    deploy:
      resources:
        limits:
          memory: 512M      # twardy limit, po przekroczeniu OOM kill
        reservations:
          memory: 256M      # gwarantowane minimum
```

Sam limit nie usuwa jednak przyczyny, tylko zamienia powolne „zjadanie” hosta na restart kontenera. Trzeba więc dopasować aplikację do limitu. W Node.js (jak w zadaniu 3) sterta V8 nie zawsze respektuje limit kontenera, dlatego warto ustawić `ENV NODE_OPTIONS="--max-old-space-size=384"`, czyli około 75% limitu. W Javie odpowiednikiem jest `-XX:MaxRAMPercentage=75`, a w Pythonie najczęstszą przyczyną są wycieki (rosnące listy, cache w pamięci, wczytywanie całych plików przez pandas zamiast porcjami przez `chunksize`). Jeśli zużycie rośnie stale przez cały czas działania, to niemal na pewno wyciek w kodzie i trzeba go namierzyć profilerem, na przykład `node --inspect` lub `tracemalloc` w Pythonie.

Na koniec pomocne są lżejsze obrazy (np. `-alpine` lub `-slim`), uruchamianie jednego procesu na kontener oraz polityka `restart: unless-stopped` jako zabezpieczenie po OOM. Jeśli pracujesz na Docker Desktop, sprawdź też w ustawieniach (Resources), ile pamięci przydzielono maszynie wirtualnej Dockera, bo `vmmem` na Windowsie potrafi zająć większość RAM-u niezależnie od kontenerów. Przy okazji: `docker system prune` zwalnia miejsce na dysku, a nie pamięć RAM.

## Prompt 2 (z rolą eksperta)

```
Jesteś doświadczonym DevOps Engineerem z 10-letnim doświadczeniem. Jak rozwiązać problem z dużym zużyciem pamięci przez kontener Docker?
```

### Odpowiedź modelu

Z perspektywy kogoś, kto gasił takie pożary na produkcji wiele razy, najważniejsza zasada brzmi: nie zaczynaj od podnoszenia limitu, tylko od ustalenia, co naprawdę zajmuje pamięć. W większości przypadków, które widziałem, przyczyna należała do jednej z trzech kategorii: brak limitów, aplikacja nieświadoma limitów kontenera albo zwykły wyciek pamięci w kodzie. Rzadziej winny jest page cache, który tylko wygląda groźnie.

Pierwszy krok to rzetelny pomiar. `docker stats` daje szybki obraz, ale przy wątpliwościach patrzę bezpośrednio w cgroup, bo tam widać podział na pamięć anonimową (sterta procesu, to jest realny problem) i pamięć plików (cache, który jądro odda samo):

```bash
# Szybki przegląd wszystkich kontenerów
docker stats --no-stream

# Czy kontener był ubity przez OOM i ile razy się restartował
docker inspect --format '{{.State.OOMKilled}} {{.RestartCount}}' app

# Szczegółowy podział pamięci w cgroup v2 (anon = sterta, file = cache)
docker exec app cat /sys/fs/cgroup/memory.stat | grep -E '^(anon|file|shmem) '
```

Jeśli rośnie `anon`, problem leży w aplikacji. Jeśli `file`, zwykle nie ma się czym martwić, chyba że aplikacja intensywnie pisze logi lub pliki tymczasowe do warstwy kontenera albo do `tmpfs`, co też liczy się do limitu.

Drugi krok to limity, i to obowiązkowo na każdym kontenerze produkcyjnym. Kontener bez limitu potrafi wywołać OOM killera na hoście i położyć sąsiednie usługi, co jest znacznie gorsze niż restart jednego kontenera. Ustawiam twardy limit, wyłączam swap dla kontenera (swap maskuje problem i niszczy wydajność) oraz dodaję politykę restartu:

```yaml
services:
  app:
    image: moja-aplikacja
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    memswap_limit: 512M   # równe limitowi = brak swapu
```

Trzeci krok, najczęściej pomijany, to uświadomienie aplikacji, ile ma pamięci. Runtime'y z garbage collectorem domyślnie liczą zapas względem całego hosta albo własnych domyślnych progów i nie sprzątają, dopóki nie jest za późno. W Node.js ustawiam `NODE_OPTIONS="--max-old-space-size=384"` przy limicie 512 MB, zostawiając margines na bufory i pamięć natywną. W JVM używam `-XX:MaxRAMPercentage=75`, a nie sztywnego `-Xmx`. W Pythonie nie ma takiego przełącznika, więc tam liczy się kod: przetwarzanie strumieniowe zamiast wczytywania całych zbiorów, ograniczone cache (`functools.lru_cache(maxsize=...)`) i liczba workerów Gunicorna dobrana do pamięci, bo każdy worker to osobna kopia aplikacji.

Czwarty krok to wyciek. Charakterystyczny objaw to piłokształtny wykres: pamięć rośnie liniowo przez godziny, OOM, restart, i od nowa. Restart co noc to plaster, nie rozwiązanie. Robię wtedy dwa zrzuty sterty w odstępie czasu i porównuję je: w Node przez `node --inspect` i Chrome DevTools lub `heapdump`, w Pythonie przez `tracemalloc.take_snapshot()` i `compare_to()`, w Javie przez `jcmd <pid> GC.heap_dump`. Typowi winowajcy to nieograniczone mapy jako cache, nasłuchiwacze zdarzeń dodawane przy każdym żądaniu i niezamykane połączenia.

Na koniec to, co odróżnia gaszenie pożaru od dojrzałej praktyki: obserwowalność. Zbieram metryki kontenerów przez cAdvisor do Prometheusa, rysuję je w Grafanie i ustawiam alert na poziomie około 80% limitu oraz na każdy restart z powodu OOM. Dzięki temu o problemie dowiaduję się z trendu tydzień wcześniej, a nie z telefonu o trzeciej w nocy. Przy okazji warto odchudzić obraz (`-slim` lub wieloetapowy build), choć to bardziej wpływa na rozmiar na dysku i czas startu niż na zużycie RAM w czasie działania.

## Obserwacje

Merytoryczny rdzeń obu odpowiedzi jest wspólny: diagnoza przez `docker stats` i `docker inspect`, twardy limit pamięci z wyłączonym swapem, dostrojenie runtime'u do limitu (`--max-old-space-size` w Node.js, `MaxRAMPercentage` w JVM), szukanie wycieków profilerem oraz uwaga, że page cache nie zawsze oznacza problem. Nadanie roli nie zmieniło więc tego, co model wie, lecz sposób, w jaki tę wiedzę uporządkował i podał.

Odpowiedź bez roli ma charakter poradnika dla szerokiego odbiorcy. Jest zwięźlejsza, zawiera porady przydatne początkującym (ustawienia pamięci w Docker Desktop, wyjaśnienie, że `docker system prune` zwalnia dysk, a nie RAM) i nawiązuje do wcześniejszego zadania z Node.js. Odpowiedź z rolą jest zbudowana jak metodyka pracy: cztery kolejne kroki (pomiar, limity, dostrojenie aplikacji, wyciek) poprzedzone zasadą „najpierw ustal przyczynę, potem podnoś limit”. Pojawiają się w niej elementy głębsze technicznie, których zabrakło w pierwszej wersji: analiza `memory.stat` w cgroup v2 z rozróżnieniem pamięci anonimowej i plikowej, liczba restartów w `docker inspect`, wpływ liczby workerów Gunicorna, metoda porównywania dwóch zrzutów sterty oraz obserwowalność (cAdvisor, Prometheus, Grafana, alert przy 80% limitu). To ostatnie przesuwa perspektywę z jednorazowej naprawy na zapobieganie problemom, co jest typowe dla dojrzałej praktyki DevOps.

Rola wpłynęła też na styl. Model pisze w pierwszej osobie („ustawiam”, „robię wtedy”, „w większości przypadków, które widziałem”), uzasadnia decyzje doświadczeniem (np. dlaczego wyłącza swap) i używa języka praktyka („gaszenie pożarów”, „restart co noc to plaster”). Odpowiedź jest przez to dłuższa i bardziej przekonująca, ale trzeba pamiętać, że „doświadczenie” jest tu jedynie konwencją narracyjną, a nie dodatkowym źródłem wiedzy, więc twierdzenia nadal wymagają weryfikacji tak samo jak w odpowiedzi bez roli.

Wniosek jest taki, że nadanie roli eksperta działa jak niejawne doprecyzowanie oczekiwań: model zakłada bardziej zaawansowanego odbiorcę i środowisko produkcyjne, więc dobiera głębsze narzędzia, porządkuje odpowiedź w proces i dodaje perspektywę długoterminową. Prompt bez roli lepiej sprawdza się przy szybkim, ogólnym rozeznaniu, a prompt z rolą wtedy, gdy potrzebna jest odpowiedź na poziomie produkcyjnym. Podobnie jak w zadaniu 3, najlepszy efekt daje połączenie obu technik: rola eksperta plus precyzyjny opis kontekstu (np. technologia aplikacji, środowisko, objawy problemu).
