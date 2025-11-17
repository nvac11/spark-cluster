# Définit le nom d'hôte pour la session PowerShell actuelle
$hostname = $env:COMPUTERNAME
$env:HOSTNAME = $hostname 

if (-Not (Test-Path "master.ip")) {
    Write-Output "➡ MASTER = $hostname"
    Set-Content -Path "master.ip" -Value $hostname
    # Définit les variables pour la session actuelle
    $env:SPARK_MODE = "master"
    $env:SPARK_MASTER_URL = ""
} else {
    $master = Get-Content master.ip
    Write-Output "➡ WORKER → Master = $master"
    # Définit les variables pour la session actuelle
    $env:SPARK_MODE = "worker"
    $env:SPARK_MASTER_URL = "spark://$master:7077"
}

# Ajout de l'étape de build
docker compose build
docker compose up -d