@echo off
rem generate_wardrobe.bat - wrapper for scripts\generate_wardrobe.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_wardrobe %*
exit /b %errorlevel%
