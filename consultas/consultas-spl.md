
# Consultas SPL — SOC Lab

Este documento reúne as consultas Search Processing Language (SPL) utilizadas no laboratório SOC Lab com Splunk Enterprise.

As pesquisas permitem monitorar os acessos à aplicação OWASP Juice Shop, analisar eventos HTTP, identificar endereços IP e visualizar os resultados de Threat Intelligence.

Todas as consultas utilizam o índice `main`.

---

## 1. Monitoramento de requisições HTTP

**Objetivo:** visualizar os acessos registrados pelo Nginx na aplicação Juice Shop.

```spl
index=main source="nginx:juice-shop-access"
| sort - _time
| table _time forwarded_for method uri status user_agent
```

**Campos apresentados:**
- `_time`: horário do evento.
- `forwarded_for`: endereço IP de origem informado no cabeçalho encaminhado.
- `method`: método HTTP utilizado.
- `uri`: rota requisitada.
- `status`: código de resposta HTTP.
- `user_agent`: navegador ou cliente utilizado.

## 2. Volume de requisições por IP

**Objetivo:** identificar a quantidade de requisições realizadas por cada endereço IP.

```spl
index=main source="nginx:juice-shop-access"
| stats count by forwarded_for
| sort - count
```

Permite visualizar quais endereços IP geraram mais eventos HTTP.

## 3. Distribuição dos códigos de resposta HTTP

**Objetivo:** visualizar a quantidade de respostas agrupadas por código HTTP.

```spl
index=main source="nginx:juice-shop-access"
| stats count by status
| sort - count
```

Essa consulta permite acompanhar respostas como:

- `200`: requisição bem-sucedida.
- `301` e `302`: redirecionamentos.
- `400`: requisição inválida.
- `401`: não autorizado.
- `403`: acesso proibido.
- `404`: recurso não encontrado.
- `500`: erro interno do servidor.

## 4. Distribuição dos métodos HTTP

**Objetivo:** identificar quais métodos HTTP são utilizados na aplicação.

```spl
index=main source="nginx:juice-shop-access"
| stats count by method
| sort - count
```

Permite analisar a frequência de métodos como GET, POST, PUT e DELETE.

## 5. Rotas mais acessadas

**Objetivo:** identificar os caminhos mais requisitados na aplicação.

```spl
index=main source="nginx:juice-shop-access"
| stats count by uri
| sort - count
```

Ajuda a visualizar quais recursos da aplicação recebem mais requisições.

## 6. Eventos de Threat Intelligence

**Objetivo:** consultar os eventos de enriquecimento de IP enviados ao Splunk.

```spl
index=main source="threat-intel:ip-enrichment"
| spath
| sort - _time
| table _time ip sources.virustotal.data.malicious sources.virustotal.data.suspicious sources.abuseipdb.data.abuse_confidence_score sources.abuseipdb.data.total_reports
```

A consulta apresenta os resultados das análises realizadas pelas plataformas VirusTotal e AbuseIPDB.

## 7. Análise de reputação dos IPs

**Objetivo:** apresentar os indicadores de reputação retornados pelas fontes de Threat Intelligence.

```spl
index=main source="threat-intel:ip-enrichment"
| spath
| table ip sources.virustotal.data.malicious sources.virustotal.data.harmless sources.virustotal.data.undetected sources.abuseipdb.data.abuse_confidence_score sources.abuseipdb.data.total_reports
```

**Indicadores:**
- `malicious`: detecções classificadas como maliciosas pelo VirusTotal.
- `harmless`: detecções classificadas como inofensivas.
- `undetected`: mecanismos que não detectaram classificação.
- `abuse_confidence_score`: pontuação de confiança de abuso do AbuseIPDB.
- `total_reports`: quantidade de denúncias registradas.

## 8. Geolocalização dos IPs investigados

**Objetivo:** extrair o país informado nos eventos de Threat Intelligence.

```spl
index=main source="threat-intel:ip-enrichment"
| rex field=_raw "\"country\":\s*\"(?<country>[^\"]+)\""
| sort 0 - _time
| dedup ip
| where isnotnull(country) AND country!=""
```

Essa consulta foi recuperada do histórico de desenvolvimento do dashboard geográfico.

O campo `country` é extraído dos eventos para permitir análises por país e utilização em visualizações geográficas.

**Observação:** a continuação da consulta original do mapa, incluindo o lookup de países, ainda precisa ser recuperada.

---

## 9. Fontes de dados do laboratório

| Source | Descrição |
|---|---|
| `nginx:juice-shop-access` | Registros de acesso HTTP da aplicação |
| `threat-intel:ip-enrichment` | Resultados de enriquecimento de IP |
| `/var/log/auth.log` | Eventos de autenticação do sistema |
| `/var/log/syslog` | Eventos gerais do sistema |

## 10. Dashboards SOC Lab

As consultas são utilizadas como base para as visualizações do Splunk Enterprise, incluindo:

- Monitoramento de requisições HTTP.
- Volume de eventos e acessos.
- Distribuição dos códigos HTTP.
- Identificação de endereços IP.
- Análise de reputação.
- Geolocalização dos IPs investigados.
- Monitoramento de eventos de Threat Intelligence.

---

## Observações

- As pesquisas utilizam o índice `main`.
- O período de tempo selecionado no Splunk influencia os resultados.
- Os eventos HTTP são enviados pelo forwarder Python por meio do HTTP Event Collector (HEC).
- Os eventos de Threat Intelligence são produzidos pelas integrações VirusTotal e AbuseIPDB.
- As consultas podem ser adaptadas conforme a evolução do laboratório.
