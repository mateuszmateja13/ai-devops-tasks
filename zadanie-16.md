# Zadanie 16 – Konwersja skryptu backupu z Bash do PowerShell

## Pliki

| Plik | Zawartość |
|------|-----------|
| `backup-db.sh` | Oryginalny skrypt Bash wykonujący backup bazy MySQL (`mysqldump` + `gzip`) |
| `backup-db.ps1` | Równoważny skrypt PowerShell dla Windows |

Wersja PowerShell powstała na podstawie poprawionego wariantu skryptu Bash. Usuwa ona błędy oryginału: niewykrywanie awarii `mysqldump` w potoku (brak `pipefail`), interaktywne pytanie o hasło (`-p`), brak sprzątania niepełnego pliku i brak rotacji starych kopii. Dodatkowo sprawdza integralność archiwum.

## Główne różnice między Bash i PowerShell

| Obszar | Bash | PowerShell |
|--------|------|------------|
| Model danych w potoku | Strumień bajtów/tekstu | Obiekty .NET (np. `FileInfo`) |
| Obsługa błędów | Kody wyjścia, `$?`, `set -euo pipefail`, `trap ... EXIT` | Wyjątki, `$ErrorActionPreference = 'Stop'`, `try/catch/finally` |
| Kod wyjścia programu zewnętrznego | `$?` (w potoku – kod **ostatniego** polecenia) | `$LASTEXITCODE` |
| Zmienne | `NAZWA="wartość"`, odwołanie `$NAZWA` | `$Nazwa = 'wartość'` |
| Interpolacja | `"${DB_NAME}_${DATE}"` | `"${DbName}_$Date"`, wyrażenia przez `$(...)` |
| Data | `date +%Y%m%d_%H%M%S` | `Get-Date -Format 'yyyyMMdd_HHmmss'` |
| Tworzenie katalogu | `mkdir -p` | `New-Item -ItemType Directory -Force` |
| Ścieżki | Łączenie tekstu z `/` | `Join-Path`, separator `\` |
| Kompresja | Narzędzie systemowe `gzip` | Klasa .NET `System.IO.Compression.GZipStream` |
| Test archiwum | `gzip -t` | Dekompresja do `[System.IO.Stream]::Null` |
| Rotacja kopii | `find -mtime +N -delete` | `Get-ChildItem \| Where-Object { $_.LastWriteTime ... } \| Remove-Item` |
| Wypisywanie | `echo`, błędy przez `>&2` | `Write-Output`, `$Host.UI.WriteErrorLine` |
| Funkcje | `log() { ...; }`, argumenty `$*` | `function Write-Log { param(...) }` z nazwanymi parametrami |
| Kontynuacja linii | `\` | backtick `` ` `` lub zakończenie linii operatorem (`\|`) |
| Uprawnienia plików | `umask 077` w skrypcie | ACL katalogu (`icacls`), dziedziczone przez pliki |
| Harmonogram | `cron` | Harmonogram zadań Windows |

## Najważniejsze obserwacje

**1. Potok tekstowy kontra potok obiektowy.** W Bashu `mysqldump | gzip` przekazuje surowe bajty między procesami, co jest naturalne i wydajne. W Windows PowerShell 5.1 wyjście programu zewnętrznego trafia do potoku jako tekst (linie łańcuchów), co może zmienić kodowanie i znaki końca linii w zrzucie SQL. Dlatego wersja PowerShell zapisuje zrzut bezpośrednio przez `mysqldump --result-file`, a dopiero potem kompresuje plik. Z drugiej strony potok obiektowy upraszcza filtrowanie plików przy rotacji – `Where-Object` operuje na właściwości `LastWriteTime` zamiast parsować wyniki tekstowe.

**2. Obsługa błędów.** Bash domyślnie kontynuuje działanie po błędzie, a `$?` po potoku zwraca kod ostatniego polecenia (`gzip`), więc oryginalny skrypt raportował sukces nawet przy nieudanym `mysqldump`. PowerShell opiera się na wyjątkach i bloku `try/catch`, ale dla programów zewnętrznych nadal trzeba ręcznie sprawdzić `$LASTEXITCODE` – `$ErrorActionPreference = 'Stop'` dotyczy tylko cmdletów.

**3. Zależność od narzędzi systemu kontra platforma .NET.** Bash składa rozwiązanie z małych narzędzi (`gzip`, `find`, `du`, `date`). PowerShell ma dostęp do bibliotek .NET, dzięki czemu kompresja i weryfikacja nie wymagają instalowania dodatkowego oprogramowania, kosztem dłuższego kodu.

**4. Czytelność i konwencje.** PowerShell stosuje konwencję `Czasownik-Rzeczownik` (`Get-ChildItem`, `Remove-Item`) i nazwane parametry, co czyni kod bardziej opisowym. Bash jest zwięźlejszy, ale wymaga znajomości flag poszczególnych narzędzi (`-mtime`, `-p`, `-t`).

**5. Środowisko uruchomieniowe.** Odpowiednikiem `cron` jest Harmonogram zadań z akcją `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Scripts\backup-db.ps1`. Uprawnienia do plików backupu w Windows ustawia się przez ACL katalogu (`icacls`), a nie przez `umask` wewnątrz skryptu.
