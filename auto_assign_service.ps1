# Script PowerShell para ejecutar asignación automática cada 30 segundos
# Ejecutar con: powershell -ExecutionPolicy Bypass -File auto_assign_service.ps1

param(
    [int]$Interval = 30,
    [string]$LogFile = "auto_assign.log"
)

Write-Host "🚀 Iniciando servicio de asignación automática..."
Write-Host "⏰ Intervalo: $Interval segundos"
Write-Host "📝 Log: $LogFile"
Write-Host "🛑 Presiona Ctrl+C para detener"
Write-Host ""

# Función para escribir log con timestamp
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry
}

# Función para ejecutar asignación
function Execute-Assignment {
    try {
        Write-Log "🔄 Iniciando ciclo de asignación..."
        
        # Ejecutar el comando Django
        $result = python manage.py asignar_solicitudes --once 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ Asignación completada exitosamente"
            if ($result -match "(\d+) solicitudes asignadas") {
                $count = $matches[1]
                if ($count -gt 0) {
                    Write-Log "📋 $count solicitudes fueron asignadas"
                }
            }
        } else {
            Write-Log "❌ Error en la asignación: $result"
        }
    }
    catch {
        Write-Log "❌ Excepción durante la asignación: $($_.Exception.Message)"
    }
}

# Inicializar log
Write-Log "🚀 Servicio de asignación automática iniciado"

try {
    while ($true) {
        $startTime = Get-Date
        
        # Ejecutar asignación
        Execute-Assignment
        
        # Calcular tiempo transcurrido
        $elapsed = ((Get-Date) - $startTime).TotalSeconds
        $sleepTime = [Math]::Max(0, $Interval - $elapsed)
        
        if ($sleepTime -gt 0) {
            Write-Log "⏱️  Esperando $sleepTime segundos hasta el próximo ciclo..."
            Start-Sleep -Seconds $sleepTime
        }
    }
}
catch {
    Write-Log "🛑 Servicio detenido: $($_.Exception.Message)"
}
finally {
    Write-Log "🔚 Servicio de asignación automática finalizado"
}
