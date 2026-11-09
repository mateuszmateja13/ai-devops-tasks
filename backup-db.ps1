#Requires -Version 5.1
# Backup bazy MySQL z kompresją GZip, weryfikacją i rotacją starych kopii (Windows)
$ErrorActionPreference = 'Stop'   # każdy błąd cmdletu przerywa skrypt

$DbName        = 'app_database'
$BackupDir     = 'C:\Backups\db'
$RetentionDays = 7
$CnfFile       = 'C:\ProgramData\MySQL\backup.cnf'  # [client] user=... password=...
$MysqlDump     = 'mysqldump.exe'                     # lub pełna ścieżka do pliku
$Date          = Get-Date -Format 'yyyyMMdd_HHmmss'
$SqlFile       = Join-Path $BackupDir "${DbName}_$Date.sql"
$GzFile        = "$SqlFile.gz"

function Write-Log {
    param([string]$Message)
    Write-Output "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
}

try {
    # Odpowiednik mkdir -p (nie zgłasza błędu, gdy katalog istnieje)
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

    Write-Log "Rozpoczynam backup bazy $DbName..."
    # --result-file zapisuje bajty bezpośrednio na dysk, z pominięciem potoku PowerShella
    & $MysqlDump "--defaults-extra-file=$CnfFile" --single-transaction `
        --routines --triggers "--result-file=$SqlFile" $DbName
    if ($LASTEXITCODE -ne 0) { throw "mysqldump zakończył się kodem $LASTEXITCODE" }

    # Kompresja GZip – odpowiednik | gzip
    $in  = [System.IO.File]::OpenRead($SqlFile)
    $out = [System.IO.File]::Create($GzFile)
    $gz  = New-Object System.IO.Compression.GZipStream($out, [System.IO.Compression.CompressionMode]::Compress)
    try { $in.CopyTo($gz) } finally { $gz.Dispose(); $out.Dispose(); $in.Dispose() }
    Remove-Item $SqlFile

    # Test integralności – odpowiednik gzip -t
    $test = New-Object System.IO.Compression.GZipStream(
        [System.IO.File]::OpenRead($GzFile),
        [System.IO.Compression.CompressionMode]::Decompress)
    try { $test.CopyTo([System.IO.Stream]::Null) } finally { $test.Dispose() }

    $sizeMb = '{0:N1} MB' -f ((Get-Item $GzFile).Length / 1MB)
    Write-Log "Backup zakończony sukcesem: $GzFile ($sizeMb)"

    # Rotacja – odpowiednik find -mtime +N -delete
    $limit = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem -Path $BackupDir -Filter "${DbName}_*.sql.gz" |
        Where-Object { $_.LastWriteTime -lt $limit } |
        Remove-Item
    Write-Log "Usunięto backupy starsze niż $RetentionDays dni"
}
catch {
    # Odpowiednik trap cleanup EXIT: usuń niepełne pliki i zwróć kod błędu
    Remove-Item $SqlFile, $GzFile -ErrorAction SilentlyContinue
    $Host.UI.WriteErrorLine("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] BŁĄD: $($_.Exception.Message)")
    exit 1
}
