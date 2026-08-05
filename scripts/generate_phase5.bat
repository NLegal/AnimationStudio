@echo off
rem generate_phase5.bat - wrapper for scripts\generate_phase5.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_phase5 %*
exit /b %errorlevel%
