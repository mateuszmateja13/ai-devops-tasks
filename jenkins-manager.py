#!/usr/bin/env python3
"""
Klient Jenkins REST API: listowanie zadań, status ostatnich buildów, uruchamianie zadań.

Konfiguracja przez zmienne środowiskowe:
    JENKINS_URL    adres Jenkinsa, np. https://jenkins.example.com
    JENKINS_USER   nazwa użytkownika
    JENKINS_TOKEN  token API (Jenkins → użytkownik → Security → API Token)

Przykłady:
    python jenkins-manager.py list
    python jenkins-manager.py status
    python jenkins-manager.py status moj-folder/moja-aplikacja
    python jenkins-manager.py build moja-aplikacja
    python jenkins-manager.py build moja-aplikacja --param ENV=staging --param VERSION=1.2.3 --wait
"""

import argparse
import os
import sys
import time
from datetime import datetime
from urllib.parse import quote

import requests


class JenkinsError(Exception):
    """Błąd komunikacji z Jenkinsem z czytelnym komunikatem dla użytkownika."""


class JenkinsClient:
    # Pola pobierane dla każdego zadania; "jobs" pozwala zejść do folderów i Multibranch
    JOB_FIELDS = "name,fullName,url,color,_class,lastBuild[number,result,building,timestamp,duration,url]"

    def __init__(self, base_url, user, token, timeout=15, verify_ssl=True):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        # Uwierzytelnianie Basic: użytkownik + token API (nie hasło do konta)
        self.session.auth = (user, token)
        self.session.verify = verify_ssl
        self.session.headers.update({"Accept": "application/json"})
        self._crumb_header = None

    # ------------------------------------------------------------------ HTTP

    def _request(self, method, path, **kwargs):
        """Wysyła żądanie i zamienia błędy HTTP/sieci na JenkinsError z opisem przyczyny."""
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.exceptions.SSLError as exc:
            raise JenkinsError(f"Błąd certyfikatu SSL dla {url}: {exc}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise JenkinsError(f"Nie można połączyć się z {self.base_url} – sprawdź adres i sieć") from exc
        except requests.exceptions.Timeout as exc:
            raise JenkinsError(f"Przekroczono limit czasu ({self.timeout} s) dla {url}") from exc

        if response.ok:
            return response

        messages = {
            401: "Nieprawidłowy użytkownik lub token API (401)",
            403: "Brak uprawnień do tej operacji (403) – sprawdź uprawnienia użytkownika lub token CSRF",
            404: f"Nie znaleziono zasobu (404): {url}",
        }
        message = messages.get(response.status_code, f"Błąd HTTP {response.status_code} dla {url}")
        raise JenkinsError(message)

    def _get_json(self, path, params=None):
        response = self._request("GET", path, params=params)
        try:
            return response.json()
        except ValueError as exc:
            raise JenkinsError(f"Odpowiedź z {path} nie jest poprawnym JSON-em") from exc

    def _get_crumb(self):
        """
        Pobiera token CSRF (crumb), jeśli Jenkins go wymaga.
        Przy uwierzytelnianiu tokenem API nowsze wersje Jenkinsa go nie potrzebują,
        więc brak crumb issuera (404) nie jest błędem.
        """
        if self._crumb_header is None:
            try:
                data = self._get_json("/crumbIssuer/api/json")
                self._crumb_header = {data["crumbRequestField"]: data["crumb"]}
            except JenkinsError:
                self._crumb_header = {}
        return self._crumb_header

    @staticmethod
    def _job_path(full_name):
        """Zamienia 'folder/podfolder/zadanie' na '/job/folder/job/podfolder/job/zadanie'."""
        parts = [p for p in full_name.strip("/").split("/") if p]
        if not parts:
            raise JenkinsError("Nazwa zadania nie może być pusta")
        return "".join(f"/job/{quote(part, safe='')}" for part in parts)

    # ------------------------------------------------------------- operacje

    def list_jobs(self, max_depth=3):
        """Zwraca płaską listę zadań, także z folderów i Multibranch Pipeline."""
        # tree=jobs[...,jobs[...,jobs[...]]] – jedno zapytanie zamiast osobnego na każdy folder
        tree = self.JOB_FIELDS
        for _ in range(max_depth):
            tree = f"{self.JOB_FIELDS},jobs[{tree}]"
        data = self._get_json("/api/json", params={"tree": f"jobs[{tree}]"})

        jobs = []

        def walk(items):
            for item in items:
                if "jobs" in item:          # folder lub Multibranch – schodzimy głębiej
                    walk(item["jobs"])
                else:
                    jobs.append(item)

        walk(data.get("jobs", []))
        return jobs

    def get_job_status(self, full_name):
        """Zwraca informacje o zadaniu wraz z ostatnim buildem."""
        return self._get_json(f"{self._job_path(full_name)}/api/json", params={"tree": self.JOB_FIELDS})

    def trigger_build(self, full_name, params=None):
        """
        Uruchamia zadanie. Zwraca URL elementu kolejki (Jenkins najpierw kolejkuje build,
        numer buildu jest znany dopiero po jego starcie).
        """
        endpoint = "buildWithParameters" if params else "build"
        response = self._request(
            "POST",
            f"{self._job_path(full_name)}/{endpoint}",
            params=params or None,
            headers=self._get_crumb(),
        )
        queue_url = response.headers.get("Location")
        if not queue_url:
            raise JenkinsError("Jenkins nie zwrócił adresu elementu kolejki (brak nagłówka Location)")
        return queue_url.rstrip("/")

    def wait_for_build(self, queue_url, poll_interval=5, max_wait=1800):
        """Czeka, aż build opuści kolejkę i się zakończy. Zwraca dane buildu."""
        deadline = time.monotonic() + max_wait

        # 1. Kolejka → numer buildu
        build_url = None
        while build_url is None:
            if time.monotonic() > deadline:
                raise JenkinsError("Build nie wystartował w wyznaczonym czasie")
            item = self._get_json(f"{queue_url}/api/json")
            if item.get("cancelled"):
                raise JenkinsError("Build został anulowany w kolejce")
            if item.get("executable"):
                build_url = item["executable"]["url"].rstrip("/")
                print(f"Build wystartował: {build_url}")
            else:
                print(f"W kolejce: {item.get('why') or 'oczekiwanie na agenta'}")
                time.sleep(poll_interval)

        # 2. Build → wynik
        while True:
            if time.monotonic() > deadline:
                raise JenkinsError(f"Build nie zakończył się w wyznaczonym czasie: {build_url}")
            build = self._get_json(f"{build_url}/api/json",
                                   params={"tree": "number,result,building,duration,url"})
            if not build.get("building"):
                return build
            time.sleep(poll_interval)


# ------------------------------------------------------------------ prezentacja

STATUS_ICONS = {"SUCCESS": "✅", "FAILURE": "❌", "UNSTABLE": "⚠️", "ABORTED": "⏹️", "NOT_BUILT": "⏸️"}


def describe_last_build(job):
    build = job.get("lastBuild")
    if not build:
        return "⚪ brak buildów"
    if build.get("building"):
        return f"🔄 #{build['number']} w trakcie"
    result = build.get("result") or "UNKNOWN"
    started = datetime.fromtimestamp(build["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M")
    duration = round(build.get("duration", 0) / 1000)
    return f"{STATUS_ICONS.get(result, '❔')} #{build['number']} {result} ({started}, {duration} s)"


def job_name(job):
    return job.get("fullName") or job["name"]


def cmd_list(client, _args):
    jobs = client.list_jobs()
    if not jobs:
        print("Brak zadań.")
        return
    for job in sorted(jobs, key=job_name):
        print(job_name(job))
    print(f"\nRazem: {len(jobs)}")


def cmd_status(client, args):
    jobs = [client.get_job_status(args.job)] if args.job else client.list_jobs()
    width = max((len(job_name(j)) for j in jobs), default=0)
    for job in sorted(jobs, key=job_name):
        print(f"{job_name(job):<{width}}  {describe_last_build(job)}")


def parse_params(raw_params):
    params = {}
    for item in raw_params or []:
        key, sep, value = item.partition("=")
        if not sep or not key:
            raise JenkinsError(f"Parametr musi mieć postać KLUCZ=WARTOŚĆ, otrzymano: {item!r}")
        params[key] = value
    return params


def cmd_build(client, args):
    queue_url = client.trigger_build(args.job, parse_params(args.param))
    print(f"Zadanie {args.job} dodane do kolejki: {queue_url}")
    if not args.wait:
        return 0
    build = client.wait_for_build(queue_url)
    result = build.get("result")
    print(f"Wynik: {STATUS_ICONS.get(result, '❔')} {result} ({round(build.get('duration', 0) / 1000)} s)")
    # Kod wyjścia ≠ 0 przy nieudanym buildzie – przydatne w skryptach i innych pipeline'ach
    return 0 if result == "SUCCESS" else 1


# ------------------------------------------------------------------------ main

def main():
    parser = argparse.ArgumentParser(description="Klient Jenkins REST API")
    parser.add_argument("--insecure", action="store_true", help="nie weryfikuj certyfikatu SSL (tylko do testów)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="wylistuj wszystkie zadania")

    p_status = sub.add_parser("status", help="status ostatnich buildów")
    p_status.add_argument("job", nargs="?", help="pełna nazwa zadania, np. folder/zadanie (domyślnie wszystkie)")

    p_build = sub.add_parser("build", help="uruchom zadanie")
    p_build.add_argument("job", help="pełna nazwa zadania, np. folder/zadanie")
    p_build.add_argument("--param", action="append", metavar="KLUCZ=WARTOŚĆ", help="parametr buildu (można powtarzać)")
    p_build.add_argument("--wait", action="store_true", help="czekaj na zakończenie buildu")

    args = parser.parse_args()

    # Dane logowania tylko ze zmiennych środowiskowych – nie w kodzie ani w argumentach,
    # które trafiają do historii powłoki i listy procesów
    config = {name: os.environ.get(name) for name in ("JENKINS_URL", "JENKINS_USER", "JENKINS_TOKEN")}
    missing = [name for name, value in config.items() if not value]
    if missing:
        print(f"Brak zmiennych środowiskowych: {', '.join(missing)}", file=sys.stderr)
        return 2

    client = JenkinsClient(config["JENKINS_URL"], config["JENKINS_USER"], config["JENKINS_TOKEN"],
                           verify_ssl=not args.insecure)
    commands = {"list": cmd_list, "status": cmd_status, "build": cmd_build}

    try:
        return commands[args.command](client, args) or 0
    except JenkinsError as exc:
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nPrzerwano.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
