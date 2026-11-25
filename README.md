
# Scripts do SOC Lab

Esta pasta reúne os scripts Python utilizados na integração entre o Nginx, o Splunk Enterprise e as plataformas de Threat Intelligence.

## Arquivos

| Arquivo | Função |
|---|---|
| `forwarder.py` | Monitora o log de acesso do Nginx e encaminha novos eventos ao Splunk via HTTP Event Collector (HEC). |
| `threat_intel.py` | Realiza consultas de reputação de IP nas APIs VirusTotal e AbuseIPDB e envia os resultados ao Splunk. |
| `auto_threat_intel.py` | Monitora novos acessos, identifica IPs públicos e inicia automaticamente investigações de Threat Intelligence. |
| `ti_cache.py` | Gerencia o cache SQLite, armazenando resultados das investigações por 24 horas. |

## Fluxo de funcionamento

1. O usuário acessa a aplicação OWASP Juice Shop.
2. O Nginx registra a requisição em um arquivo JSON.
3. O `forwarder.py` encaminha os eventos HTTP ao Splunk.
4. O `auto_threat_intel.py` monitora os acessos e identifica IPs públicos.
5. O `threat_intel.py` consulta VirusTotal e AbuseIPDB.
6. O `ti_cache.py` evita consultas repetidas durante o período de validade do cache.
7. Os resultados são enviados ao Splunk para análise e visualização nos dashboards.

## Dependências

- Python 3
- SQLite
- Bibliotecas padrão do Python
- API Key do VirusTotal
- API Key do AbuseIPDB
- Splunk HTTP Event Collector (HEC)

## Segurança

As chaves de API, tokens HEC, arquivos de configuração com credenciais e bancos de dados locais não devem ser publicados neste repositório.

Os scripts disponibilizados representam a implementação utilizada no laboratório, com configurações adaptáveis ao ambiente de execução.
