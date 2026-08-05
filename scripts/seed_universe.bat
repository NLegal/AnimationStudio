@echo off
rem seed_universe.bat - wrapper for scripts\seed_universe.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" seed_universe %*
exit /b %errorlevel%
