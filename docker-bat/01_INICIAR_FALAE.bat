@echo off
title FALAE - Iniciar Docker

cd /d "%~dp0.."

echo.
echo ==========================================
echo       INICIANDO O FALAE NO DOCKER
echo ==========================================
echo.

docker compose up -d

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel iniciar o FALAE.
    echo Verifique se o Docker Desktop esta aberto.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Containers iniciados com sucesso.
echo.

docker compose ps

echo.
pause