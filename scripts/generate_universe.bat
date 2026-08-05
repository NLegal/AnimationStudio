@echo off
rem generate_universe.bat - wrapper for scripts\generate_universe.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_universe %*
exit /b %errorlevel%
