#!/bin/bash

# Détecte automatiquement la meilleure IP LAN
# Fonctionne sur Linux, Mac, Windows (Docker Desktop)

detect_ip() {
    if command -v ip >/dev/null 2>&1; then
        ip=$(ip route get 8.8.8.8 2>/dev/null | awk '/src/ {print $7}')
        if [[ -n "$ip" ]]; then
            echo "$ip"
            return
        fi
    fi

    if [[ "$OSTYPE" == "darwin"* ]]; then
        ip=$(ipconfig getifaddr en0 2>/dev/null)
        [[ -z "$ip" ]] && ip=$(ipconfig getifaddr en1 2>/dev/null)
        if [[ -n "$ip" ]]; then
            echo "$ip"
            return
        fi
    fi

    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    if [[ -n "$ip" ]]; then
        echo "$ip"
        return
    fi

    echo "127.0.0.1"
}

detect_ip
