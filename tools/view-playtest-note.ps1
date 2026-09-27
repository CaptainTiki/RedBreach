param(
    # The session folder (playtests/<scene>/<date_time>); the newest session when left out.
    [string]$Session = '',
    # A note number, or 'all'.
    [string]$Note = 'all',
    # Machine-specific. Set REDBREACH_GODOT once per machine rather than editing this, or pass -GodotPath.
    [string]$GodotPath = $(if ($env:REDBREACH_GODOT) { $env:REDBREACH_GODOT }
                          else { 'D:\SteamLibrary\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe' })
)
# Puts a camera back where a playtest note was made and renders the view (the map as it is now) to
# RedBreach/.godot/playtest_views/<scene>/<date_time>/note_NNN.png, which git ignores.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$projectDir = Join-Path $root 'RedBreach'
if (-not (Test-Path -LiteralPath $GodotPath)) { throw "Godot not found at '$GodotPath'. Set `$env:REDBREACH_GODOT or pass -GodotPath." }
if (-not $Session) {
    $latest = Get-ChildItem -Path (Join-Path $root 'playtests') -Filter notes.jsonl -Recurse | Sort-Object { $_.Directory.Name } | Select-Object -Last 1
    if (-not $latest) { throw "No playtest sessions under $(Join-Path $root 'playtests')" }
    $Session = $latest.DirectoryName
}
$Session = [IO.Path]::GetFullPath($Session)
$out = Join-Path $projectDir ('.godot\playtest_views\' + (Split-Path (Split-Path $Session -Parent) -Leaf) + '\' + (Split-Path $Session -Leaf))
$log = Join-Path $projectDir '.godot\playtest_view.log'
$runArgs = @('--path', ('"' + $projectDir + '"'), '--log-file', ('"' + $log + '"'), '--script', 'res://tools/view_playtest_note.gd',
             '--quit-after', '6000', '--', ('"' + $Session + '"'), $Note, ('"' + $out + '"'))
$run = Start-Process -FilePath $GodotPath -ArgumentList $runArgs -WindowStyle Normal -PassThru -Wait
Get-Content -LiteralPath $log | Select-String -Pattern '^VIEW_NOTE' | ForEach-Object { $_.Line }
if ($run.ExitCode -ne 0) { throw "view_playtest_note.gd failed; see $log" }
