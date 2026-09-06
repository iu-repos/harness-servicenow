# Plano de Provisionamento - Harness + ServiceNow

## Objetivo
Definir, de forma clara e executavel, as etapas para provisionar e integrar o ambiente local, a plataforma Harness e o ServiceNow para um fluxo de deploy com governanca de mudancas.

## Escopo
- Provisionamento local para desenvolvimento e validacao.
- Provisionamento na Harness para pipeline e integracoes.
- Provisionamento no ServiceNow para Change Management.
- Integracao ponta a ponta entre pipeline e change request.

## Visao Geral das Fases
1. Preparar ambiente local.
2. Configurar fundamentos na Harness.
3. Configurar fundamentos no ServiceNow.
4. Integrar Harness e ServiceNow.
5. Validar fluxo completo com testes.
6. Definir operacao, metricas e proxima expansao.

---

## 1) Provisionamento Local

### 1.1 Pre-requisitos
- Acesso ao repositorio no GitHub.
- Python 3.10+ instalado.
- Ambiente virtual local configurado.
- Conta com acesso a Harness e ServiceNow.
- Credenciais e tokens de integracao (armazenados de forma segura).

### 1.2 Estrutura de trabalho
- Clonar repositorio.
- Criar e ativar ambiente virtual.
- Instalar dependencias do projeto.
- Definir variaveis de ambiente para testes locais.

### 1.3 Itens de configuracao local
- Arquivo de variaveis de ambiente (exemplo: endpoint Harness, endpoint ServiceNow, credenciais de teste).
- Scripts utilitarios para:
  - validar conectividade com APIs.
  - disparar chamadas de teste.
  - registrar logs de execucao.

### 1.3.1 Agent especialista ServiceNow (CLI local)
- Arquivo: `servicenow_specialist_agent.py`
- Objetivo: validar conexao e executar operacoes basicas de desenvolvimento via API REST do ServiceNow.
- A conexao e feita por variaveis de ambiente (nao salve senha no codigo):
  - `SN_INSTANCE_URL` (default: `https://dev395848.service-now.com`)
  - `SN_USERNAME`
  - `SN_PASSWORD`

Exemplo de setup local:
1. Copie `.env.example` para `.env`.
2. Preencha usuario e senha da instancia.
3. Exporte as variaveis no terminal.

Exemplos de uso:
- Testar conexao:
  - `python servicenow_specialist_agent.py ping`
- Listar registros:
  - `python servicenow_specialist_agent.py list --table incident --limit 5`
- Criar registro (exemplo em `change_request`):
  - `python servicenow_specialist_agent.py create --table change_request --data "{\"short_description\":\"Mudanca via agent\",\"category\":\"software\"}"`

### 1.4 Entregaveis locais
- Ambiente funcional para execucao de scripts.
- Checklist de conectividade concluido.
- Evidencias basicas de teste (log/screenshot).

---

## 2) Provisionamento na Harness

### 2.1 Fundacoes da plataforma
- Criar ou selecionar Organization e Project.
- Definir ambientes (dev, hml, prod, se aplicavel).
- Definir politicas de acesso (RBAC) por perfil.

### 2.2 Conectores
- GitHub Connector para leitura do repositorio e webhook.
- Cloud Connector (exemplo AWS) caso exista deploy real.
- ServiceNow Connector para abertura e atualizacao de change.

### 2.3 Secrets e governanca
- Cadastrar segredos no Secret Manager da Harness.
- Mapear variaveis sensiveis para runtime sem expor no pipeline.
- Definir padrao de naming para conectores, secrets e pipelines.

### 2.4 Pipeline
- Criar pipeline com estagios:
  - Build/Validacao.
  - Pre-Deploy: criar Change Request no ServiceNow.
  - Gate de aprovacao (manual ou automatizado).
  - Deploy.
  - Pos-Deploy: atualizar status da mudanca.
- Configurar rollback e notificacoes.

### 2.5 Entregaveis Harness
- Conectores validados.
- Pipeline versionado e executavel.
- Evidencia de execucao com rastreabilidade.

---

## 3) Provisionamento no ServiceNow

### 3.1 Estrutura de ITSM
- Confirmar modulo de Change Management habilitado.
- Definir tipo de mudanca para automacao (normal, standard, emergency).
- Definir tabela/campos obrigatorios para abertura via API.

### 3.2 Usuarios e permissoes
- Criar conta tecnica para integracao Harness.
- Conceder papeis minimos necessarios para:
  - criar Change Request.
  - consultar status.
  - atualizar fechamento.

### 3.2.1 Recomendacao: usuario de integracao dedicado
Sim, e altamente recomendado criar um usuario de integracao dedicado no ServiceNow para conectar com o Harness. Usar o usuario admin nao e uma boa pratica, porque ele tem permissoes muito amplas e pode trazer riscos de seguranca ou auditoria.

#### Por que criar um usuario de integracao?
- Seguranca: voce limita os acessos apenas ao que o Harness precisa.
- Auditoria: fica claro nos logs que as acoes foram feitas pelo usuario de integracao, e nao por um administrador humano.
- Boas praticas: evita expor credenciais de contas privilegiadas.

#### Como configurar o usuario de integracao no ServiceNow
1. Crie um novo usuario no ServiceNow (ex.: harness_integration).
2. Defina uma senha segura para esse usuario.
3. Atribua papeis minimos necessarios:

- Normalmente, o papel itil ja permite criar e atualizar incidentes, problemas e mudancas.
- Se o Harness precisar de mais permissoes (ex.: acesso a tabelas especificas), voce adiciona conforme a necessidade.

4. Teste o login desse usuario diretamente no ServiceNow para garantir que funciona.
5. Cadastre esse usuario no Harness Connector:

- Username: harness_integration
- Password: referenciado via Secret no Harness.

Em resumo: crie um usuario de integracao dedicado no ServiceNow, com permissoes minimas necessarias, e use esse usuario no conector do Harness.

### 3.3 Regras e fluxo de aprovacao
- Configurar workflow de aprovacao (grupo aprovador, SLA, criterios).
- Definir estados permitidos na transicao automatizada.
- Definir padroes de descricao para auditoria.

### 3.4 API e seguranca
- Habilitar e validar endpoint REST para Change Request.
- Validar autenticacao e politica de expiracao de credenciais.
- Garantir logs de auditoria para chamadas de integracao.

### 3.5 Entregaveis ServiceNow
- Conta tecnica ativa e testada.
- Fluxo de aprovacao validado.
- API pronta para consumo da Harness.

---

## 4) Integracao Harness + ServiceNow

### 4.1 Mapeamento de campos
Definir correspondencia entre dados do pipeline e campos da mudanca:
- servico/aplicacao
- ambiente
- versao
- janela de mudanca
- risco/impacto
- plano de rollback

### 4.2 Contrato de integracao
- Payload padrao para criacao da mudanca.
- Payload padrao para atualizacao de status.
- Estrategia de retries e tratamento de erro.

### 4.3 Fluxo funcional esperado
1. Pipeline inicia.
2. Harness cria Change Request no ServiceNow.
3. ServiceNow retorna numero da mudanca.
4. Pipeline aguarda aprovacao conforme regra.
5. Deploy executa apos aprovacao.
6. Harness atualiza mudanca com resultado final.

### 4.4 Entregaveis da integracao
- Fluxo ponta a ponta validado.
- Numero da mudanca associado ao deployment.
- Evidencias de auditoria nos dois sistemas.

---

## 5) Validacao e Testes

### 5.1 Casos minimos
- Criacao de change com sucesso.
- Bloqueio de deploy sem aprovacao.
- Continuidade de deploy com aprovacao.
- Atualizacao final de status apos deploy.
- Cenarios de falha (timeout API, rejeicao, credencial invalida).

### 5.2 Evidencias
- Logs da execucao do pipeline.
- Registro da mudanca no ServiceNow.
- Capturas de tela para documentacao de processo.

### 5.3 Criterio de pronto
- Fluxo estavel em ambiente piloto.
- Time operacional apto a executar sem suporte externo.
- KPIs minimos definidos e medidos.

---

## 6) Operacao e Proximos Passos

### 6.1 Indicadores recomendados
- Lead time de mudanca ate deploy.
- Taxa de sucesso de deploy.
- Tempo medio de aprovacao.
- Volume de rollback.

### 6.2 Rotina operacional
- Revisao semanal de falhas e gargalos.
- Rotacao de credenciais tecnicas.
- Revisao trimestral de permissoes e compliance.

### 6.3 Escala
- Iniciar com 1 servico piloto.
- Expandir para outras squads apos estabilidade.
- Padronizar template de pipeline com etapa ServiceNow reutilizavel.

---

## Checklist de Execucao

### Local
- [ ] Ambiente virtual criado e ativo.
- [ ] Dependencias instaladas.
- [ ] Variaveis de ambiente configuradas.
- [ ] Teste de conectividade com Harness e ServiceNow.

### Harness
- [ ] Project e RBAC definidos.
- [ ] Connectors GitHub e ServiceNow configurados.
- [ ] Secrets cadastrados com seguranca.
- [ ] Pipeline com gate de mudanca criado.

### ServiceNow
- [ ] Conta tecnica criada com papeis minimos.
- [ ] Workflow de aprovacao configurado.
- [ ] API de Change validada.
- [ ] Auditoria habilitada.

### Integracao
- [ ] Mapeamento de campos validado.
- [ ] Fluxo create -> approve -> deploy -> close funcionando.
- [ ] Evidencias registradas.

## Responsaveis Sugeridos
- DevOps/Plataforma: Harness, pipeline e segredos.
- ITSM/Service Management: workflow e politicas no ServiceNow.
- Engenharia de Aplicacao: validacao funcional e criterios de deploy.
- Seguranca/Compliance: revisao de permissoes e auditoria.
