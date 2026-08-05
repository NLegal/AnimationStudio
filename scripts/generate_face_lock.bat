@echo off
rem generate_face_lock.bat - wrapper for scripts\generate_face_lock.py.
rem Forwards all arguments to the generic runner (scripts\py.bat).
call "%~dp0py.bat" generate_face_lock %*
exit /b %errorlevel%
