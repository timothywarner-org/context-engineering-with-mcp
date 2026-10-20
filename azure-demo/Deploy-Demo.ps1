<#
.SYNOPSIS
Deploy the isolated classroom MCP API using existing Azure infrastructure.
.DESCRIPTION
Builds only the course server and lock file. Reuses an existing Container Apps
environment, registry pull identity, and APIM instance. Never updates the
Schematica application, its API, or subscription-wide settings.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SubscriptionId,
    [Parameter(Mandatory)][string]$TenantId,
    [Parameter(Mandatory)][string]$ResourceGroup,
    [Parameter(Mandatory)][string]$ApimName,
    [Parameter(Mandatory)][string]$EnvironmentName,
    [Parameter(Mandatory)][string]$RegistryName,
    [Parameter(Mandatory)][string]$PullIdentityName,
    [switch]$SkipBuild
)
$ErrorActionPreference = 'Stop'
$apiId = 'warnerco-class-mcp'
$appName = 'warnerco-class-mcp'
$owner = 'Context Engineering classroom MCP demo'
$repoRoot = Split-Path $PSScriptRoot -Parent
$localDir = Join-Path $PSScriptRoot '.local'
New-Item -ItemType Directory -Path $localDir -Force | Out-Null

function Invoke-AzureCli {
    <# .SYNOPSIS
    Stop at a failed CLI operation instead of deploying with an empty identifier.
    #>
    param([string[]]$Arguments)
    $result = & az @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Azure CLI failed: $($Arguments[0]) $($Arguments[1])" }
    return $result
}

$account = Invoke-AzureCli @('account', 'show', '--subscription', $SubscriptionId, '-o', 'json') |
    ConvertFrom-Json
if ($account.tenantId -ne $TenantId -or $account.state -ne 'Enabled') {
    throw 'The requested subscription is not enabled in the expected tenant.'
}
$armToken = Invoke-AzureCli @(
    'account', 'get-access-token', '--subscription', $SubscriptionId,
    '--resource', 'https://management.azure.com/',
    '--query', 'accessToken', '-o', 'tsv'
)
$armHeaders = @{Authorization = "Bearer $armToken"; Accept = 'application/json'}
$groupId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup"
$apimId = "$groupId/providers/Microsoft.ApiManagement/service/$ApimName"
$environmentId = "$groupId/providers/Microsoft.App/managedEnvironments/$EnvironmentName"
$pullIdentityId = "$groupId/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$PullIdentityName"

function Invoke-Arm {
    <# .SYNOPSIS
    Send an authenticated ARM request without printing credentials or response bodies.
    #>
    param([string]$Method, [string]$ResourceId, [string]$Version, $Body)
    $parameters = @{
        Method = $Method
        Uri = "https://management.azure.com${ResourceId}?api-version=$Version"
        Headers = $armHeaders
        ContentType = 'application/json'
    }
    if ($null -ne $Body) { $parameters.Body = $Body | ConvertTo-Json -Depth 30 -Compress }
    if ($Method -eq 'PUT') {
        # Explicit upsert semantics allow a rerun to repair this demo's own resources.
        $parameters.Headers = $armHeaders.Clone()
        $parameters.Headers['If-Match'] = '*'
    }
    Invoke-RestMethod @parameters
}

$environment = Invoke-Arm GET $environmentId '2025-01-01'
$registry = Invoke-Arm GET "$groupId/providers/Microsoft.ContainerRegistry/registries/$RegistryName" '2025-04-01'
$null = Invoke-Arm GET $pullIdentityId '2024-11-30'
$null = Invoke-Arm GET $apimId '2024-05-01'

# Persist the shared backend credential with Windows DPAPI, never as plaintext in Git.
$credentialPath = Join-Path $localDir 'backend-key.clixml'
if (Test-Path -LiteralPath $credentialPath) {
    $credential = Import-Clixml -LiteralPath $credentialPath
    $backendKey = $credential.GetNetworkCredential().Password
} else {
    $backendKey = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    $credential = [pscredential]::new(
        'warnerco-class-backend', (ConvertTo-SecureString $backendKey -AsPlainText -Force)
    )
    $credential | Export-Clixml -LiteralPath $credentialPath
}

$buildInputs = @('azure-demo/server.py', 'azure-demo/Dockerfile', 'python/pyproject.toml', 'python/uv.lock')
# A dependency or Dockerfile change needs a new tag even when the tool code is unchanged.
$inputHashes = foreach ($inputPath in $buildInputs) {
    (Get-FileHash -LiteralPath (Join-Path $repoRoot $inputPath) -Algorithm SHA256).Hash
}
$buildHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData(
    [Text.Encoding]::UTF8.GetBytes(($inputHashes -join "`n"))
)).ToLower()
$imageTag = "warnerco-class-mcp:$($buildHash.Substring(0,12))"
if (-not $SkipBuild) {
    # Limit the remote build context to reviewed source files, excluding local state and secrets.
    $buildDir = Join-Path $localDir "build-$($buildHash.Substring(0,12))"
    New-Item -ItemType Directory -Path (Join-Path $buildDir 'python'), (Join-Path $buildDir 'azure-demo') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot 'python/pyproject.toml'), (Join-Path $repoRoot 'python/uv.lock') -Destination (Join-Path $buildDir 'python')
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'server.py'), (Join-Path $PSScriptRoot 'Dockerfile') -Destination (Join-Path $buildDir 'azure-demo')
    Invoke-AzureCli @(
        'acr', 'build', '--subscription', $SubscriptionId, '--registry', $RegistryName,
        '--image', $imageTag, '--file', 'azure-demo/Dockerfile', '--platform', 'linux/amd64',
        '--only-show-errors', $buildDir
    ) | Write-Host
} else {
    # Fail before updating ACA if SkipBuild refers to an image that was never built.
    $null = Invoke-AzureCli @(
        'acr', 'repository', 'show', '--subscription', $SubscriptionId,
        '--name', $RegistryName, '--image', $imageTag, '--only-show-errors', '-o', 'json'
    )
}
$image = "$($registry.properties.loginServer)/$imageTag"
$application = @{
    location = $environment.location
    tags = @{Purpose = $owner; ManagedBy = 'Deploy-Demo.ps1'}
    identity = @{type = 'UserAssigned'; userAssignedIdentities = @{$pullIdentityId = @{}}}
    properties = @{
        managedEnvironmentId = $environmentId
        workloadProfileName = 'Consumption'
        configuration = @{
            activeRevisionsMode = 'Single'
            secrets = @(@{name = 'backend-key'; value = $backendKey})
            registries = @(@{server = $registry.properties.loginServer; identity = $pullIdentityId})
            ingress = @{external = $true; targetPort = 8000; transport = 'http'; allowInsecure = $false}
        }
        template = @{
            containers = @(@{
                name = 'mcp'; image = $image
                resources = @{cpu = 0.25; memory = '0.5Gi'}
                env = @(@{name = 'WARNERCO_BACKEND_KEY'; secretRef = 'backend-key'})
                probes = @(
                    @{type = 'Readiness'; httpGet = @{path = '/health'; port = 8000}; initialDelaySeconds = 5; periodSeconds = 10}
                    @{type = 'Liveness'; httpGet = @{path = '/health'; port = 8000}; initialDelaySeconds = 10; periodSeconds = 20}
                )
            })
            scale = @{minReplicas = 0; maxReplicas = 1; rules = @(
                @{name = 'http'; http = @{metadata = @{concurrentRequests = '10'}}}
            )}
        }
    }
}
$appId = "$groupId/providers/Microsoft.App/containerApps/$appName"
$app = Invoke-Arm PUT $appId '2025-01-01' $application
# ARM accepts creation before ingress exists; wait for the resource, not a fixed delay.
$deadline = [DateTime]::UtcNow.AddMinutes(5)
while ($app.properties.provisioningState -ne 'Succeeded' -or -not $app.properties.configuration.ingress.fqdn) {
    if ($app.properties.provisioningState -in @('Failed', 'Canceled')) {
        throw "Container App provisioning ended with $($app.properties.provisioningState)."
    }
    if ([DateTime]::UtcNow -ge $deadline) { throw 'Container App provisioning exceeded five minutes.' }
    Write-Host "Waiting for Container App provisioning: $($app.properties.provisioningState)"
    Start-Sleep -Seconds 10
    $app = Invoke-Arm GET $appId '2025-01-01'
}
$fqdn = $app.properties.configuration.ingress.fqdn

$null = Invoke-Arm PUT "$apimId/namedValues/warnerco-class-backend-key" '2024-05-01' @{
    properties = @{displayName = 'warnerco-class-backend-key'; secret = $true; value = $backendKey}
}
foreach ($route in @('catalog', 'incidents', 'runbooks')) {
    $null = Invoke-Arm PUT "$apimId/backends/warnerco-class-$route" '2024-05-01' @{
        properties = @{
            title = "$owner - $route"
            description = $owner
            protocol = 'http'
            url = "https://$fqdn/$route"
        }
    }
}

# The native MCP API retains MCP discovery; policy selects the execution backend per tool.
$api = @{
    properties = @{
        type = 'mcp'; path = 'class-mcp'; displayName = 'WARNERCO classroom MCP'
        description = $owner; protocols = @('https'); subscriptionRequired = $true
        backendId = 'warnerco-class-catalog'
        mcpProperties = @{
            # This service's live ARM contract requires a dictionary, unlike the current Learn example.
            endpoints = @{mcp = @{uriTemplate = '/mcp'}}
        }
    }
}
$null = Invoke-Arm PUT "$apimId/apis/$apiId" '2025-09-01-preview' $api
$observedApi = Invoke-Arm GET "$apimId/apis/$apiId" '2025-09-01-preview'
if ($observedApi.properties.backendId -ne 'warnerco-class-catalog') {
    throw 'The MCP API did not retain the catalog backend binding.'
}
$policy = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'policy.xml') -Raw
$null = Invoke-Arm PUT "$apimId/apis/$apiId/policies/policy" '2025-09-01-preview' @{
    properties = @{format = 'rawxml'; value = $policy}
}
$null = Invoke-Arm PUT "$apimId/subscriptions/warnerco-class-presenter" '2024-05-01' @{
    properties = @{
        displayName = 'WARNERCO classroom presenter'
        scope = "/apis/$apiId"
        state = 'active'
        allowTracing = $false
    }
}
$deployment = @{
    subscriptionId = $SubscriptionId; tenantId = $TenantId; resourceGroup = $ResourceGroup
    apimName = $ApimName; apiId = $apiId; appName = $appName
    backendUrl = "https://$fqdn"; gatewayUrl = "https://$ApimName.azure-api.net/class-mcp/mcp"
    image = $image; updatedAt = [DateTime]::UtcNow.ToString('o')
}
$deployment | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $localDir 'deployment.json')
$backendKey = $null
$armToken = $null
$deployment | ConvertTo-Json
