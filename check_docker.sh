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
