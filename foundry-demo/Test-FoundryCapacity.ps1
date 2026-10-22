#Requires -Version 7.0
<#
.SYNOPSIS
Read model catalogs, quota, and deployment capacity for a small Foundry demo.
.DESCRIPTION
Uses the existing Azure CLI sign-in. Performs GET/list operations only, never
changes the default subscription, and never requests or prints access tokens.
Catalog availability, quota, and capacity are separate checks. A positive
capacity value does not prove that a model is still deployable or that every
Foundry feature is available. Review lifecycle dates before deploying.
.PARAMETER SubscriptionId
The intended subscription ID. Required to avoid deploying into an implicit account.
.PARAMETER Regions
Regions to inspect for both the chat and embedding deployments.
.EXAMPLE
./foundry-demo/Test-FoundryCapacity.ps1 -SubscriptionId '<subscription-id>'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [guid] $SubscriptionId,
    [string[]] $Regions = @('eastus2', 'swedencentral', 'westus3', 'francecentral')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw 'Azure CLI is required. Install it and sign in with az login first.'
}

function Invoke-AzJson {
    param([Parameter(Mandatory)][string[]] $Arguments)
    $raw = & az @Arguments --only-show-errors --output json
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI failed ($LASTEXITCODE): $($Arguments[0]) $($Arguments[1]). No resources were changed."
    }
    if (-not $raw) { throw 'Azure CLI returned no JSON.' }
    return ($raw -join "`n" | ConvertFrom-Json -AsHashtable)
}

$subscription = $SubscriptionId.ToString()
$account = Invoke-AzJson -Arguments @('account', 'show', '--subscription', $subscription)
if ($account.state -ne 'Enabled') { throw 'The requested subscription is not enabled.' }
$candidates = @('gpt-5.4-mini', 'gpt-5-mini', 'gpt-4.1-mini', 'text-embedding-3-small')
$catalog = [System.Collections.Generic.List[object]]::new()
$quota = [System.Collections.Generic.List[object]]::new()
$capacity = [System.Collections.Generic.List[object]]::new()
$failures = [System.Collections.Generic.List[string]]::new()

foreach ($region in $Regions) {
    if ($region -notmatch '^[a-z0-9]+$') { throw "Invalid Azure region: $region" }
    try {
        $models = Invoke-AzJson -Arguments @('cognitiveservices', 'model', 'list', '--location', $region, '--subscription', $subscription)
        foreach ($entry in $models) {
            if ($entry.model.name -in $candidates) {
                # Retain lifecycle details so retired models cannot look like a recommendation.
                $catalog.Add([ordered]@{ region = $region; model = $entry.model })
            }
        }
        $usage = Invoke-AzJson -Arguments @('rest', '--method', 'get', '--subscription', $subscription,
            '--url', "https://management.azure.com/subscriptions/$subscription/providers/Microsoft.CognitiveServices/locations/$region/usages?api-version=2024-10-01")
        foreach ($entry in $usage.value) {
            if ($entry.name.value -match 'gpt-.*mini|text-embedding-3-small') {
                $quota.Add([ordered]@{
                    region = $region; name = $entry.name.value; label = $entry.name.localizedValue
                    used = $entry.currentValue; limit = $entry.limit
                    remaining = $entry.limit - $entry.currentValue; unit = $entry.unit
                })
            }
        }
    } catch {
        $failures.Add("${region}: $($_.Exception.Message)")
    }
}

# Capacity is subscription-wide. Query each observed model/version only once.
$seen = @{}
foreach ($entry in $catalog) {
    $model = $entry.model
    $key = "$($model.name)/$($model.version)"
    if ($seen.ContainsKey($key)) { continue }
    $seen[$key] = $true
    try {
        $name = [uri]::EscapeDataString($model.name)
        $version = [uri]::EscapeDataString($model.version)
        $result = Invoke-AzJson -Arguments @('rest', '--method', 'get', '--subscription', $subscription,
            '--url', "https://management.azure.com/subscriptions/$subscription/providers/Microsoft.CognitiveServices/modelCapacities?api-version=2024-10-01&modelFormat=OpenAI&modelName=$name&modelVersion=$version")
        foreach ($item in $result.value) {
            if ($item.properties.skuName -in @('Standard', 'GlobalStandard', 'DataZoneStandard')) {
                $capacity.Add([ordered]@{
                    region = $item.location; model = $model.name; version = $model.version
                    sku = $item.properties.skuName; available = $item.properties.availableCapacity
                })
            }
        }
    } catch {
        $failures.Add("${key}: $($_.Exception.Message)")
    }
}
if ($catalog.Count -eq 0) { $failures.Add('No candidate models were found; do not infer deployment readiness.') }

[ordered]@{
    checkedAtUtc = [DateTime]::UtcNow.ToString('o')
    subscriptionName = $account.name
    status = $(if ($failures.Count) { 'incomplete' } else { 'read-only checks completed' })
    catalogs = $catalog.ToArray()
    quotas = $quota.ToArray()
    capacities = $capacity.ToArray()
    errors = $failures.ToArray()
    note = 'Capacity is not a spend cap. Check model lifecycle, SKU units, and feature support before deployment. No resources were created.'
} | ConvertTo-Json -Depth 20
if ($failures.Count) { exit 1 }
