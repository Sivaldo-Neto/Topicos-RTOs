# Usina de Projetos Experimentais (UPx)
## Projeto – Relatório Final

### IDENTIFICAÇÃO

| NO    | Nome                         | e-mail / contato |
|-------|------------------------------|------------------|
| 211653 | Bruno Bagatella              | bruno.bagatella@gmail.com — Tel. 15 99698-4173 |
| 211911 | Felipe Augusto Santos Piovani | Tel. 15 98804-8326 |
| 222608 | Guilherme da Silva Barros     | Tel. 15 99830-3002 |
| 223466 | Lucas Rogério do Couto        | lucasrcouto9@hotmail.com — Tel. 15 99721-2528 |
| 212181 | Sivaldo Castro Araújo Neto    | Tel. 15 98834-9087 |

**TÍTULO DO TRABALHO:** SISTEMA DE MONITORAMENTO E CONTROLE DE QUALIDADE DO AR COM RTOS  

**LÍDER DO GRUPO:** _(preencher)_  

**ORIENTADOR(A):** Prof. Me. Lucas Nunes Monteiro  

**Data da entrega:** __/__/2026  

**Visto do(a) orientador(a):** _________________________  

---

*Primeira parte do projeto experimental apresentado ao Centro Universitário Facens, como exigência parcial para a disciplina de Usina de Projetos Experimentais (UPx).*  

**Sorocaba/SP, 2026**

---

## SUMÁRIO

1. Objetivo geral  
2. Revisão de literatura e estado da arte  
3. Objetivos específicos  
4. Justificativa  
5. Materiais e métodos  
   - 5.1 Proposta final do produto  
   - 5.1.1 Orçamento  
   - 5.1.2 Retorno esperado  
6. Validação  
   - 6.1 Procedimento  
   - 6.2 Resultados  
7. Conclusão  
Referências  

---

## 1 OBJETIVO GERAL

Desenvolver um sistema embarcado de monitoramento e controle de qualidade do ar em ambiente de laboratório, com foco em **temperatura** e **umidade relativa**, utilizando o sistema operacional de tempo real **FreeRTOS** em microcontrolador **ESP32 DevKit V1**. O trabalho visa demonstrar a aplicabilidade de um RTOS no gerenciamento determinístico de **múltiplas tarefas concorrentes** (sensor, controle, interface humana e segurança térmica) em automação ambiental de pequena escala, com **malha de controle por histerese** em torno de um **setpoint de 35 °C** e atuação via **módulo de relé** (aquecedor e cooler/resfriamento).

---

## 2 REVISÃO DE LITERATURA E ESTADO DA ARTE

Sistemas embarcados com RTOS permitem escalar a complexidade do firmware sem sacrificar, de forma tão acentuada, a **previsibilidade temporal**: o escalonador **preemptivo** do FreeRTOS permite que tarefas de maior prioridade atendam a restrições críticas — por exemplo, **desligar o aquecimento** em condição de sobretemperatura — enquanto tarefas de menor prioridade tratam de **interface** e **telemetria** (TANENBAUM, 2015). O **FreeRTOS** é amplamente adotado em microcontroladores de baixo custo e oferece um núcleo enxuto, com primitivas como **filas**, **semáforos** e **mutexes**, adequadas a comunicação segura entre tarefas (BARRY, 2022).

Em plataformas com recursos limitados, Spohn et al. (2019) avaliam o desempenho do FreeRTOS no **Arduino Uno** e discutem **limites de memória e processamento** ao usar um kernel; o trabalho reforça a importância de **dimensionar stacks** e de definir com clareza o **fluxo de dados** entre tarefas. Back (2018), em trabalho de conclusão no repositório da Ânima, relata **portabilidade** usando FreeRTOS em duas plataformas distintas e **alto reaproveitamento de código** — alinhado à decisão de separar **aplicação** (lógica de setpoint, estados e tarefas) de **drivers** (GPIO, I2C, leitura DHT).

No contexto automotivo, Anacleto e Perez (2017) apresentam estudo de caso com FreeRTOS em aplicação de **controle de cruzeiro**, destacando boas práticas de **concorrência** e uso de RTOS em sistemas com restrições de tempo. Materiais didáticos e exemplos com **filas** e **ESP32** (MakerHero; FBSeletronica) sustentam o uso de filas para **desacoplar** a produção de dados (sensor) do consumo (controle).

O livro *Hands-On RTOS with Microcontrollers* (Amos et al.) sistematiza o desenvolvimento de firmware em tempo real e a integração com microcontroladores, complementando a base teórica da disciplina **Tópicos Especiais em Engenharia Mecatrônica I** (análise em frequência, implementação digital de controle e RTOS), conforme plano de aprendizagem da componente curricular.

---

## 3 OBJETIVOS ESPECÍFICOS

1. Selecionar o **ESP32 DevKit V1** e o ambiente **Arduino** com FreeRTOS integrado, organizando o firmware em **quatro tarefas** com prioridades distintas.  
2. Integrar o sensor **DHT22** (temperatura e umidade), display **OLED 0,96" I2C** (controlador SSD1306) e **módulo de relé de dois canais** (aquecedor 12 V e cooler 12 V).  
3. Implementar comunicação inter-tarefas com **fila FreeRTOS** (`xQueue`) transportando uma estrutura com temperatura e umidade da `Task_Sensor` para a `Task_Control`; usar **mutex** (`xSemaphoreCreateMutex`) para acesso exclusivo ao barramento **I2C** do OLED.  
4. Implementar controle em malha fechada com **banda morta por histerese**: abaixo de **34 °C** prioriza aquecimento; acima de **36 °C** prioriza resfriamento; entre **34 °C e 36 °C** desliga ambos; **setpoint nominal 35 °C**.  
5. Implementar `Task_Emergency` (**prioridade máxima**) para temperatura **≥ 50 °C**: desliga aquecedor, liga cooler, sinaliza **EMERGENCIA** no display e na serial e impede a atuação normal da `Task_Control` enquanto persistir a condição crítica (`gEmergencia`).  
6. Montar **câmara** laboratorial (ex.: caixa térmica em isopor ~10 L) e executar ensaios de validação segundo o capítulo 6.  
7. Demonstrar o papel do RTOS na **preempção** e no **isolamento de responsabilidades** (sensor × controle × HMI × segurança).

---

## 4 JUSTIFICATIVA

**Problemas que o projeto ajuda a endereçar:** em laboratórios de ensino e em protótipos de IoT, manter a temper estável em pequeno volume **sem automação** tende a gerar variabilidade e risco térmico; a solução proposta é **reprodutível**, de **custo acessível** (faixa de aproximadamente **R$ 200,00** no orçamento preliminar) e alinhada à demanda por sistemas embarcados em **Indústria 4.0**.

**Potencialidades e oportunidades:** o ESP32 oferece **Wi-Fi/Bluetooth** para extensões futuras (telemetria, nuvem, MQTT); o firmware estruturado em tarefas facilita **evolução** (PID, registro em SD, alarmes remotos).

**Importância e contexto:** o controle ambiental confinado fundamenta processos didáticos e simula restrições de **câmaras** e estufas em escala reduzida.

**Origem da ideia:** integrar os requisitos da UPx e da disciplina de **RTOS/controle em tempo real** com um caso concreto de **qualidade do ar** (T e UR) monitorada e atuada.

**Inovação / diferencial:** arquitetura **multitarefa** com **prioridade máxima para emergência térmica**; a segurança não depende de um único `loop` bloqueante — a `Task_Emergency` age de forma coordenada com GPIO e com o bloqueio do controle normal durante alarme.

**Formação:** articula programação embarcada, **I2C**, sensoriamento, atuação a relé e **engenharia de software concorrente**.

---

## 5 MATERIAIS E MÉTODOS

### 5.1 Proposta final do produto

O produto é um **protótipo** de monitoramento e controle térmico da qualidade do ar confinado. O firmware roda no **ESP32** com **FreeRTOS**; após o `setup()`, o `loop()` do Arduino **não executa lógica de aplicação** (no código entregue, apenas chama `vTaskDelete(NULL)`), havendo **quatro tarefas** cooperando por **fila** e **mutex**.

#### Arquitetura de software implementada (firmware `sistema_qualidade_ar.ino`)

| Elemento | Descrição |
|----------|-----------|
| **Fila `xFilaDados`** | Capacidade **5** elementos; tipo `DadosSensor_t { float temperatura; float umidade; }`. A `Task_Sensor` envia leituras válidas; a `Task_Control` recebe com espera **bloqueante**. |
| **Mutex `xMutexI2C`** | Protege o acesso ao **SSD1306** (I2C) entre `Task_Display` e atualizações forçadas em `Task_Emergency`. |
| **`Task_Sensor`** | Prioridade **2**, stack **2048** words, **Core 1**; período **2 s** (`vTaskDelayUntil`); lê DHT22; atualiza `gTemperatura` e `gUmidade` (volatile); envia à fila (timeout 100 ms se fila cheia). |
| **`Task_Control`** | Prioridade **3**; ao receber dados, se **não** houver emergência, aplica **histerese**: `T < 34 °C` → aquecedor ligado (relé ativo em **LOW**), cooler desligado; `T > 36 °C` → aquecedor desligado, cooler ligado; caso contrário ambos desligados. |
| **`Task_Display`** | Prioridade **1**, stack **3072**; atualização **1 s**; exibe modo normal ou **EMERGENCIA**. |
| **`Task_Emergency`** | Prioridade **4** (máxima); a cada **500 ms** testa `gTemperatura ≥ 50 °C`; força **OFF** no aquecedor e **ON** no cooler; seta `gEmergencia`; ao normalizar, limpa a flag. |

#### Pinagem (implementação)

| Função | GPIO |
|--------|------|
| DHT22 | **4** |
| Relé aquecedor | **26** |
| Relé cooler | **27** |
| I2C SDA / SCL | **21** / **22** |
| OLED (SSD1306) | Endereço **0x3C** |
| Serial (depuração) | **115200** baud |

#### Diagrama lógico (texto)

```
DHT22 → Task_Sensor → [xQueue] → Task_Control → GPIO (relés)
         ↓ (volatile)
    gTemperatura / gUmidade  →  Task_Display / Task_Emergency  →  OLED (mutex I2C)
```

*Incluir no relatório final, se exigido: fotos da montagem, esquemático elétrico e capturas de tela da Serial.*

### 5.1.1 Orçamento

Valores **indicativos** (ajustar com notas fiscais na versão final):

| Item | Especificação | Qtd. | Valor (R$) |
|------|---------------|------|------------|
| Microcontrolador | ESP32 DevKit V1 | 1 | 45,00 |
| Sensor | DHT22 | 1 | 18,00 |
| Display | OLED 0,96" I2C | 1 | 18,00 |
| Aquecedor | Cerâmica 10 W 12 V | 1 | 12,00 |
| Ventilador | Cooler 40 mm 12 V | 1 | 15,00 |
| Driver | Módulo relé 5 V 2 canais | 1 | 15,00 |
| Estrutura | Caixa isopor ~10 L + acabamento | 1 | 25,00 |
| Fonte | 12 V 3 A bivolt | 1 | 35,00 |
| Diversos | Protoboard, jumpers | 1 | 15,00 |
| **Total** | | | **198,00** |

Na **entrega final**, conforme modelo da UPx, discriminar também **custos de implantação** da versão definitiva e **alterações de infraestrutura**, se houver.

### 5.1.2 Retorno esperado

- **Tangível:** protótipo documentado e firmware versionado; base para publicações/relatórios e portfólio; possível extensão com **telemetria** (Wi-Fi).  
- **Intangível:** aprendizado em **RTOS**, depuração serial, projeto seguro (emergência térmica) e trabalho em equipe.  
- **No tempo:** benefício educacional no semestre; benefício técnico médio prazo (TCC, emprego, competições).

---

## 6 VALIDAÇÃO

### 6.1 Procedimento

1. **Calibração:** comparar leituras do DHT22 com termômetro de referência em pelo menos três condições (ex.: banho de gelo fundente **0 °C** com metodologia adequada; **ambiente ~25 °C**; faixa elevada **~50 °C** com supervisão). Registrar desvio; eventual **compensação** no software é melhoria futura.  
2. **Controle:** configurar operação em torno de **35 °C**; medir **tempo** para aproximar-se da faixa a partir de ~25 °C; registrar **overshoot** e **estabilidade** em regime.  
3. **Distúrbio:** abrir a tampa da câmara por **10 s**; medir **tempo de recuperação**.  
4. **RTOS / emergência:** com segurança, verificar disparo **≥ 50 °C**; confirmar desligamento do aquecedor, acionamento do cooler e mensagem **EMERGENCIA**; confirmar que o **controle ordinário** permanece inibido com `gEmergencia == true`.  

**Critério de aceitação sugerido:** temperatura dentro de **±2 °C** do setpoint em **≥ 95%** do tempo em regime, **e** validação qualitativa (**histerese** e **emergência**).

### 6.2 Resultados

*(Preencher após os ensaios: tabelas, gráficos T(t), fotos, prints da Serial e do OLED em modo normal e em emergência.)*

---

## 7 CONCLUSÃO

*(Redigir ao final do ciclo: atendimento aos objetivos; o que funcionou bem — modularidade em tarefas, fila, mutex; dificuldades — ruído do DHT22, inércia térmica da câmara, afinação da histerese; contribuições para a formação do grupo; trabalhos futuros — PID, datalogger, MQTT, PCB.)*

---

## REFERÊNCIAS

AMOS, B.; YUILL, J.; LINDER, P. *Hands-On RTOS with Microcontrollers: Create high-performance, real-time embedded systems using FreeRTOS, STM32 MCUs and SEGGER*. Packt Publishing, 2020.

ANACLETO, V. L.; PEREZ, A. L. F. Avaliação do uso do sistema operacional embarcado FreeRTOS em aplicações automotivas. *Anais do Computer on the Beach*, v. 7, p. 337–346, 2017. DOI 10.14210/cotb.v0n0.p337-346. Disponível em: https://periodicos.univali.br/index.php/acotb/article/view/10743. Acesso em: 14 abr. 2026.

BACK, M. Sistema embarcado com RTOS: uma abordagem prática e voltada à portabilidade. 2018. Monografia (Graduação) — UNISUL, Palhoça. Disponível em: https://repositorio.animaeducacao.com.br/items/a6acd4a9-6fc3-4bef-8843-1fac71b123f6. Acesso em: 14 abr. 2026.

BARRY, R. *Mastering the FreeRTOS Real Time Kernel: a hands-on tutorial guide*. Real Time Engineers Ltd., 2022.

FACENS. Plano de aprendizagem — Tópicos Especiais em Engenharia Mecatrônica I (CA220). Sorocaba, 2026. (Documento da disciplina.)

FBSELETRONICA. *Exemplos-FreeRTOS* (ESP32). GitHub. Disponível em: https://github.com/FBSeletronica/Exemplos-FreeRTOS. Acesso em: 14 abr. 2026.

MAKERHERO. Fila com FreeRTOS. *Blog MakerHero*. Disponível em: https://www.makerhero.com/blog/fila-com-freertos/. Acesso em: 14 abr. 2026.

MEDEIROS, M. L. de. Dissertação (mestrado) — UNIFEI, 2017. Repositório: https://repositorio.unifei.edu.br/jspui/bitstream/123456789/1071/1/dissertacao_medeiros_2017.pdf. Acesso em: 14 abr. 2026. *(Ajustar citação bibliográfica completa conforme a folha de rosto do PDF.)*

SPOHN, M. A.; CHABATURA NETO, F.; FASSINI, L. T. Uma avaliação do sistema operacional FreeRTOS na plataforma Arduino Uno. *Revista de Sistemas e Computação*, v. 9, n. 2, 2019. Disponível em: https://revistas.unifacs.br/index.php/rsc/article/view/6016. Acesso em: 14 abr. 2026.

TANENBAUM, A. S. *Sistemas operacionais modernos*. 4. ed. São Paulo: Pearson Education do Brasil, 2015.

---

## ANEXO A — Correspondência com o código-fonte

Arquivo: `sistema_qualidade_ar/sistema_qualidade_ar.ino`

- Constantes: `SETPOINT 35`, `HISTERESE_INF 34`, `HISTERESE_SUP 36`, `TEMP_EMERGENCIA 50`.  
- Prioridades (ordem crescente de número = maior prioridade neste firmware): Display (1), Sensor (2), Control (3), Emergency (4).  
- Tarefas criadas com `xTaskCreatePinnedToCore` no **Core 1**.  
- `loop()` não usa delays; após inicialização, libera o núcleo com `vTaskDelete(NULL)`.

---

*Para gerar o `.docx` já com a capa, tabela de identificação, sumário e estilos do modelo da UPx, execute no PowerShell: `gerar_docx_com_modelo.ps1`. Depois, no Word: clique com o botão direito no sumário → **Atualizar campo** → **Atualizar tabela inteira**, para alinhar números de página e entradas ao novo texto.*

*Documento-fonte em Markdown; formatação final conforme `Modelo do Projeto Escrito_s1.docx`.*
