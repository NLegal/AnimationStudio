@echo off
rem generate_phase4.bat - wrapper for scripts\generate_phase4.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_phase4 %*
exit /b %errorlevel%
