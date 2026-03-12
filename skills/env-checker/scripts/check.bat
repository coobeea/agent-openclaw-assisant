@echo off
REM 虚拟环境快速检查脚本（Windows）
REM 功能：检查项目根目录下的虚拟环境是否存在
REM 使用：check.bat
REM 退出码：0=存在, 1=不存在

setlocal enabledelayedexpansion

REM 获取脚本所在目录（env-checker\scripts）
set SCRIPT_DIR=%~dp0
REM 去除末尾反斜杠
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM 项目根目录：env-checker\scripts -> env-checker -> skills -> 根目录
for %%I in ("%SCRIPT_DIR%\..\..\..")  do set PROJECT_ROOT=%%~fI

REM 虚拟环境路径
set VENV_DIR=%PROJECT_ROOT%\.venv
set VENV_PYTHON=%VENV_DIR%\Scripts\python.exe

REM 检查虚拟环境是否存在
if exist "%VENV_PYTHON%" (
    REM 虚拟环境存在
    for /f "delims=" %%V in ('"%VENV_PYTHON%" --version 2^>^&1') do set PYTHON_VERSION=%%V
    echo VENV_EXISTS=true
    echo VENV_PYTHON=%VENV_PYTHON%
    echo VENV_DIR=%VENV_DIR%
    echo PROJECT_ROOT=%PROJECT_ROOT%
    echo PYTHON_VERSION=!PYTHON_VERSION!
    exit /b 0
) else (
    REM 虚拟环境不存在
    set SETUP_SCRIPT=%SCRIPT_DIR%\setup.bat
    echo VENV_EXISTS=false
    echo VENV_DIR=%VENV_DIR%
    echo PROJECT_ROOT=%PROJECT_ROOT%
    echo SETUP_COMMAND=!SETUP_SCRIPT!
    exit /b 1
)
