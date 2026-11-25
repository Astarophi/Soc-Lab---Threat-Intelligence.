# Scripts — SOC Lab

Esta pasta reúne a documentação dos scripts Python desenvolvidos para automatizar processos de coleta, integração e enriquecimento de eventos no laboratório SOC.

## Scripts desenvolvidos

### 1. Forwarder.py

Responsável por monitorar os registros de acesso gerados pelo Nginx e encaminhar automaticamente os eventos ao Splunk Enterprise por meio do HTTP Event Collector (HEC).

Principais funções:
- Leitura dos logs em formato JSON.
- Encaminhamento automático dos eventos.
- Integração entre a máquina Juice Lab e o Splunk.

### 2. Threat Intelligence

Scripts responsáveis pelo enriquecimento automatizado de endereços IP identificados nos registros da aplicação.

Integrações utilizadas:
- VirusTotal.
- AbuseIPDB.

Principais funções:
- Identificação de endereços IP públicos.
- Consulta de informações de reputação.
- Enriquecimento dos eventos com dados de Threat Intelligence.
- Envio dos resultados ao Splunk.
- Armazenamento em cache SQLite com validade de 24 horas, evitando consultas repetidas.

## Integração com o Splunk

Os scripts utilizam o HTTP Event Collector (HEC) para enviar os dados processados ao Splunk, permitindo centralizar as informações e utilizá-las em consultas SPL e dashboards.

## Observação

Os scripts fazem parte de um laboratório pessoal desenvolvido para fins educacionais e de prática em automação, monitoramento e investigação de eventos de segurança.
