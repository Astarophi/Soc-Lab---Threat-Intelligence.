
"""
=========================================================
SOC LAB - THREAT INTELLIGENCE
=========================================================

Descrição:
Script desenvolvido em Python para investigação e
enriquecimento de endereços IP públicos utilizando
fontes externas de Threat Intelligence.

Funcionalidades:
- Recebimento de endereço IP para investigação.
- Validação de endereços IP públicos.
- Consulta à API do VirusTotal.
- Consulta à API do AbuseIPDB.
- Consolidação dos resultados das duas fontes.
- Consulta e armazenamento de resultados em cache SQLite.
- Cache com validade de 24 horas.
- Envio dos resultados ao Splunk Enterprise via HEC.

Fontes de Threat Intelligence:
- VirusTotal
- AbuseIPDB

Fluxo de funcionamento:
IP -> Validação -> Cache SQLite -> APIs de Threat Intelligence
-> Consolidação dos resultados -> Splunk HEC -> Splunk SIEM

Tecnologias:
- Python
- REST APIs
- JSON
- SQLite
- VirusTotal
- AbuseIPDB
- Splunk Enterprise
- HTTP Event Collector (HEC)

Projeto:
SOC Lab - Security Operations Center

Segurança:
As chaves de API, tokens e endereços internos devem
ser configurados externamente, nunca publicados no código.
=========================================================
"""

import json
import os
import ipaddress
import urllib.request
import urllib.parse
import urllib.error
import ssl

from datetime import datetime, timezone
from ti_cache import get_cached_ip, save_ip_cache


# CONFIGURAÇÕES
ENV_FILE = os.getenv(
    "TI_ENV_FILE",
    "/opt/juice-splunk/threat-intel.env"
)

HEC_TOKEN_FILE = os.getenv(
    "TOKEN_FILE",
    "/opt/juice-splunk/hec.env"
)

HEC_URL = os.getenv("HEC_URL")

INDEX = "main"
SOURCE = "threat-intel:ip-enrichment"
HOST = "juicelab"

# Contexto SSL utilizado no ambiente de laboratório.
SSL_CONTEXT = ssl._create_unverified_context()


def load_keys(file_path):
    """Carrega configurações e chaves de arquivos externos."""
    keys = {}

    with open(file_path, "r") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                keys[key] = value

    return keys


def validate_ip(ip):
    """Valida o endereço IP e aceita somente IPs públicos."""
    address = ipaddress.ip_address(ip)

    if not address.is_global:
        raise ValueError("O IP precisa ser público.")

    return str(address)


def virustotal(ip, key):
    """Consulta estatísticas de reputação no VirusTotal."""
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"

    request = urllib.request.Request(
        url,
        headers={"x-apikey": key}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read())

    stats = data["data"]["attributes"]["last_analysis_stats"]

    return {
        "malicious": stats.get("malicious", 0),
        "suspicious": stats.get("suspicious", 0),
        "harmless": stats.get("harmless", 0),
        "undetected": stats.get("undetected", 0)
    }


def abuseipdb(ip, key):
    """Consulta informações de abuso no AbuseIPDB."""
    params = urllib.parse.urlencode({
        "ipAddress": ip,
        "maxAgeInDays": "90"
    })

    url = f"https://api.abuseipdb.com/api/v2/check?{params}"

    request = urllib.request.Request(
        url,
        headers={
            "Key": key,
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read())

    result = data["data"]

    return {
        "abuse_confidence_score": result.get("abuseConfidenceScore"),
        "total_reports": result.get("totalReports"),
        "country": result.get("countryCode"),
        "isp": result.get("isp")
    }


def investigate(ip, keys):
    """Consolida os resultados das fontes de Threat Intelligence."""
    result = {
        "event_type": "threat_intelligence",
        "ip": ip,
        "investigation_time": datetime.now(timezone.utc).isoformat(),
        "sources": {}
    }

    sources = [
        ("virustotal", virustotal, "VT_API_KEY"),
        ("abuseipdb", abuseipdb, "ABUSEIPDB_API_KEY")
    ]

    for name, function, key_name in sources:
        try:
            result["sources"][name] = {
                "status": "success",
                "data": function(ip, keys[key_name])
            }

        except urllib.error.HTTPError as error:
            result["sources"][name] = {
                "status": "error",
                "http_code": error.code
            }

        except Exception as error:
            result["sources"][name] = {
                "status": "error",
                "message": str(error)
            }

    return result


def send_to_splunk(event):
    """Envia o resultado da investigação ao Splunk via HEC."""
    if not HEC_URL:
        raise RuntimeError("Configure a variável de ambiente HEC_URL.")

    keys = load_keys(HEC_TOKEN_FILE)
    token = keys.get("HEC_TOKEN")

    if not token:
        raise RuntimeError("Token HEC não encontrado.")

    payload = {
        "event": event,
        "index": INDEX,
        "sourcetype": "_json",
        "source": SOURCE,
        "host": HOST
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        HEC_URL,
        data=data,
        headers={
            "Authorization": f"Splunk {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        context=SSL_CONTEXT,
        timeout=15
    ) as response:

        response_data = json.loads(
            response.read().decode("utf-8")
        )

        if response_data.get("code") != 0:
            raise RuntimeError(f"Erro HEC: {response_data}")

        print("\n[OK] Evento enviado ao Splunk!")


def main():
    """Executa o processo completo de investigação do IP."""
    ip = input("Digite o IP público para investigar: ").strip()

    try:
        ip = validate_ip(ip)

        cached = get_cached_ip(ip)

        if cached:
            print("\n[CACHE] Resultado encontrado. Nenhuma API foi consultada.")
            result = cached
            result["cache_hit"] = True

        else:
            print("\n[API] Consultando VirusTotal e AbuseIPDB...")
            keys = load_keys(ENV_FILE)
            result = investigate(ip, keys)

            if all(
                source.get("status") == "success"
                for source in result["sources"].values()
            ):
                save_ip_cache(ip, result)
                print("[CACHE] Resultado salvo por 24 horas.")
            else:
                print("[AVISO] Consulta incompleta. Resultado não armazenado.")

            result["cache_hit"] = False

        print("\n--- RESULTADO CONSOLIDADO ---")
        print(json.dumps(result, indent=4, ensure_ascii=False))

        send_to_splunk(result)

    except ValueError as error:
        print(f"\nErro: {error}")

    except Exception as error:
        print(f"\nFalha na execução: {error}")


if __name__ == "__main__":
    main()
