param(
    # Machine-specific. Set REDBREACH_GODOT once per machine rather than editing this,
    # or pass -GodotPath. The desktop default is kept as the last resort.
    [string]$GodotPath = $(if ($env:REDBREACH_GODOT) { $env:REDBREACH_GODOT }
                          else { 'D:\SteamLibrary\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe' }),
    [switch]$Validate
)
$ErrorActionPreference = 'Stop'
$projectDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\RedBreach'))
if (-not (Test-Path -LiteralPath $GodotPath)) { throw "Godot not found at '$GodotPath'. Set `$env:REDBREACH_GODOT or pass -GodotPath." }
$import = Start-Process -FilePath $GodotPath -ArgumentList @('--headless', '--path', ('"' + $projectDir + '"'), '--import') -WindowStyle Hidden -PassThru -Wait
if ($import.ExitCode -ne 0) { throw "texture import failed with exit code $($import.ExitCode)" }
# Rebuild freight v2 from the editable source map; never run the one-time bootstrap here.
$checks = ,@('res://tools/build_freight_v2.gd', 'freight_v2_build.log', '2400', '^FREIGHT_V2_BUILD: \d+ brushes; \d+ lights; \d+ ladders; \d+ kit pieces; \d+ navigation polygons; save=0$', @())
if ($Validate) {
    # The generic, marker-driven validator: any map validates by placing markers.
    $checks += ,@('res://tools/validate_markers.gd', 'freight_v2_qa.log', '400000', '^MARKER_QA: \d+ checks; 0 failures$', @('--', 'res://missions/freight_v2/freight_v2.tscn'))
}
if ($Validate) {
    # The source map must be sealed (no air path to the void) and is checked for visible z-fighting. Reads the map as
    # edited, so it covers TrenchBroom hand edits too. A leak fails the rebuild; z-fighting is reported.
    $zf = & python (Join-Path $PSScriptRoot 'check-map-zfight.py') (Join-Path $projectDir 'maps/freight_v2_01.map') --limit 12
    $zf | ForEach-Object { Write-Output $_ }
    if ($LASTEXITCODE -ne 0) { throw "check-map-zfight.py failed" }
    if ($zf | Select-String -Pattern '^LEAK \d+:' -Quiet) { throw "freight_v2_01.map leaks into the void; see the LEAK lines" }
}
foreach ($entry in $checks) {
    $logPath = Join-Path $projectDir ('.godot\' + $entry[1])
    $runArgs = @('--path', ('"' + $projectDir + '"'), '--log-file', ('"' + $logPath + '"'), '--script', $entry[0], '--fixed-fps', '120', '--quit-after', $entry[2]) + $entry[4]
    if ($entry[0] -notlike '*capture*') { $runArgs = @('--headless') + $runArgs }
    $run = Start-Process -FilePath $GodotPath -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait
    Get-Content -LiteralPath $logPath
    if ($run.ExitCode -ne 0) { throw "$($entry[0]) failed with exit code $($run.ExitCode)" }
    if (Select-String -LiteralPath $logPath -Pattern '^(SCRIPT ERROR:|ERROR:|FAIL:)' -Quiet) { throw "$($entry[0]) reported errors; see $logPath" }
    if (-not (Select-String -LiteralPath $logPath -Pattern $entry[3] -Quiet)) { throw "$($entry[0]) did not finish; see $logPath" }
}
