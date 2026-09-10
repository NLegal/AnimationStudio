@echo off
rem generate_phase7.bat - wrapper for scripts\generate_phase7.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_phase7 %*
exit /b %errorlevel%