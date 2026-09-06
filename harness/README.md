# Harness Pipelines (Demo)

Este diretorio contem um baseline para criar as pipelines da demo Harness + ServiceNow do zero.

## Arquivos
- pipelines/servicenow_demo_pipeline.yaml
- inputsets/servicenow_demo_inputset.yaml

## Pre-requisitos na Harness
1. Criar projeto e organization.
2. Garantir delegate online.
3. Criar os secrets de conta:
   - account.sn_integration_username
   - account.sn_integration_password

## Como importar
1. Abrir Harness.
2. Ir em Pipelines > Import YAML.
3. Importar pipelines/servicenow_demo_pipeline.yaml.
4. Ajustar orgIdentifier e projectIdentifier.
5. Salvar pipeline.
6. Abrir a pipeline salva e ir na aba Input Sets.
7. Clicar em New Input Set > Import YAML.
8. Importar inputsets/servicenow_demo_inputset.yaml.
9. Ajustar orgIdentifier e projectIdentifier.
10. Salvar e executar pipeline com esse input set.

## Fluxo da pipeline
1. Build Validation (pre-check).
2. Open Change In ServiceNow (POST change_request).
3. Approval Gate (Harness Approval).
4. Deploy Simulation.
5. Close Change In ServiceNow (PATCH em change_request).

## Observacoes
- O usuario de integracao no ServiceNow deve ter papel minimo para criar e atualizar change_request.
- Se o campo assignment_group nao existir no ambiente, remova do payload de criacao.
- Se o endpoint retornar erro de permissao, revise papeis no ServiceNow e os secrets da Harness.
