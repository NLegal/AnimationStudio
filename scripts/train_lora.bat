@echo off
rem train_lora.bat - wrapper for scripts\train_lora.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" train_lora %*
exit /b %errorlevel%