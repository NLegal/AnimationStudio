@echo off
rem generate_phase1_library.bat - wrapper for scripts\generate_phase1_library.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_phase1_library %*
exit /b %errorlevel%
