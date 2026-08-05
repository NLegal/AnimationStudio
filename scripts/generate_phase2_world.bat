@echo off
rem generate_phase2_world.bat - wrapper for scripts\generate_phase2_world.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_phase2_world %*
exit /b %errorlevel%
