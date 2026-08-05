@echo off
rem build_world_sheets.bat - wrapper for scripts\build_world_sheets.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" build_world_sheets %*
exit /b %errorlevel%
