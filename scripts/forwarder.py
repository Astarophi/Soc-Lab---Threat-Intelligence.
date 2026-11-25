
"""
=========================================================
SOC LAB - NGINX TO SPLUNK FORWARDER
=========================================================

Descrição:
Script desenvolvido em Python para monitorar os logs
de acesso do Nginx e encaminhar automaticamente os
eventos ao Splunk Enterprise.

Funcionalidades:
- Monitoramento contínuo dos logs do Nginx.
- Leitura de eventos em formato JSON.
- Encaminhamento dos registros via Splunk HTTP Event Collector (HEC).
- Identificação de rotação do arquivo de logs.
- Tratamento de erros durante o processamento.
- Envio de eventos para indexação no Splunk.

Fluxo de funcionamento:
Nginx -> Logs JSON -> Python Forwarder -> Splunk HEC -> Splunk SIEM

Tecnologias:
- Python
- Nginx
- JSON
- HTTP Event Collector (HEC)
- Splunk Enterprise

Projeto:
SOC Lab - Security Operations Center

Observação:
As configurações de conexão e autenticação são
mantidas externamente, evitando a exposição de
informações sensíveis no código-fonte.
=========================================================
"""

import json
import os
import ssl
import time
import urllib.request

# Continuação do código...
