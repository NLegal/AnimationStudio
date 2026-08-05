@echo off
rem generate_body_lock.bat - wrapper for scripts\generate_body_lock.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_body_lock %*
exit /b %errorlevel%
