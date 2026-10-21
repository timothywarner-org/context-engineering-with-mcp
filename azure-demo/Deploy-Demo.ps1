<#
.SYNOPSIS
Deploy the isolated classroom MCP API using existing Azure infrastructure.
.DESCRIPTION
Builds only the course server and lock file. Reuses an existing Container Apps
environment, registry pull identity, and APIM instance. Never updates the
Schematica application, its API, or subscription-wide settings.
.PARAMETER SkipBuild
Require the content-addressed image to exist; do not build it.
.PARAMETER Rebuild
Rebuild even when this environment's receipt already identifies the same image.
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
    [switch]$SkipBuild,
    [switch]$Rebuild
)
$ErrorActionPreference = 'Stop'
$apiId = 'warnerco-class-mcp'
$appName = 'warnerco-class-mcp'
$owner = 'Context Engineering classroom MCP demo'
$repoRoot = Split-Path $PSScriptRoot -Parent
$localDir = Join-Path $PSScriptRoot '.local'
New-Item -ItemType Directory -Path $localDir -Force | Out-Null
if ($SkipBuild -and $Rebuild) { throw 'Choose SkipBuild or Rebuild, not both.' }

# Serialize this checkout's credential, build, and receipt updates across terminal sessions.
$leasePath = Join-Path $localDir 'deployment.lock'
try {
    $deploymentLease = [IO.File]::Open($leasePath, [IO.FileMode]::OpenOrCreate,
        [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
} catch [IO.IOException] {
    throw 'Another deployment holds this checkout''s deployment lease, or the lock file is unavailable. Wait for it to finish before retrying.'
}
try {

function Write-AtomicLocalFile {
    <# .SYNOPSIS
    Replace local state only after its complete contents have been written.
    #>
    param([string]$Path, [scriptblock]$Write)
    $temporary = "$Path.$([Guid]::NewGuid().ToString('N')).tmp"
    try {
        & $Write $temporary
        # A same-directory rename prevents an interrupted write from truncating saved state.
        [IO.File]::Move($temporary, $Path, $true)
    } finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
    }
}

$deploymentPath = Join-Path $localDir 'deployment.json'
$scopePath = Join-Path $localDir 'deployment-scope.json'
$credentialPath = Join-Path $localDir 'backend-key.clixml'
$scope = [ordered]@{
    subscriptionId = $SubscriptionId; tenantId = $TenantId; resourceGroup = $ResourceGroup
    apimName = $ApimName; environmentName = $EnvironmentName
    registryName = $RegistryName; pullIdentityName = $PullIdentityName
}
$previousDeployment = $null
if (Test-Path -LiteralPath $deploymentPath) {
    $previousDeployment = Get-Content -LiteralPath $deploymentPath -Raw | ConvertFrom-Json
    foreach ($name in @('subscriptionId', 'tenantId', 'resourceGroup', 'apimName')) {
        if ($previousDeployment.$name -ne $scope[$name]) {
            throw "Existing deployment receipt belongs to a different $name. Use this course home's recorded environment parameters; do not repoint its saved credentials."
        }
    }
    if (-not (Test-Path -LiteralPath $credentialPath)) {
        throw 'Existing deployment receipt has no backend credential. Restore its credential before redeploying.'
    }
}
if (Test-Path -LiteralPath $scopePath) {
    $savedScope = Get-Content -LiteralPath $scopePath -Raw | ConvertFrom-Json
    foreach ($name in $scope.Keys) {
        if ($savedScope.$name -ne $scope[$name]) {
            throw "Saved backend credential scope differs at $name. Use this course home's recorded environment parameters; do not repoint its saved credentials."
        }
    }
} elseif ((Test-Path -LiteralPath $credentialPath) -and -not $previousDeployment) {
    throw 'An unscoped backend credential exists without a deployment receipt. Restore its matching receipt before redeploying.'
}

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

# Legacy receipts predate the scope file; confirm their registry before binding the credential.
if ($previousDeployment -and -not $previousDeployment.image.StartsWith(
    "$($registry.properties.loginServer)/", [StringComparison]::OrdinalIgnoreCase
)) { throw 'Existing deployment receipt belongs to a different registry.' }

function Get-ExistingArmResource {
    <# .SYNOPSIS
    Treat only a confirmed 404 as absence, never an authorization or network failure.
    #>
    param([string]$ResourceId, [string]$Version)
    try { Invoke-Arm GET $ResourceId $Version }
    catch {
        if ($_.Exception.Response.StatusCode -eq 404) { return $null }
        throw
    }
}

$appId = "$groupId/providers/Microsoft.App/containerApps/$appName"
$existingApp = Get-ExistingArmResource $appId '2025-01-01'
if ($existingApp -and ($existingApp.tags.Purpose -ne $owner -or
    $existingApp.tags.ManagedBy -ne 'Deploy-Demo.ps1' -or
    $existingApp.properties.managedEnvironmentId -ne $environmentId)) {
    throw 'The named Container App belongs to another owner or environment; refusing to overwrite it.'
}
$existingApi = Get-ExistingArmResource "$apimId/apis/$apiId" '2025-09-01-preview'
if ($existingApi -and $existingApi.properties.description -ne $owner) {
    throw 'The named APIM API belongs to another owner; refusing to overwrite it.'
}
foreach ($route in @('catalog', 'incidents', 'runbooks')) {
    $existingBackend = Get-ExistingArmResource "$apimId/backends/warnerco-class-$route" '2024-05-01'
    if ($existingBackend -and $existingBackend.properties.description -ne $owner) {
        throw 'A named APIM backend belongs to another owner; refusing to overwrite it.'
    }
}
Write-AtomicLocalFile $scopePath { param($path) $scope | ConvertTo-Json | Set-Content -LiteralPath $path }

# Persist the shared backend credential with Windows DPAPI, never as plaintext in Git.
if (Test-Path -LiteralPath $credentialPath) {
    $credential = Import-Clixml -LiteralPath $credentialPath
    $backendKey = $credential.GetNetworkCredential().Password
} else {
    $backendKey = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    $credential = [pscredential]::new(
        'warnerco-class-backend', (ConvertTo-SecureString $backendKey -AsPlainText -Force)
    )
    Write-AtomicLocalFile $credentialPath { param($path) $credential | Export-Clixml -LiteralPath $path }
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
$image = "$($registry.properties.loginServer)/$imageTag"
# A successful receipt binds the cached image to this environment and these exact inputs.
$reuseImage = $SkipBuild -or (-not $Rebuild -and $previousDeployment -and $previousDeployment.image -eq $image)
if (-not $reuseImage) {
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
    # Fail before updating ACA if a cached image has been deleted; Rebuild explicitly repairs it.
    $null = Invoke-AzureCli @(
        'acr', 'repository', 'show', '--subscription', $SubscriptionId,
        '--name', $RegistryName, '--image', $imageTag, '--only-show-errors', '-o', 'json'
    )
}
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
Write-AtomicLocalFile $deploymentPath { param($path) $deployment | ConvertTo-Json | Set-Content -LiteralPath $path }
$backendKey = $null
$armToken = $null
$deployment | ConvertTo-Json
} finally {
    # Keep the harmless lock file so no delete/recreate race can bypass the exclusive handle.
    $deploymentLease.Dispose()
}
