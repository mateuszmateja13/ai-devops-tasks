# Zadanie 7: skrypt bash – kontrola usługi Docker

Model poproszono o prosty skrypt bash, który sprawdza stan usługi Docker i w razie potrzeby próbuje ją uruchomić, a następnie o wyjaśnienie jego działania linia po linii dla osoby początkującej. Gotowy skrypt zapisano w repozytorium jako [`check_docker.sh`](check_docker.sh).

## Prompt 1 (skrypt)

```
Napisz prosty skrypt bash, który sprawdza, czy usługa Docker działa, a jeśli nie - próbuje ją uruchomić.
```

### Odpowiedź modelu

```bash
#!/usr/bin/env bash
# Sprawdza, czy usługa Docker działa, a jeśli nie - próbuje ją uruchomić.
# Użycie: ./check_docker.sh

set -u

# Polecenia administracyjne wymagają uprawnień roota - jeśli ich nie mamy, używamy sudo.
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# Sprawdza, czy demon Docker odpowiada.
docker_dziala() {
    if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
        systemctl is-active --quiet docker
    else
        $SUDO docker info >/dev/null 2>&1
    fi
}

# Uruchamia usługę Docker za pomocą systemctl albo (bez systemd) polecenia service.
uruchom_docker() {
    if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
        $SUDO systemctl start docker
    else
        $SUDO service docker start
    fi
}

# Bez zainstalowanego Dockera nie ma czego uruchamiać.
if ! command -v docker >/dev/null 2>&1; then
    echo "BŁĄD: Docker nie jest zainstalowany." >&2
    exit 2
fi

if docker_dziala; then
    echo "OK: usługa Docker działa."
    exit 0
fi

echo "Usługa Docker nie działa - próbuję ją uruchomić..."
uruchom_docker

# Demon potrzebuje chwili na start, więc sprawdzamy kilka razy.
for _ in 1 2 3 4 5; do
    if docker_dziala; then
        echo "OK: usługa Docker została uruchomiona."
        exit 0
    fi
    sleep 2
done

echo "BŁĄD: nie udało się uruchomić usługi Docker." >&2
echo "Sprawdź logi: journalctl -u docker --no-pager -n 50" >&2
exit 1
```

## Uruchomienie

```bash
chmod +x check_docker.sh
./check_docker.sh
```

## Opis

Skrypt najpierw sprawdza, czy Docker jest w ogóle zainstalowany, a następnie weryfikuje stan usługi poleceniem `systemctl is-active` (na systemach z systemd) lub `docker info` (na systemach bez systemd, np. w WSL). Jeśli usługa nie działa, skrypt uruchamia ją przez `systemctl start docker` albo `service docker start`, w razie potrzeby z użyciem `sudo`, po czym przez około 10 sekund ponawia sprawdzenie, bo demon potrzebuje chwili na start. Kody wyjścia pozwalają wykorzystać skrypt w automatyzacji: 0 oznacza działającą usługę, 1 nieudane uruchomienie, a 2 brak zainstalowanego Dockera.

## Prompt 2 (wyjaśnienie linia po linii)

```
Wyjaśnij działanie tego skryptu linia po linii, tak jakbyś tłumaczył osobie początkującej.
```

### Odpowiedź modelu

Poniżej wyjaśnienie fragment po fragmencie, w kolejności, w jakiej bash wykonuje skrypt.

```bash
#!/usr/bin/env bash
```

To tak zwany shebang. Mówi systemowi, jakim programem uruchomić plik. Tutaj jest to bash, a `env` sam znajduje, gdzie bash jest zainstalowany. Dzięki temu skrypt można odpalić wprost przez `./check_docker.sh`.

```bash
# Sprawdza, czy usługa Docker działa, a jeśli nie - próbuje ją uruchomić.
# Użycie: ./check_docker.sh
```

Linie zaczynające się od `#` to komentarze. Bash je pomija, są tylko dla człowieka czytającego kod.

```bash
set -u
```

To włącza tryb ostrożny. Jeśli gdzieś w skrypcie użyjemy zmiennej, której nie zdefiniowaliśmy, na przykład przez literówkę, skrypt zatrzyma się z błędem, zamiast po cichu podstawić pusty tekst.

```bash
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi
```

Polecenie `id -u` zwraca numer użytkownika, a administrator (root) ma zawsze numer 0. Zapis `$( )` oznacza „wykonaj polecenie i wstaw jego wynik”, a `-eq` to porównanie liczb. Jeśli jesteśmy rootem, zmienna `SUDO` jest pusta. W przeciwnym razie zawiera słowo `sudo`, czyli polecenie dające chwilowo uprawnienia administratora. Później wpisujemy `$SUDO` przed poleceniami wymagającymi uprawnień i skrypt sam dopasowuje się do sytuacji. Konstrukcja `if … then … else … fi` to zwykły warunek, a `fi` to po prostu „if” czytane od tyłu, czyli koniec warunku.

```bash
docker_dziala() {
    if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
        systemctl is-active --quiet docker
    else
        $SUDO docker info >/dev/null 2>&1
    fi
}
```

Tu definiujemy funkcję, czyli nazwany kawałek kodu, który można wywołać wiele razy. Ta funkcja odpowiada na pytanie, czy Docker działa. Najpierw sprawdza, czy system używa systemd, czyli menedżera usług obecnego w większości współczesnych dystrybucji Linuksa. `command -v systemctl` sprawdza, czy istnieje polecenie `systemctl`, a `[ -d /run/systemd/system ]` sprawdza, czy istnieje katalog tworzony przez działający systemd. `&&` oznacza „i”, więc oba warunki muszą być spełnione. Fragment `>/dev/null 2>&1` wycisza wszystko, co polecenie wypisuje, bo interesuje nas tylko, czy się udało. Jeśli systemd jest, `systemctl is-active --quiet docker` po cichu sprawdza stan usługi. Jeśli go nie ma, na przykład w WSL, pytamy samego Dockera przez `docker info`, które zadziała tylko wtedy, gdy Docker jest uruchomiony. W bashu każde polecenie kończy się kodem wyjścia: 0 oznacza sukces, inna liczba porażkę. Funkcja zwraca kod ostatniego polecenia, dlatego można jej potem użyć w `if`.

```bash
uruchom_docker() {
    if command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
        $SUDO systemctl start docker
    else
        $SUDO service docker start
    fi
}
```

Druga funkcja działa analogicznie, ale zamiast sprawdzać, uruchamia usługę. Z systemd robi to przez `systemctl start docker`, a bez niego przez starsze polecenie `service docker start`. Na początku stoi `$SUDO`, bo start usługi wymaga uprawnień administratora.

```bash
if ! command -v docker >/dev/null 2>&1; then
    echo "BŁĄD: Docker nie jest zainstalowany." >&2
    exit 2
fi
```

Tu zaczyna się właściwe działanie skryptu, bo funkcje były tylko zdefiniowane. Wykrzyknik `!` odwraca warunek, więc czytamy to jako „jeśli polecenie docker nie istnieje”. Wtedy `echo` wypisuje komunikat, a `>&2` kieruje go na strumień błędów, gdzie zgodnie z konwencją trafiają komunikaty o problemach. `exit 2` kończy skrypt z kodem 2, który umówiliśmy jako „brak Dockera”.

```bash
if docker_dziala; then
    echo "OK: usługa Docker działa."
    exit 0
fi
```

Wywołujemy pierwszą funkcję. Jeśli Docker już działa, wypisujemy komunikat i kończymy z kodem 0, czyli sukcesem. Dalsza część skryptu się wtedy nie wykona.

```bash
echo "Usługa Docker nie działa - próbuję ją uruchomić..."
uruchom_docker
```

Do tego miejsca dochodzimy tylko wtedy, gdy Docker nie działa. Informujemy o tym użytkownika i wywołujemy funkcję uruchamiającą usługę.

```bash
for _ in 1 2 3 4 5; do
    if docker_dziala; then
        echo "OK: usługa Docker została uruchomiona."
        exit 0
    fi
    sleep 2
done
```

Docker nie startuje natychmiast, więc zamiast sprawdzić stan raz, robimy to w pętli `for` pięć razy. Podkreślnik `_` to nazwa zmiennej, której nie używamy, bo liczy się tylko liczba powtórzeń. W każdym obrocie sprawdzamy, czy Docker już działa. Jeśli tak, kończymy sukcesem. Jeśli nie, `sleep 2` czeka 2 sekundy i pętla próbuje ponownie. Razem daje to około 10 sekund cierpliwości.

```bash
echo "BŁĄD: nie udało się uruchomić usługi Docker." >&2
echo "Sprawdź logi: journalctl -u docker --no-pager -n 50" >&2
exit 1
```

Jeśli po pięciu próbach Docker nadal nie działa, wypisujemy błąd i podpowiedź, gdzie szukać przyczyny. `journalctl -u docker` pokazuje dziennik usługi Docker, a `-n 50` ogranicza go do 50 ostatnich wpisów. Skrypt kończy się kodem 1, czyli „nie udało się uruchomić”.

Całość działa więc jak prosta lista kontrolna: czy Docker jest zainstalowany, czy działa, a jeśli nie, to próba uruchomienia i chwila oczekiwania. Kody wyjścia 0, 1 i 2 pozwalają innym skryptom lub potokom CI/CD sprawdzić wynik bez czytania komunikatów.
