@echo off

taskkill /f /im python35.exe /t
taskkill /f /im redis-server.exe /t

start /D %~dp0 restart_cache.bat 
start /D %~dp0 restart_chat.bat
start /D %~dp0 restart_dae.bat