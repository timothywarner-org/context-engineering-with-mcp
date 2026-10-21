#Requires -Version 7.0
<#
.SYNOPSIS
Generate portable launch snippets for the incident server and optional memory server.
.DESCRIPTION
Writes snippets only. Never replaces a host configuration or unrelated server entry.
.PARAMETER OutputDirectory
Folder receiving VS Code, portable Copilot, Claude Code, Claude Desktop and Inspector JSON.
.PARAMETER IncludeMemory
Include the built memory-mcp server. Omit for the original Python-only first example.
.PARAMETER MemoryPath
Absolute JSON data path shared by independently launched memory server processes.
#>
[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'generated'),
    [switch]$IncludeMemory,
    [string]$MemoryPath
)
$ErrorActionPreference = 'Stop'
try {
    $courseRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    $uvPath = (Get-Command uv -ErrorAction Stop).Source
    $serverDirectory = Join-Path $courseRoot 'python'
    # Absolute executables and scripts remove GUI working-directory/PATH assumptions.
    $incident = [ordered]@{command=$uvPath; args=@('run','--locked','--project',$serverDirectory,'python',(Join-Path $serverDirectory 'server.py'))}
    $entries = [ordered]@{'warnerco-incidents'=$incident}
    if ($IncludeMemory) {
        $nodePath = (Get-Command node -ErrorAction Stop).Source
        $memoryServer = Join-Path $courseRoot 'memory-mcp/dist/server.js'
        if (-not (Test-Path -LiteralPath $memoryServer -PathType Leaf)) {
            throw 'Build memory-mcp before generating its launch configuration.'
        }
        if (-not $MemoryPath) { $MemoryPath = Join-Path $courseRoot '.local/memory/warnerco.json' }
        if (-not [System.IO.Path]::IsPathFullyQualified($MemoryPath)) {
            throw 'MemoryPath must be an absolute file path.'
        }
        $entries['warnerco-memory'] = [ordered]@{
            command=$nodePath; args=@($memoryServer)
            env=[ordered]@{WARNERCO_MEMORY_PATH=[System.IO.Path]::GetFullPath($MemoryPath)}
        }
    }
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $vscode=[ordered]@{}; $inspector=[ordered]@{}; $portable=[ordered]@{}
    foreach ($name in $entries.Keys) {
        $vscode[$name]=[ordered]@{type='stdio'}
        $portable[$name]=[ordered]@{type='stdio'}
        # Inspector's protocol-era setting must not leak into host snippets.
        $inspector[$name]=[ordered]@{protocolEra='modern'}
        foreach ($key in $entries[$name].Keys) {
            $vscode[$name][$key]=$entries[$name][$key]
            $portable[$name][$key]=$entries[$name][$key]
            $inspector[$name][$key]=$entries[$name][$key]
        }
    }
    [ordered]@{servers=$vscode} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'vscode-mcp.json') -Encoding utf8
    $shared=[ordered]@{mcpServers=$portable} | ConvertTo-Json -Depth 8
    foreach ($file in @('claude-code.mcp.json','claude-desktop.json','copilot-mcp.json')) {
        Set-Content -LiteralPath (Join-Path $OutputDirectory $file) -Value $shared -Encoding utf8
    }
    [ordered]@{mcpServers=$inspector} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'inspector.json') -Encoding utf8
    Write-Output "Generated snippets in $OutputDirectory. Merge only the named WARNERCO entries; preserve unrelated settings."
} catch { Write-Error "Client configuration generation failed: $_" -ErrorAction Continue; exit 1 }
