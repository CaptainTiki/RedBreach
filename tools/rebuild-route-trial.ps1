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
$checks = ,@('res://tools/build_route_trial.gd', 'route_build.log')
if ($Validate) {
    $checks += ,@('res://tools/validate_encounters.gd', 'encounter_qa.log')
    $checks += ,@('res://tools/validate_route_trial.gd', 'route_qa.log')
    $checks += ,@('res://tools/validate_bug_mix.gd', 'bug_mix_qa.log')
    $checks += ,@('res://tools/validate_rear_ambush.gd', 'rear_ambush_qa.log')
    $checks += ,@('res://tools/validate_greybox.gd', 'greybox_qa.log')
}
foreach ($entry in $checks) {
    $logPath = Join-Path $projectDir ('.godot\' + $entry[1])
    $runArgs = @('--headless', '--path', ('"' + $projectDir + '"'), '--log-file', ('"' + $logPath + '"'), '--script', $entry[0], '--fixed-fps', '120')
    $run = Start-Process -FilePath $GodotPath -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait
    Get-Content -LiteralPath $logPath
    if (Select-String -LiteralPath $logPath -Pattern '^(SCRIPT ERROR:|ERROR:|FAIL:)' -Quiet) { throw "$($entry[0]) reported errors; see $logPath" }
    if ($run.ExitCode -ne 0) { throw "$($entry[0]) failed with exit code $($run.ExitCode)" }
}
