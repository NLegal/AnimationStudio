@echo off
rem build_model_sheets.bat - wrapper for scripts\build_model_sheets.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" build_model_sheets %*
exit /b %errorlevel%
