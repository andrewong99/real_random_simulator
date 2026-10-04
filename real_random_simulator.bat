@echo off
rem ===========================================================================
rem  Real Random Simulator - Windows launcher
rem
rem  Double-click this file to start the app. The console closes immediately
rem  and only the program window stays.
rem
rem  If something goes wrong, run it with the word debug to keep the console
rem  open and see the full traceback:
rem
rem      real_random_simulator.bat debug
rem
rem  Keep this .bat beside real_random_simulator.py and rrs_kernel.py.
rem  Nothing else in the folder is read or written by this launcher.
rem ===========================================================================
setlocal EnableExtensions
title Real Random Simulator
pushd "%~dp0"

set "APP=%~dp0real_random_simulator.py"
set "KERNEL=%~dp0rrs_kernel.py"
if not exist "%APP%" goto :no_app
if not exist "%KERNEL%" goto :no_kernel

set "PY="
set "PYW="

rem --- 1. the Windows Python Launcher (py.exe) - preferred -------------------
py -3 -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
  set "PY=py -3"
  set "PYW=pyw -3"
  goto :found
)

rem --- 2. python.exe on PATH -------------------------------------------------
python -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
  set "PY=python"
  set "PYW=pythonw"
  goto :found
)

rem --- 3. the usual install locations ---------------------------------------
call :probe "%USERPROFILE%\Python314\python.exe"
if defined PY goto :found
call :probe "%USERPROFILE%\Python313\python.exe"
if defined PY goto :found
call :probe "%USERPROFILE%\Python312\python.exe"
if defined PY goto :found
call :probe "%USERPROFILE%\Python311\python.exe"
if defined PY goto :found
call :probe "%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if defined PY goto :found
call :probe "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if defined PY goto :found
call :probe "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY goto :found
call :probe "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if defined PY goto :found
call :probe "C:\Python314\python.exe"
if defined PY goto :found
call :probe "C:\Python313\python.exe"
if defined PY goto :found
call :probe "C:\Python312\python.exe"
if defined PY goto :found
call :probe "C:\Python311\python.exe"
if defined PY goto :found
call :probe "C:\Program Files\Python313\python.exe"
if defined PY goto :found
call :probe "C:\Program Files\Python312\python.exe"
if defined PY goto :found
goto :no_python

:found
if /i "%~1"=="debug" goto :debug
start "" %PYW% "%APP%"
popd
exit /b 0

:debug
echo.
echo   interpreter : %PY%
echo   script      : %APP%
echo.
echo   ---------------------------------------------------------------
%PY% "%APP%"
set "RC=%errorlevel%"
echo   ---------------------------------------------------------------
echo   exited with code %RC%
echo.
pause
popd
exit /b %RC%

rem --- helper: accept an interpreter only if it has tkinter ------------------
:probe
if defined PY exit /b 0
if not exist "%~1" exit /b 0
"%~1" -c "import tkinter" >nul 2>&1
if errorlevel 1 exit /b 0
set "PY="%~1""
set "PYW="%~dpn1w.exe""
if not exist "%~dpn1w.exe" set "PYW="%~1""
exit /b 0

:no_kernel
echo.
echo   [X] rrs_kernel.py was not found next to this launcher.
echo.
echo       expected here: %KERNEL%
echo.
echo       Both programs share that one kernel file - the entropy
echo       sources, the statistics and the theme all live in it.
echo       Keep it in the same folder as the .py files.
echo.
pause
popd
exit /b 1

:no_app
echo.
echo   [X] real_random_simulator.py was not found next to this launcher.
echo.
echo       expected here: %APP%
echo.
echo       Keep the .bat, the .py and rrs_kernel.py in the same folder.
echo.
pause
popd
exit /b 1

:no_python
echo.
echo   [X] No Python 3 with tkinter was found.
echo.
echo       Looked for: the "py" launcher, "python" on PATH, and the usual
echo       install folders under your profile, LOCALAPPDATA, C:\ and
echo       C:\Program Files.
echo.
echo       Install Python 3 from https://www.python.org/downloads/ and
echo       tick "Add python.exe to PATH" during setup. tkinter ships with
echo       the standard python.org installer - nothing else is needed.
echo.
echo       Already have Python? Open a Command Prompt and run:
echo.
echo           python -c "import tkinter; print(tkinter.TkVersion)"
echo.
echo       If that errors, your Python was built without tkinter. If it
echo       prints a version, tell me the output of:  where python
echo.
pause
popd
exit /b 1
