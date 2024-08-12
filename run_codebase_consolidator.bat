@echo off
setlocal

rem Set the path to the Python script
set "python_script_path=%~dp0codebase_consolidator_gui.py"

rem Attempt to find the Python executable by using 'python' command
for %%i in (python python3) do (
    where %%i >nul 2>nul
    if not errorlevel 1 (
        set "python_executable_path=%%i"
        goto :found_python
    )
)

rem If not found, provide an error message and exit
echo Python executable not found. Please ensure Python is installed and added to the PATH.
exit /b 1

:found_python
rem Debugging output
echo Python Script Path: %python_script_path%
echo Python Executable Path: %python_executable_path%

rem Check if a directory argument is provided
if "%~1"=="" (
    echo Usage: %~nx0 "path\to\directory"
    exit /b 1
)

rem Run the Python script with the provided directory argument
"%python_executable_path%" "%python_script_path%" "%~1"

endlocal
