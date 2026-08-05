@echo off
rem export_assets.bat - wrapper for scripts\export_assets.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" export_assets %*
exit /b %errorlevel%
