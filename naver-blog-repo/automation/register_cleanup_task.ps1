# 매일 오전 10시에 "node automation/drive.js cleanup" 을 실행하는 Windows 작업을 등록합니다.
# PC가 꺼져 있었으면 켜진 뒤 바로 실행합니다 (StartWhenAvailable). 결과는 .state/cleanup.log 에 쌓입니다.
# 실행: powershell -ExecutionPolicy Bypass -File automation\register_cleanup_task.ps1
$repo = Split-Path -Parent $PSScriptRoot
$node = (Get-Command node -ErrorAction SilentlyContinue).Source
if (-not $node) { $node = "C:\Program Files\nodejs\node.exe" }
$cmd = "/c cd /d `"$repo`" && `"$node`" automation\drive.js cleanup >> .state\cleanup.log 2>&1"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $cmd
$trigger = New-ScheduledTaskTrigger -Daily -At 10:00
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "NaverBlog_DriveCleanup" -Action $action -Trigger $trigger -Settings $settings -Description "블로그 사진 폴더 3일 뒤 정리" -Force | Out-Null
Write-Output "등록 완료: NaverBlog_DriveCleanup (매일 10:00)"
