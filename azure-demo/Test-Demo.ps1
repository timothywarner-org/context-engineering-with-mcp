<#
.SYNOPSIS
Run the live MCP routing and policy demonstration without displaying credentials.
.DESCRIPTION
Reads the deployment receipt, obtains this API's presenter subscription key
through ARM, and passes it only through the child process environment.
Requires the same signed-in Azure tenant and permission to read subscription keys.
#>
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$receipt = Join-Path $PSScriptRoot '.local/deployment.json'
if (-not (Test-Path -LiteralPath $receipt)) { throw 'Deploy the demonstration before running its live checks.' }
$deployment = Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
$account = az account show --subscription $deployment.subscriptionId --output json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $account.tenantId -ne $deployment.tenantId) {
    throw 'Azure subscription and tenant verification failed.'
}
$token = az account get-access-token --subscription $deployment.subscriptionId `
    --resource 'https://management.azure.com/' --query accessToken --output tsv
if ($LASTEXITCODE -ne 0) { throw 'Could not obtain the ARM token.' }
$resource = "/subscriptions/$($deployment.subscriptionId)/resourceGroups/$($deployment.resourceGroup)"
$resource += "/providers/Microsoft.ApiManagement/service/$($deployment.apimName)"
$resource += '/subscriptions/warnerco-class-presenter/listSecrets'
$keys = Invoke-RestMethod -Method Post `
    -Uri "https://management.azure.com${resource}?api-version=2024-05-01" `
    -Headers @{Authorization = "Bearer $token"}
$previous = @{
    WARNERCO_GATEWAY_URL = $env:WARNERCO_GATEWAY_URL
    WARNERCO_BACKEND_URL = $env:WARNERCO_BACKEND_URL
    WARNERCO_APIM_KEY = $env:WARNERCO_APIM_KEY
}
try {
    # Environment inheritance keeps the key out of command history and process arguments.
    $env:WARNERCO_GATEWAY_URL = $deployment.gatewayUrl
    $env:WARNERCO_BACKEND_URL = $deployment.backendUrl
    $env:WARNERCO_APIM_KEY = $keys.primaryKey
    & uv run --locked --project (Join-Path $repoRoot 'python') python `
        (Join-Path $PSScriptRoot 'verify_demo.py') `
        --output (Join-Path $PSScriptRoot '.local/live-verification.json')
    if ($LASTEXITCODE -ne 0) { throw 'Live gateway verification failed. Inspect the sanitized local report.' }
} finally {
    foreach ($name in $previous.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process')
    }
    $token = $null
    $keys = $null
}
