@echo off
rem generate_phase3_assets.bat - wrapper for scripts\generate_phase3_assets.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_phase3_assets %*
exit /b %errorlevel%
