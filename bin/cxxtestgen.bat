@echo off
setlocal

rem Strip .bat extension, if present
set me=%0
if "%me:~-4,4%" == ".bat" (set py=%me:~0,-4%) else (set py=%me%)
rem Run the python script
python %py% %*
