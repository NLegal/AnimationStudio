@echo off
rem verify_catalog.bat - wrapper for scripts\verify_catalog.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" verify_catalog %*
exit /b %errorlevel%