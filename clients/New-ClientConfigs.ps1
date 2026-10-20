<#
.SYNOPSIS
Generate client configuration files for wherever this repository lives on disk.
.DESCRIPTION
Writes to a chosen output folder. It never edits a user's existing client configuration.
.PARAMETER OutputDirectory
Folder receiving the VS Code, Claude Code, Claude Desktop, and Inspector snippets.
#>
[CmdletBinding()]
param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'generated'))
$ErrorActionPreference = 'Stop'
try {
    $courseRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    $uvPath = (Get-Command uv -ErrorAction Stop).Source
    $serverDirectory = Join-Path $courseRoot 'python'
    # Explicit paths remove dependence on the GUI application's working directory or PATH.
    $entry = @{ command=$uvPath; args=@('run','--project',$serverDirectory,'python',(Join-Path $serverDirectory 'server.py')) }
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    @{servers=@{'warnerco-incidents'=(@{type='stdio'}+$entry)}} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'vscode-mcp.json') -Encoding utf8
    $shared = @{mcpServers=@{'warnerco-incidents'=$entry}} | ConvertTo-Json -Depth 6
    foreach($file in @('claude-code.mcp.json','claude-desktop.json')) {
        Set-Content -LiteralPath (Join-Path $OutputDirectory $file) -Value $shared -Encoding utf8
    }
    # Inspector defaults to the legacy handshake unless its own entry selects the modern era.
    @{mcpServers=@{'warnerco-incidents'=(@{protocolEra='modern'}+$entry)}} |
        ConvertTo-Json -Depth 6 |
        Set-Content -LiteralPath (Join-Path $OutputDirectory 'inspector.json') -Encoding utf8
    Write-Output "Generated configuration snippets in $OutputDirectory. Merge only the named server into each existing client configuration."
} catch { Write-Error "Client configuration generation failed: $_"; exit 1 }
