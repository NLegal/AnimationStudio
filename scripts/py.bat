@echo off
rem py.bat - generic Windows wrapper for scripts\*.py entry points.
rem
rem Usage:
rem   scripts\py.bat <script-name> [args...]
rem   scripts\py.bat seed_universe --db catalog.db
rem   scripts\py.bat generate_phase1_library --backend comfyui --jobs 12
rem
rem Python resolution order: %PYTHON% -> the Python 3.14 install in the
rem user AppData layout (python3.exe, then python.exe) -> python on PATH.
rem Set PYTHON explicitly to override.

setlocal

if defined PYTHON goto :have_python

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python3.exe" (
    set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python3.exe"
    goto :have_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    goto :have_python
)
set "PYTHON=python"

:have_python
if "%~1"=="" (
    echo usage: py.bat ^<script-name^> [args...]
    exit /b 1
)
"%PYTHON%" "%~dp0%~1.py" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%
