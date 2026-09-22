param(
    # Machine-specific. Set REDBREACH_GODOT once per machine rather than editing this,
    # or pass -GodotPath. The desktop default is kept as the last resort.
    [string]$GodotPath = $(if ($env:REDBREACH_GODOT) { $env:REDBREACH_GODOT }
                          else { 'D:\SteamLibrary\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe' }),
    [switch]$Validate,
    [switch]$Capture
)
$ErrorActionPreference = 'Stop'
$projectDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\RedBreach'))
if (-not (Test-Path -LiteralPath $GodotPath)) { throw "Godot not found at '$GodotPath'. Set `$env:REDBREACH_GODOT or pass -GodotPath." }
# Rebuild the editable source map; never run the one-time bootstrap generator here.
$checks = ,@('res://tools/build_architecture_lab_corners.gd', 'arch_corner_build.log', '600', '^ARCH_CORNER_BUILD: \d+ brushes; save=0$')
if ($Validate) {
    $checks += ,@('res://tools/validate_architecture_lab_corners.gd', 'arch_corner_qa.log', '20000', '^ARCH_CORNER_QA: \d+ checks; 0 failures$')
}
if ($Capture) {
    $checks += ,@('res://tools/capture_architecture_lab_corners.gd', 'arch_corner_capture.log', '4000', '^ARCH_CORNER_CAPTURE: PASS$')
}
foreach ($entry in $checks) {
    $logPath = Join-Path $projectDir ('.godot\' + $entry[1])
    $runArgs = @('--path', ('"' + $projectDir + '"'), '--log-file', ('"' + $logPath + '"'), '--script', $entry[0], '--fixed-fps', '120', '--quit-after', $entry[2])
    if ($entry[0] -notlike '*capture*') { $runArgs = @('--headless') + $runArgs }
    $run = Start-Process -FilePath $GodotPath -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait
    Get-Content -LiteralPath $logPath
    if ($run.ExitCode -ne 0) { throw "$($entry[0]) failed with exit code $($run.ExitCode)" }
    if (Select-String -LiteralPath $logPath -Pattern '^(SCRIPT ERROR:|ERROR:|FAIL:)' -Quiet) { throw "$($entry[0]) reported errors; see $logPath" }
    if (-not (Select-String -LiteralPath $logPath -Pattern $entry[3] -Quiet)) { throw "$($entry[0]) did not finish; see $logPath" }
}
