
"""
Módulo de cache de Threat Intelligence.

Armazena os resultados das investigações de IP em um banco SQLite,
evitando consultas repetidas às APIs VirusTotal e AbuseIPDB.

Cada resultado permanece válido por 24 horas.
"""

import sqlite3
import json
import os

from datetime import datetime, timezone, timedelta


# Caminho do banco de dados
DB_FILE = os.getenv(
    "CACHE_DB_FILE",
    "/opt/juice-splunk/threat-intel-cache.db"
)

# Tempo de validade do cache
CACHE_HOURS = 24


def initialize_cache():
    """Cria a tabela de cache caso ainda não exista."""

    with sqlite3.connect(DB_FILE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS ip_cache (
                ip TEXT PRIMARY KEY,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def get_cached_ip(ip):
    """Retorna a investigação armazenada, se ainda estiver válida."""

    initialize_cache()

    with sqlite3.connect(DB_FILE) as db:
        row = db.execute(
            "SELECT result, created_at FROM ip_cache WHERE ip = ?",
            (ip,)
        ).fetchone()

    if not row:
        return None

    created_at = datetime.fromisoformat(row[1])
    expiration = created_at + timedelta(hours=CACHE_HOURS)

    if datetime.now(timezone.utc) > expiration:
        return None

    return json.loads(row[0])


def save_ip_cache(ip, result):
    """Armazena ou atualiza o resultado da investigação."""

    initialize_cache()

    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_FILE) as db:
        db.execute("""
            INSERT OR REPLACE INTO ip_cache
            (ip, result, created_at)
            VALUES (?, ?, ?)
        """, (
            ip,
            json.dumps(result),
            created_at
        ))


if __name__ == "__main__":
    initialize_cache()
    print("Banco de cache criado com sucesso!")
