@echo off
rem build_asset_sheets.bat - wrapper for scripts\build_asset_sheets.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" build_asset_sheets %*
exit /b %errorlevel%
