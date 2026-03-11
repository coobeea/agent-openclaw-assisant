@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM env-checker: Windows Python 环境全自动检测、安装、初始化、验证
REM 目标版本: Python 3.12
REM 全程无需人工干预，执行完毕即可运行所有 Skill

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "SKILL_DIR=%%~fI"

set "REQUIRED_MAJOR=3"
set "REQUIRED_MINOR=12"
set "REQUIRED_VERSION=3.12"
set "PYTHON_FULL_VERSION=3.12.8"

set "WIN_INSTALLER_URL=https://www.python.org/ftp/python/%PYTHON_FULL_VERSION%/python-%PYTHON_FULL_VERSION%-amd64.exe"
set "WIN_INSTALLER_URL_ARM=https://www.python.org/ftp/python/%PYTHON_FULL_VERSION%/python-%PYTHON_FULL_VERSION%-arm64.exe"
set "WIN_INSTALLER_URL_BACKUP=https://registry.npmmirror.com/-/binary/python/%PYTHON_FULL_VERSION%/python-%PYTHON_FULL_VERSION%-amd64.exe"

set "UNIFIED_REQUIREMENTS=%SKILL_DIR%\requirements.txt"
set "VERIFY_SCRIPT=%SCRIPT_DIR%verify.py"

set "PROJECT_DIR="
set "REQUIREMENTS_FILE="
set "CHECK_ONLY=0"
set "VERBOSE=0"
set "VENV_NAME=.venv"
set "FOUND_PYTHON="

:parse_args
if "%~1"=="" goto :done_args
if "%~1"=="--project-dir" (
    set "PROJECT_DIR=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--requirements" (
    set "REQUIREMENTS_FILE=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--check-only" (
    set "CHECK_ONLY=1"
    shift
    goto :parse_args
)
if "%~1"=="--verbose" (
    set "VERBOSE=1"
    shift
    goto :parse_args
)
if "%~1"=="--venv-name" (
    set "VENV_NAME=%~2"
    shift
    shift
    goto :parse_args
)
echo [ERROR] 未知参数: %~1
exit /b 1

:done_args

echo.
echo [STEP] ===== 环境全自动初始化 (Python %REQUIRED_VERSION%) =====
echo.
echo [INFO] 操作系统: Windows

REM === Step 1: 检测 Python ===
echo [STEP] 1/5 检测 Python 环境...

call :try_python "python" && goto :python_found
call :try_python "python3" && goto :python_found
call :try_python "py -%REQUIRED_VERSION%" && goto :python_found
call :try_python "py -3" && goto :python_found

for %%D in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%PROGRAMFILES%\Python312\python.exe"
    "%PROGRAMFILES(x86)%\Python312\python.exe"
    "C:\Python312\python.exe"
    "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
) do (
    if exist "%%~D" (
        call :try_python "%%~D" && goto :python_found
    )
)

for /f "delims=" %%P in ('where python 2^>nul') do (
    call :try_python "%%P" && goto :python_found
)

echo [WARN] 未找到 Python %REQUIRED_VERSION% 或兼容版本

if %CHECK_ONLY%==1 (
    echo [ERROR] Python %REQUIRED_VERSION% 未安装
    exit /b 1
)

REM === Step 2: 安装 Python ===
echo [STEP] 2/5 自动安装 Python %PYTHON_FULL_VERSION%...
call :install_python_windows
if errorlevel 1 (
    echo [ERROR] Python 安装失败
    exit /b 1
)
goto :after_install

:python_found
echo [INFO] 找到 Python: %FOUND_PYTHON%

if %CHECK_ONLY%==1 (
    echo.
    echo ==============================================
    echo   环境检测报告
    echo ==============================================
    echo.
    echo   Python 路径:  %FOUND_PYTHON%
    echo   目标版本:     %REQUIRED_VERSION%.x
    echo   版本状态:     匹配
    echo.
    echo ==============================================
    exit /b 0
)

:after_install
if "%FOUND_PYTHON%"=="" (
    call :try_python "python" && goto :install_verified
    call :try_python "py -%REQUIRED_VERSION%" && goto :install_verified
    echo [ERROR] 安装后仍未找到 Python
    exit /b 1
)
:install_verified

REM === Step 3: 创建虚拟环境 ===
echo [STEP] 3/5 配置虚拟环境...

if defined PROJECT_DIR (
    set "TARGET_DIR=%PROJECT_DIR%"
) else (
    set "TARGET_DIR=%CD%"
)

set "VENV_DIR=%TARGET_DIR%\%VENV_NAME%"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    echo [INFO] 虚拟环境已存在: %VENV_DIR%
    goto :install_deps
)

if exist "%VENV_DIR%" (
    echo [WARN] 虚拟环境不完整，重新创建...
    rmdir /s /q "%VENV_DIR%" 2>nul
)

echo [INFO] 创建虚拟环境: %VENV_DIR%
%FOUND_PYTHON% -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo [ERROR] 虚拟环境创建失败
    exit /b 1
)

echo [INFO] 升级 pip...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet 2>nul

:install_deps
REM === Step 4: 安装依赖（统一 + 项目） ===
echo [STEP] 4/5 安装依赖...

if exist "%UNIFIED_REQUIREMENTS%" (
    echo [INFO] 安装统一依赖(所有Skill): %UNIFIED_REQUIREMENTS%
    "%VENV_PYTHON%" -m pip install -r "%UNIFIED_REQUIREMENTS%" --quiet
)

if defined REQUIREMENTS_FILE (
    if exist "%REQUIREMENTS_FILE%" (
        echo [INFO] 安装项目依赖: %REQUIREMENTS_FILE%
        "%VENV_PYTHON%" -m pip install -r "%REQUIREMENTS_FILE%" --quiet
    )
) else if exist "%TARGET_DIR%\requirements.txt" (
    if not "%TARGET_DIR%\requirements.txt"=="%UNIFIED_REQUIREMENTS%" (
        echo [INFO] 安装项目依赖: %TARGET_DIR%\requirements.txt
        "%VENV_PYTHON%" -m pip install -r "%TARGET_DIR%\requirements.txt" --quiet
    )
)

echo [INFO] 所有依赖安装完成

REM === Step 5: 自动验证 ===
echo [STEP] 5/5 验证环境...

if exist "%VERIFY_SCRIPT%" (
    "%VENV_PYTHON%" "%VERIFY_SCRIPT%"
    if errorlevel 1 (
        echo [ERROR] 环境验证未通过
        exit /b 1
    )
) else (
    echo [WARN] 验证脚本不存在，跳过验证
)

echo.
echo ==============================================
echo   环境就绪
echo ==============================================
echo.
echo   Python:     %VENV_PYTHON%
echo   虚拟环境:   %VENV_DIR%
if defined PROJECT_DIR echo   项目目录:   %PROJECT_DIR%
echo.
echo ==============================================

echo ENV_PYTHON=%VENV_PYTHON%
echo ENV_VENV_DIR=%VENV_DIR%
exit /b 0

REM ===== 辅助函数 =====

:try_python
setlocal
set "CMD=%~1"
for /f "tokens=2 delims= " %%V in ('%CMD% --version 2^>nul') do (
    set "VER=%%V"
)
if not defined VER (
    endlocal
    exit /b 1
)
for /f "tokens=1,2 delims=." %%A in ("%VER%") do (
    set "VMAJOR=%%A"
    set "VMINOR=%%B"
)
if "%VMAJOR%"=="%REQUIRED_MAJOR%" if "%VMINOR%"=="%REQUIRED_MINOR%" (
    endlocal & set "FOUND_PYTHON=%CMD%"
    exit /b 0
)
if %VMAJOR% gtr %REQUIRED_MAJOR% (
    endlocal & set "FOUND_PYTHON=%CMD%"
    exit /b 0
)
if "%VMAJOR%"=="%REQUIRED_MAJOR%" if %VMINOR% gtr %REQUIRED_MINOR% (
    endlocal & set "FOUND_PYTHON=%CMD%"
    exit /b 0
)
endlocal
exit /b 1

:install_python_windows
echo [INFO] 从 python.org 下载安装包...

set "TMPDIR=%TEMP%\python_installer"
mkdir "%TMPDIR%" 2>nul

set "INSTALLER=%TMPDIR%\python-%PYTHON_FULL_VERSION%.exe"

set "DOWNLOAD_URL=%WIN_INSTALLER_URL%"
if "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "DOWNLOAD_URL=%WIN_INSTALLER_URL_ARM%"

where curl >nul 2>&1
if %errorlevel%==0 (
    echo [INFO] 使用 curl 下载...
    curl -fSL --progress-bar -o "%INSTALLER%" "%DOWNLOAD_URL%"
    if not errorlevel 1 goto :run_installer
    echo [WARN] 官方源下载失败，尝试镜像源...
    curl -fSL --progress-bar -o "%INSTALLER%" "%WIN_INSTALLER_URL_BACKUP%"
    if not errorlevel 1 goto :run_installer
)

echo [INFO] 使用 PowerShell 下载...
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALLER%' -UseBasicParsing }" 2>nul
if not errorlevel 1 goto :run_installer

powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%WIN_INSTALLER_URL_BACKUP%' -OutFile '%INSTALLER%' -UseBasicParsing }" 2>nul
if not errorlevel 1 goto :run_installer

echo [ERROR] 下载失败，请检查网络连接
echo [ERROR] 你可以手动下载: %DOWNLOAD_URL%
rmdir /s /q "%TMPDIR%" 2>nul
exit /b 1

:run_installer
echo [INFO] 正在静默安装 Python...
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1

if errorlevel 1 (
    echo [WARN] 静默安装失败，尝试被动模式安装...
    "%INSTALLER%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
)

rmdir /s /q "%TMPDIR%" 2>nul

set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"

call :try_python "python" && exit /b 0
call :try_python "py -%REQUIRED_VERSION%" && exit /b 0
call :try_python "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" && exit /b 0

echo [ERROR] 安装似乎成功，但无法验证。请重新打开终端后再试。
exit /b 1
