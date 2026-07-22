@echo off
title FALAE - Reiniciar Docker

cd /d "%~dp0.."

echo.
echo ==========================================
echo       REINICIANDO O FALAE NO DOCKER
echo ==========================================
echo.

docker compose restart

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel reiniciar os containers.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Containers reiniciados com sucesso.
echo.

docker compose ps

echo.
pause