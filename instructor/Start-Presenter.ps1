<#
.SYNOPSIS
Open the current presenter guide from this course checkout.
.DESCRIPTION
Starts a hidden loopback server only when the port is available. An existing
listener is accepted only if its HTML and revision match this checkout's file.
Private neighbors are never served. Use -NoBrowser for automated verification.
.EXAMPLE
.\instructor\Start-Presenter.ps1
#>
[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)][int]$Port = 8768,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
$courseRoot = Split-Path $PSScriptRoot -Parent
$document = Join-Path $PSScriptRoot '2026-10-pearson/Context-Engineering-All-Demos-v2.html'
$server = Join-Path $courseRoot 'scripts/Serve-PresenterRunbook.py'
if (-not (Test-Path -LiteralPath $document -PathType Leaf)) { throw "Presenter guide is missing: $document" }
$expected = (Get-FileHash -LiteralPath $document -Algorithm SHA256).Hash.ToLowerInvariant()
$url = "http://127.0.0.1:$Port/"

function Test-PresenterIdentity {
    # A successful connection alone can hide an obsolete server or another application.
    $response = Invoke-WebRequest -Uri $url -TimeoutSec 5
    $body = $response.RawContentStream.ToArray()
    $actual = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($body)).ToLowerInvariant()
    $revision = (Invoke-RestMethod -Uri "${url}__version" -TimeoutSec 5).revision
    if ($actual -ne $expected -or $revision -ne $expected) {
        throw "Port $Port serves a different document. Stop that presenter server before restarting from this checkout."
    }
}

$probe = [Net.Sockets.TcpClient]::new()
try {
    try { $probe.Connect('127.0.0.1', $Port); $occupied = $true }
    catch [Net.Sockets.SocketException] { $occupied = $false }
} finally { $probe.Dispose() }

if ($occupied) {
    Test-PresenterIdentity
} else {
    $python = (Get-Command python -ErrorAction Stop).Source
    $logDirectory = Join-Path $courseRoot '.local/presenter-server'
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    # Quoted path arguments support a checkout whose parent directory contains spaces.
    $process = Start-Process -FilePath $python -WindowStyle Hidden -PassThru `
        -ArgumentList @(('"{0}"' -f $server), '--file', ('"{0}"' -f $document), '--port', $Port) `
        -RedirectStandardOutput (Join-Path $logDirectory 'stdout.log') `
        -RedirectStandardError (Join-Path $logDirectory 'stderr.log')
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ($process.HasExited) { throw "Presenter server exited. Inspect $logDirectory\stderr.log" }
        try { Test-PresenterIdentity; $ready = $true; break }
        catch { Start-Sleep -Milliseconds 100 }
    }
    if (-not $ready) { throw "Presenter server didn't become ready. Inspect $logDirectory\stderr.log" }
    $process.Id | Set-Content -LiteralPath (Join-Path $logDirectory 'process-id.txt')
}
Write-Output "Presenter: $url"
Write-Output "File: $document"
Write-Output "SHA256 verified: $expected"
if (-not $NoBrowser) { Start-Process $url }
