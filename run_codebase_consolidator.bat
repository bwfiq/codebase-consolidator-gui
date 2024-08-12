@echo off
setlocal

set "python_script_path=C:\GitRepos\codebase-consolidator-gui\codebase_consolidator_gui.py"
set "python_executable_path=C:\Users\rafiq\AppData\Local\Programs\Python\Python311\python.exe"

if "%~1"=="" (
    echo Usage: %~nx0 "path\to\directory"
    exit /b 1
)

"%python_executable_path%" "%python_script_path%" "%~1"

endlocal
