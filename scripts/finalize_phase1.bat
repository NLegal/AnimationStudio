@echo off
rem finalize_phase1.bat - wrapper for scripts\finalize_phase1.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" finalize_phase1 %*
exit /b %errorlevel%
