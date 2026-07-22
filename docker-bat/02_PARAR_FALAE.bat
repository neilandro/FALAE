@echo off
title FALAE - Parar Docker

cd /d "%~dp0.."

echo.
echo ==========================================
echo        PARANDO O FALAE NO DOCKER
echo ==========================================
echo.

docker compose stop

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel parar os containers.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Containers parados com seguranca.
echo Os containers e os volumes continuam preservados.
echo.

pause