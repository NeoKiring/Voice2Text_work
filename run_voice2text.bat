@echo off
chcp 65001 > nul
setlocal

cd /d %~dp0

if not exist .venv (
    py -3 -m venv .venv
)

call .venv\Scripts\activate.bat

if not exist .venv\.deps_installed (
    echo [INFO] 初回セットアップ: 依存パッケージをインストールします...
    python -m pip install --upgrade pip
    if errorlevel 1 goto install_error
    pip install -r requirements.txt
    if errorlevel 1 goto install_error
    type nul > .venv\.deps_installed
) else (
    echo [INFO] 依存パッケージはインストール済みです。スキップします。
)

python scripts\launch.py
goto end

:install_error
echo [ERROR] 依存パッケージのインストールに失敗しました。
echo [ERROR] ネットワークまたはプロキシ設定を確認してください。
exit /b 1

:end
endlocal
