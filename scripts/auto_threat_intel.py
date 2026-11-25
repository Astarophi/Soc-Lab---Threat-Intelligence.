
"""
=========================================================
SOC LAB - AUTOMATED THREAT INTELLIGENCE MONITOR
=========================================================

Descrição:
Script desenvolvido em Python para monitorar continuamente
os logs de acesso do Nginx e identificar automaticamente
endereços IP públicos para investigação.

Funcionalidades:
- Monitoramento contínuo dos logs do Nginx.
- Extração de endereços IP dos registros JSON.
- Identificação e validação de IPs públicos.
- Controle de IPs já processados durante a execução.
- Verificação de resultados existentes no cache SQLite.
- Investigação automatizada utilizando VirusTotal e AbuseIPDB.
- Envio dos resultados consolidados ao Splunk via HEC.
- Armazenamento dos resultados no cache por 24 horas.
- Detecção de rotação ou substituição do arquivo de logs.

Fluxo de funcionamento:
Nginx -> Logs JSON -> Extração do IP -> Validação
-> Cache SQLite -> Threat Intelligence -> Splunk HEC -> SIEM

Integrações:
- threat_intel.py
- ti_cache.py
- VirusTotal
- AbuseIPDB
- Splunk Enterprise

Tecnologias:
- Python
- JSON
- IP Address Validation
- SQLite
- REST APIs
- Nginx
- Splunk HTTP Event Collector (HEC)

Projeto:
SOC Lab - Security Operations Center

Observação:
As configurações e credenciais são mantidas externamente.
Não publique tokens, chaves de API ou informações privadas.
=========================================================
"""

import json
import ipaddress
import time
import os

from threat_intel import (
    load_keys,
    investigate,
    send_to_splunk
)

from ti_cache import get_cached_ip, save_ip_cache


# CONFIGURAÇÕES
LOG_FILE = os.getenv(
    "LOG_FILE",
    "/var/log/nginx/juice-shop-access.log"
)

ENV_FILE = os.getenv(
    "TI_ENV_FILE",
    "/opt/juice-splunk/threat-intel.env"
)

CHECK_INTERVAL = 2

# IPs já tratados nesta execução
processed_ips = set()


def extract_public_ip(line):
    """Extrai e valida o IP público de um evento JSON."""
    try:
        event = json.loads(line)
        forwarded = event.get("forwarded_for", "")

        ip = forwarded.split(",")[0].strip()
        address = ipaddress.ip_address(ip)

        if not address.is_global:
            return None

        return str(address)

    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def process_ip(ip):
    """Investiga novos IPs e encaminha os resultados ao Splunk."""

    if ip in processed_ips:
        return

    # Evita reprocessar o mesmo IP nesta execução
    processed_ips.add(ip)

    cached = get_cached_ip(ip)

    if cached:
        print(f"[CACHE] {ip} já possui investigação válida.")
        return

    print(f"\n[INVESTIGACAO] Novo IP: {ip}")

    try:
        keys = load_keys(ENV_FILE)

        result = investigate(ip, keys)

        if not all(
            source.get("status") == "success"
            for source in result["sources"].values()
        ):
            print(f"[AVISO] Investigação incompleta: {ip}")
            return

        send_to_splunk(result)

        save_ip_cache(ip, result)

        print(f"[OK] {ip} investigado e enviado ao Splunk.")

    except Exception as error:
        print(f"[ERRO] Falha ao investigar {ip}: {error}")


def monitor_log():
    """Monitora novos registros gerados pelo Nginx."""

    print("Monitor automático de Threat Intelligence iniciado.")
    print("Aguardando novos acessos no Nginx...")

    while not os.path.exists(LOG_FILE):
        time.sleep(2)

    log = open(LOG_FILE, "r")
    log.seek(0, os.SEEK_END)

    current_inode = os.fstat(log.fileno()).st_ino

    while True:

        try:
            line = log.readline()

            if line:
                ip = extract_public_ip(line)

                if ip:
                    process_ip(ip)

                continue

            time.sleep(CHECK_INTERVAL)

            # Detecta rotação ou recriação do arquivo
            try:
                new_inode = os.stat(LOG_FILE).st_ino

                if new_inode != current_inode:
                    print("[INFO] Arquivo de log substituído. Reabrindo.")

                    log.close()
                    log = open(LOG_FILE, "r")
                    current_inode = os.fstat(log.fileno()).st_ino

            except FileNotFoundError:
                continue

        except Exception as error:
            print(f"[ERRO] Monitor: {error}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor_log()
