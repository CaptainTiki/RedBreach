param(
    [string]$GodotPath = 'D:\SteamLibrary\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe',
    [switch]$Validate
)
$ErrorActionPreference = 'Stop'
$projectDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\RedBreach'))
if (-not (Test-Path -LiteralPath $GodotPath)) { throw 'Godot not found. Supply -GodotPath.' }
# Rebuild the editable source map; never run the one-time bootstrap generator here.
$checks = ,@('res://tools/build_freight.gd', 'freight_build.log', '600', '^FREIGHT_BUILD: \d+ brushes; save=0$')
if ($Validate) {
    $checks += ,@('res://tools/validate_freight.gd', 'freight_qa.log', '70000', '^FREIGHT_QA: \d+ checks; 0 failures$')
}
foreach ($entry in $checks) {
    $logPath = Join-Path $projectDir ('.godot\' + $entry[1])
    $runArgs = @('--headless', '--path', ('"' + $projectDir + '"'), '--log-file', ('"' + $logPath + '"'), '--script', $entry[0], '--fixed-fps', '120', '--quit-after', $entry[2])
    $run = Start-Process -FilePath $GodotPath -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait
    Get-Content -LiteralPath $logPath
    if ($run.ExitCode -ne 0) { throw "$($entry[0]) failed with exit code $($run.ExitCode)" }
    if (Select-String -LiteralPath $logPath -Pattern '^(SCRIPT ERROR:|ERROR:|FAIL:)' -Quiet) { throw "$($entry[0]) reported errors; see $logPath" }
    if (-not (Select-String -LiteralPath $logPath -Pattern $entry[3] -Quiet)) { throw "$($entry[0]) did not finish; see $logPath" }
}
