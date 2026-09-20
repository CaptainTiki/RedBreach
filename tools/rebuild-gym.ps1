param(
    [string]$GodotPath = 'D:\SteamLibrary\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe',
    [switch]$Validate
)
$ErrorActionPreference = 'Stop'
$projectDir = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\RedBreach'))
if (-not (Test-Path -LiteralPath $GodotPath)) { throw 'Godot not found. Supply -GodotPath.' }
New-Item -ItemType Directory -Path (Join-Path $projectDir '.godot') -Force | Out-Null
function Invoke-GymScript([string]$Script, [string]$LogName, [int]$FixedFPS = 0) {
    $logPath = Join-Path $projectDir ".godot\$LogName"
    $runArgs = @('--headless', '--path', ('"' + $projectDir + '"'), '--log-file', ('"' + $logPath + '"'), '--script', $Script)
    if ($FixedFPS -gt 0) { $runArgs += @('--fixed-fps', $FixedFPS) }
    $run = Start-Process -FilePath $GodotPath -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait
    Get-Content -LiteralPath $logPath
    if (Select-String -LiteralPath $logPath -Pattern '^(SCRIPT ERROR:|ERROR:|FAIL:)' -Quiet) { throw "$Script reported errors; see $logPath" }
    if ($run.ExitCode -ne 0) { throw "$Script failed with exit code $($run.ExitCode)" }
}
Invoke-GymScript 'res://tools/build_gym.gd' 'gym_build.log'
if ($Validate) {
    Invoke-GymScript 'res://tools/validate_gym.gd' 'gym_qa.log'
    Invoke-GymScript 'res://tools/validate_motion.gd' 'motion_qa.log' 120
    Invoke-GymScript 'res://tools/validate_door.gd' 'door_qa.log' 120
}
