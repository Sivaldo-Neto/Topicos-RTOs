# Checklist Detalhado Para Montar o Word da UPx

Este arquivo serve como guia manual para montar o documento final no Word usando o `Modelo do Projeto Escrito_s1.docx` e o conteúdo já produzido para o projeto `SISTEMA DE MONITORAMENTO E CONTROLE DE QUALIDADE DO AR COM RTOS`.

## 1. Arquivos que você vai usar

- `Modelo do Projeto Escrito_s1.docx`
- `Relatorio_UPx_Sistema_Qualidade_do_Ar_COM_RTOS.md`
- `Relatorio_UPx_RTOS.rtf` (opcional, se quiser abrir no Word e copiar trechos)
- `sistema_qualidade_ar\sistema_qualidade_ar.ino`
- Fotos da montagem
- Capturas da Serial do Arduino/ESP32
- Prints do display OLED, se possível
- Tabelas ou anotações dos testes

## 2. Estrutura geral que o Word precisa ter

O documento final precisa conter, nesta ordem:

1. Capa institucional no formato do modelo
2. Página com os nomes dos integrantes e título
3. Página de apresentação do trabalho com orientador
4. Sumário
5. `1 OBJETIVO GERAL`
6. `2 REVISÃO DE LITERATURA E ESTADO DA ARTE`
7. `3 OBJETIVOS ESPECÍFICOS`
8. `4 JUSTIFICATIVA`
9. `5 MATERIAIS E MÉTODOS`
10. `5.1 Proposta Final do Produto`
11. `5.1.1 Orçamento`
12. `5.1.2 Retorno Esperado`
13. `6 VALIDAÇÃO`
14. `6.1 Procedimento`
15. `6.2 Resultados`
16. `7 CONCLUSÃO`
17. `REFERÊNCIAS`

## 3. O que preencher na capa e identificação

No começo do documento, você deve revisar e preencher:

- Título do trabalho:
  `SISTEMA DE MONITORAMENTO E CONTROLE DE QUALIDADE DO AR COM RTOS`
- Líder do grupo
- Nome completo dos integrantes
- RA de cada integrante
- E-mail dos integrantes, se o modelo pedir
- Telefone, se o modelo pedir
- Nome do orientador:
  `Prof. Me. Lucas Nunes Monteiro`
- Cidade e ano:
  `Sorocaba/SP, 2026`
- Data de entrega
- Visto do orientador, se for deixar espaço

## 4. Como copiar o conteúdo para o Word

Use o `Modelo do Projeto Escrito_s1.docx` como base e vá substituindo apenas o texto explicativo do modelo pelo conteúdo real do projeto.

### 4.1 Objetivo geral

No capítulo `1 OBJETIVO GERAL`, deve entrar um texto curto, direto e técnico explicando:

- O que o sistema faz
- Em qual plataforma ele roda
- Qual o foco do monitoramento
- Qual o papel do FreeRTOS
- Qual a meta principal do projeto

O texto já preparado fala que o sistema:

- monitora temperatura e umidade
- usa ESP32 DevKit V1
- usa FreeRTOS
- controla aquecimento e ventilação
- demonstra gerenciamento determinístico de múltiplas tarefas

### 4.2 Revisão de literatura e estado da arte

No capítulo `2 REVISÃO DE LITERATURA E ESTADO DA ARTE`, o texto precisa mostrar:

- o que é RTOS
- por que o FreeRTOS é importante em sistemas embarcados
- o que os trabalhos-base mostram
- como isso se conecta com o seu projeto

Você deve mencionar, em texto corrido:

- FreeRTOS em sistemas embarcados
- escalonamento preemptivo
- filas, mutexes e sincronização
- trabalhos com FreeRTOS em Arduino/ESP32
- o livro `Hands-On RTOS with Microcontrollers`
- os materiais do professor

Importante:

- não deixar esse capítulo só como lista de links
- transformar as referências em argumentação
- conectar os autores com as decisões do projeto

### 4.3 Objetivos específicos

No capítulo `3 OBJETIVOS ESPECÍFICOS`, deve entrar uma lista clara das etapas do projeto. Deve conter:

- seleção do ESP32
- integração do DHT22
- integração do display OLED
- uso de relés para aquecedor e cooler
- criação das tasks no FreeRTOS
- uso de fila e mutex
- implementação da histerese
- implementação da task de emergência
- montagem da câmara de teste
- realização dos testes e validação

### 4.4 Justificativa

No capítulo `4 JUSTIFICATIVA`, o texto precisa responder:

- Qual problema o projeto resolve
- Por que é relevante academicamente
- Por que RTOS foi escolhido
- Qual o diferencial do sistema
- Qual a importância para formação do grupo

Também é importante citar:

- baixo custo da solução
- aplicação em automação e IoT
- valor didático do uso de multitarefa e prioridades

### 4.5 Materiais e métodos

No capítulo `5 MATERIAIS E MÉTODOS`, você precisa explicar:

- como o sistema foi construído
- quais componentes foram usados
- como o firmware foi organizado
- como o sistema atua no ambiente

#### 5.1 Proposta final do produto

Aqui deve entrar:

- descrição do protótipo
- função de cada componente
- visão geral do funcionamento
- explicação da arquitetura do firmware

Não esqueça de explicar:

- ESP32 como controlador principal
- DHT22 como sensor de temperatura e umidade
- OLED como interface local
- relé do aquecedor
- relé do cooler
- lógica com histerese
- modo de emergência

Também vale inserir:

- diagrama de blocos
- foto da montagem
- desenho das conexões

#### 5.1.1 Orçamento

Esse item precisa mostrar os custos de forma organizada.

A tabela deve incluir:

- nome do item
- especificação
- quantidade
- valor unitário ou total

Itens esperados:

- ESP32 DevKit V1
- DHT22
- OLED 0,96" I2C
- aquecedor/resistor cerâmico
- cooler
- módulo relé
- fonte
- caixa de isopor / estrutura
- protoboard e jumpers

#### 5.1.2 Retorno esperado

Aqui você precisa separar retorno:

- tangível
- intangível

Exemplos para esse projeto:

- Tangível:
  documentação técnica, protótipo funcional, base para estudos futuros
- Intangível:
  aprendizado em RTOS, embarcados, validação experimental, integração hardware/software

### 4.6 Validação

No capítulo `6 VALIDAÇÃO`, divida em:

- `6.1 Procedimento`
- `6.2 Resultados`

#### 6.1 Procedimento

Tem que explicar como o teste foi feito:

- calibração do sensor
- teste de controle para setpoint
- teste de distúrbio
- teste de emergência

Esse item deve parecer um roteiro de laboratório.

#### 6.2 Resultados

Aqui você deve colocar o que realmente aconteceu nos testes.

Incluir, se tiver:

- tabela de temperatura por tempo
- comportamento do aquecedor
- comportamento do cooler
- ativação do modo emergência
- estabilidade do sistema
- dificuldades encontradas

Se ainda não tiver o ensaio completo, deixe esse trecho preparado para preencher depois.

### 4.7 Conclusão

No capítulo `7 CONCLUSÃO`, você precisa fechar o relatório respondendo:

- o projeto atingiu o objetivo?
- o FreeRTOS ajudou?
- a arquitetura ficou funcional?
- o que deu certo?
- o que precisa melhorar?
- o que pode virar continuação?

Sugestões de continuação:

- usar controle PID
- salvar dados em cartão SD
- enviar dados por Wi-Fi/MQTT
- criar app ou dashboard
- fazer placa dedicada

### 4.8 Referências

As referências devem estar no final, padronizadas.

Verifique se aparecem:

- livro do FreeRTOS
- artigo do FreeRTOS no Arduino Uno
- artigo automotivo com FreeRTOS
- trabalho de portabilidade com RTOS
- materiais do professor
- links técnicos usados

Importante:

- revisar nomes dos autores
- revisar ano
- revisar título completo
- revisar link e data de acesso

## 5. O que não pode faltar no Word final

- título correto do projeto
- nomes do grupo
- orientador
- capítulos na ordem certa
- texto técnico coerente
- orçamento
- explicação da arquitetura do firmware
- metodologia de teste
- espaço ou preenchimento dos resultados
- referências

## 6. Itens visuais recomendados

Se possível, incluir:

- foto do protótipo montado
- foto da caixa/câmara de teste
- print da Serial mostrando leituras
- print do display OLED
- tabela de orçamento
- tabela de resultados
- diagrama em blocos do sistema

## 7. O que revisar antes de entregar

- ortografia e acentuação
- consistência entre texto e código
- nomes corretos dos componentes
- números do orçamento
- títulos iguais no sumário e no corpo
- atualização do sumário automático no Word
- paginação correta
- imagens legíveis
- referências completas

## 8. Ordem prática para você montar sem se perder

1. Abrir o `Modelo do Projeto Escrito_s1.docx`
2. Preencher capa e identificação
3. Copiar o conteúdo dos capítulos do relatório preparado
4. Ajustar o orçamento em tabela
5. Inserir imagens e diagramas
6. Preencher ou reservar `6.2 Resultados`
7. Revisar a conclusão
8. Revisar referências
9. Atualizar o sumário
10. Salvar em `.docx`
11. Exportar uma cópia em `.pdf`

## 9. Sugestão de nome final do arquivo

- `Relatorio_UPx_Sistema_Qualidade_do_Ar_COM_RTOS.docx`
- `Relatorio_UPx_Sistema_Qualidade_do_Ar_COM_RTOS.pdf`
