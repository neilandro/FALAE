@echo off
title FALAE - Status Docker

cd /d "%~dp0.."

echo.
echo ==========================================
echo          STATUS DO FALAE
echo ==========================================
echo.

docker compose ps

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel consultar o Docker.
    echo Verifique se o Docker Desktop esta aberto.
    echo.
    pause
    exit /b 1
)

echo.
pause