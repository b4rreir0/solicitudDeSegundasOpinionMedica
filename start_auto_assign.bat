@echo off
echo ========================================
echo    SERVICIO DE ASIGNACION AUTOMATICA
echo ========================================
echo.
echo Iniciando servicio cada 30 segundos...
echo Presiona Ctrl+C para detener
echo.

python manage.py asignar_solicitudes --interval 30

pause
