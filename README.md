# Soc-Lab---Threat-Intelligence.
Laboratório prático de SOC com Splunk SIEM, OWASP Juice Shop e Threat Intelligence.

## Sobre o projeto

Este projeto consiste no desenvolvimento de um laboratório prático de operações de segurança (SOC), com foco em monitoramento de aplicações web, coleta e análise de logs, investigação de atividades suspeitas e integração com fontes de Threat Intelligence.

O ambiente utiliza o Splunk Enterprise como SIEM para centralizar eventos, identificar comportamentos suspeitos e facilitar a investigação de endereços IP.

## Objetivos

- Implementar um ambiente de monitoramento utilizando Splunk Enterprise.
- Monitorar requisições HTTP em uma aplicação OWASP Juice Shop.
- Coletar e centralizar logs utilizando Nginx e Python.
- Integrar fontes de Threat Intelligence para enriquecimento de endereços IP.
- Investigar atividades suspeitas a partir dos registros coletados.
- Desenvolver dashboards para visualização e análise de eventos.

## Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Splunk Enterprise | SIEM e análise de eventos |
| OWASP Juice Shop | Aplicação web para testes |
| Nginx | Registro de requisições HTTP |
| Python | Automação e integração de dados |
| VirusTotal | Análise de reputação de IPs |
| AbuseIPDB | Consulta de denúncias de IPs |
| SQLite | Cache de consultas de Threat Intelligence |
| Docker | Execução da aplicação |
| Ubuntu Server | Sistema operacional |
| VirtualBox | Virtualização |
| Tailscale | Comunicação entre ambientes |

## Arquitetura do laboratório

O ambiente é composto por duas máquinas virtuais Ubuntu Server.

**VM 1 — SOC-LAB-Ubuntu**
- Splunk Enterprise.
- Recebimento e indexação de eventos.
- Consultas SPL e dashboards de monitoramento.

**VM 2 — juicelab**
- OWASP Juice Shop executado em Docker.
- Nginx para registro das requisições HTTP.
- Scripts Python para encaminhamento automático dos logs.
- Integração com VirusTotal e AbuseIPDB.
- Tailscale para comunicação entre as máquinas.

## Coleta e processamento de logs

As requisições realizadas na aplicação OWASP Juice Shop são registradas pelo Nginx em formato JSON.

Um script desenvolvido em Python realiza o encaminhamento automático desses registros para o Splunk por meio do HTTP Event Collector (HEC).

Dessa forma, os eventos ficam centralizados e disponíveis para consultas e investigação.

## Threat Intelligence

O laboratório possui integração automatizada com duas fontes de inteligência de ameaças:

- **VirusTotal:** consulta informações de reputação e indicadores associados aos endereços IP.
- **AbuseIPDB:** consulta registros de denúncias e indicadores de atividade abusiva.

Os IPs públicos identificados nos registros são processados por scripts Python, que consultam essas fontes e encaminham os resultados ao Splunk.

Também foi implementado um mecanismo de cache utilizando SQLite, com validade de 24 horas, para evitar consultas repetidas.

## Monitoramento e dashboards

Foram desenvolvidos dashboards no Splunk para facilitar a visualização e investigação dos eventos coletados, incluindo:

- Volume de requisições HTTP.
- Endereços IP de origem.
- Países e informações de geolocalização.
- Atividades potencialmente suspeitas.
- Informações de reputação dos IPs.
- Dados de Threat Intelligence.

## Aprendizados práticos

Durante o desenvolvimento do projeto, foram aplicados conhecimentos de:

- Administração de sistemas Linux.
- Configuração de serviços e infraestrutura.
- Monitoramento de aplicações web.
- Coleta, tratamento e análise de logs.
- Consultas utilizando Search Processing Language (SPL).
- Automação e integração com Python.
- Investigação de endereços IP.
- Conceitos de SIEM, SOC e Threat Intelligence.
