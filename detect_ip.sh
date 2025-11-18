#!/bin/bash

# Détecte automatiquement la meilleure IP LAN de la machine
# Compatible Linux / MacOS / Windows Docker Desktop

detect_ip() {
    local ip

    ### --- Linux (méthode la plus fiable) ---
    if command -v ip >/dev/null 2>&1; then
        ip=$(ip route get 8.8.8.8 2>/dev/null | awk '{for(i=1;i<=NF;i++){if($i=="src"){print $(i+1); exit}}}')
        if [[ "$ip" =~ ^(10|192\.168|172\.(1[6-9]|2[0-9]|3[0-1]))\..* ]]; then
            echo "$ip"
            return
        fi
    fi

    ### --- MacOS (réseaux Wi-Fi / ethernet) ---
    if [[ "$OSTYPE" == "darwin"* ]]; then
        ip=$(ipconfig getifaddr en0 2>/dev/null)
        [[ -z "$ip" ]] && ip=$(ipconfig getifaddr en1 2>/dev/null)
        if [[ "$ip" =~ ^(10|192\.168|172\.(1[6-9]|2[0-9]|3[0-1]))\..* ]]; then
            echo "$ip"
            return
        fi
    fi

    ### --- Fallback Linux: hostname -I ---
    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    if [[ "$ip" =~ ^(10|192\.168|172\.(1[6-9]|2[0-9]|3[0-1]))\..* ]]; then
        echo "$ip"
        return
    fi

    ### --- Dernière option ---
    echo "127.0.0.1"
}

detect_ip
