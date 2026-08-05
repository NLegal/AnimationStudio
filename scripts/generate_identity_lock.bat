@echo off
rem generate_identity_lock.bat - wrapper for scripts\generate_identity_lock.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_identity_lock %*
exit /b %errorlevel%
