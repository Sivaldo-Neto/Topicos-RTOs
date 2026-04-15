# Guia de Teste do Projeto RTOS

Este guia organiza tudo o que você precisa para testar o projeto `SISTEMA DE MONITORAMENTO E CONTROLE DE QUALIDADE DO AR COM RTOS`, tanto na parte de hardware quanto na parte de software e documentação.

## 1. Objetivo do teste

O objetivo dos testes é comprovar que o sistema:

- lê temperatura e umidade corretamente
- executa múltiplas tasks com FreeRTOS
- controla aquecedor e cooler conforme a histerese definida
- exibe as informações no OLED
- entra em modo de emergência quando a temperatura atinge o limite crítico
- se mantém estável dentro da faixa desejada

## 2. Arquivos que você precisa ter

### 2.1 Arquivos principais do projeto

- `sistema_qualidade_ar\sistema_qualidade_ar.ino`
- `Relatorio_UPx_Sistema_Qualidade_do_Ar_COM_RTOS.md`
- `Checklist_Montagem_Word_UPx.md`
- `Guia_Teste_Projeto_RTOS.md`

### 2.2 Arquivos úteis para a entrega

- `Modelo do Projeto Escrito_s1.docx`
- Fotos da montagem
- Prints do monitor serial
- Prints do display
- Tabela de orçamento
- Anotações de resultados

### 2.3 Arquivos que vale guardar durante o teste

- planilha com medições
- fotos em cada etapa
- vídeo curto mostrando funcionamento
- print da serial em situação normal
- print da serial em situação de emergência

## 3. Materiais de hardware

### 3.1 Componentes eletrônicos principais

- 1x ESP32 DevKit V1
- 1x sensor DHT22
- 1x display OLED 0,96" I2C SSD1306
- 1x módulo relé 5 V com 2 canais
- 1x aquecedor ou resistor cerâmico 10 W / 12 V
- 1x cooler 12 V
- 1x fonte 12 V / 3 A
- jumpers
- protoboard

### 3.2 Estrutura mecânica

- caixa de isopor ou câmara térmica improvisada
- suporte para fixar o sensor
- espaço interno para o aquecedor e o cooler
- fita, abraçadeiras ou cola quente para organizar a montagem

### 3.3 Instrumentos de apoio

- termômetro de referência
- se possível, higrômetro de referência
- cronômetro
- multímetro
- régua ou suporte para posicionamento interno dos componentes

## 4. Materiais de software

- Arduino IDE ou PlatformIO
- driver/placa ESP32 configurada no ambiente
- bibliotecas:
  - `DHT`
  - `Adafruit GFX`
  - `Adafruit SSD1306`
  - `Wire`
- cabo USB para programação e monitor serial

## 5. Ligação básica esperada

Pelos arquivos do projeto, a pinagem usada é:

- DHT22 no `GPIO 4`
- relé do aquecedor no `GPIO 26`
- relé do cooler no `GPIO 27`
- I2C SDA no `GPIO 21`
- I2C SCL no `GPIO 22`

## 6. O que verificar antes de ligar

- alimentação correta do ESP32
- alimentação correta do módulo relé
- tensão correta do cooler
- tensão correta do aquecedor
- GND comum entre os módulos
- polaridade correta do display OLED
- DHT22 ligado corretamente
- nenhum fio encostando em outro
- relé compatível com a carga usada

## 7. Cuidados de segurança

- não deixar o aquecedor encostando no isopor
- manter o resistor/aquecedor bem fixado
- não ligar o sistema sem supervisão
- testar primeiro por poucos segundos
- monitorar aquecimento dos fios e do relé
- ter cuidado com fonte 12 V e corrente da carga

## 8. O que testar no software

### 8.1 Inicialização

Quando o sistema ligar, verificar:

- se a Serial inicia em `115200`
- se o DHT22 é inicializado
- se o OLED mostra mensagem inicial
- se fila e mutex são criados
- se as tasks são criadas sem erro

### 8.2 Leitura do sensor

Verificar se:

- temperatura aparece na Serial
- umidade aparece na Serial
- os valores fazem sentido
- não há muitas falhas seguidas de leitura

### 8.3 Controle normal

Verificar a lógica:

- abaixo de `34 C`: aquecedor ligado
- acima de `36 C`: cooler ligado
- entre `34 C` e `36 C`: ambos desligados

### 8.4 Display

Verificar se o OLED mostra:

- temperatura
- umidade
- estado do aquecedor
- estado do cooler
- mensagem de emergência, quando necessário

### 8.5 Emergência

Verificar se, ao ultrapassar `50 C`:

- aquecedor desliga
- cooler liga
- mensagem `EMERGENCIA` aparece
- a Serial registra o evento

## 9. Roteiro completo de teste

## 9.1 Teste 1: inicialização do sistema

Objetivo:

- confirmar que o firmware sobe sem erro

Passos:

1. Conectar o ESP32 ao PC
2. Abrir o monitor serial
3. Ligar o sistema
4. Observar mensagens de inicialização

Registrar:

- hora do teste
- print da Serial
- se o OLED acendeu

Critério de sucesso:

- sistema inicializa sem travar
- tasks são criadas
- não aparece falha crítica

## 9.2 Teste 2: leitura do DHT22

Objetivo:

- verificar leitura correta de temperatura e umidade

Passos:

1. Deixar o sistema em repouso
2. Observar leituras por alguns minutos
3. Comparar com termômetro de referência

Registrar:

- temperatura do DHT22
- temperatura do termômetro de referência
- umidade
- erro aproximado

Critério de sucesso:

- leitura coerente e estável

## 9.3 Teste 3: atuação do aquecedor

Objetivo:

- verificar se o aquecedor liga quando a temperatura está baixa

Passos:

1. Iniciar com temperatura ambiente abaixo da faixa
2. Ligar o sistema
3. Observar o acionamento do relé do aquecedor
4. Acompanhar a subida da temperatura

Registrar:

- temperatura inicial
- tempo de acionamento
- tempo até chegar perto do setpoint

Critério de sucesso:

- aquecedor liga abaixo da faixa definida

## 9.4 Teste 4: atuação do cooler

Objetivo:

- verificar se o cooler liga quando a temperatura sobe acima da faixa

Passos:

1. Aquecer a câmara
2. Observar a temperatura na Serial
3. Confirmar se o cooler entra em ação acima de `36 C`

Registrar:

- temperatura de acionamento
- comportamento do relé
- tempo de resfriamento

Critério de sucesso:

- cooler liga acima da faixa definida

## 9.5 Teste 5: zona morta / histerese

Objetivo:

- verificar se o sistema não fica chaveando toda hora

Passos:

1. Levar o sistema para a faixa entre `34 C` e `36 C`
2. Observar se os dois atuadores permanecem desligados

Registrar:

- faixa observada
- estabilidade da leitura

Critério de sucesso:

- ambos desligados dentro da zona morta

## 9.6 Teste 6: emergência térmica

Objetivo:

- verificar a task de emergência

Passos:

1. Aquecer o ambiente controlado até ultrapassar `50 C`
2. Observar o comportamento do sistema

Registrar:

- temperatura do disparo
- mensagem na Serial
- mensagem no display
- status do aquecedor
- status do cooler

Critério de sucesso:

- aquecedor desliga imediatamente
- cooler liga
- mensagem de emergência aparece

## 9.7 Teste 7: distúrbio térmico

Objetivo:

- verificar recuperação do sistema

Passos:

1. Deixar o sistema estabilizado
2. Abrir a tampa da câmara por 10 segundos
3. Fechar novamente
4. Medir o tempo de recuperação

Registrar:

- temperatura antes
- temperatura depois da abertura
- tempo de retorno

Critério de sucesso:

- sistema volta à faixa desejada em tempo razoável

## 10. O que anotar em cada teste

Para cada teste, anote:

- data
- horário
- quem realizou
- versão do código usado
- condição inicial
- resultado observado
- fotos ou prints
- problema encontrado
- observação final

## 11. Modelo simples de tabela de resultados

Você pode usar uma tabela assim no Word:

| Teste | Objetivo | Resultado esperado | Resultado obtido | Aprovado? |
|------|----------|--------------------|------------------|-----------|
| Inicialização | Verificar boot | Sistema sobe sem erro | preencher | Sim/Não |
| Sensor | Validar leitura | Leitura coerente | preencher | Sim/Não |
| Aquecedor | Atuar abaixo de 34 C | Liga corretamente | preencher | Sim/Não |
| Cooler | Atuar acima de 36 C | Liga corretamente | preencher | Sim/Não |
| Emergência | Proteger acima de 50 C | Desliga aquecedor e liga cooler | preencher | Sim/Não |

## 12. Evidências que você deveria produzir

- 1 foto da montagem geral
- 1 foto da câmara de teste
- 1 print da inicialização serial
- 1 print da leitura normal
- 1 print do aquecedor ligado
- 1 print do cooler ligado
- 1 print do modo emergência
- 1 tabela com resultados finais

## 13. Critérios finais de aceitação

Considere o projeto validado se:

- o ESP32 inicializa corretamente
- o sensor mede de forma coerente
- o OLED exibe os dados
- o aquecedor e o cooler respondem corretamente à histerese
- o sistema entra em emergência em temperatura crítica
- o comportamento geral é estável

## 14. O que levar no dia de teste/apresentação

- notebook com Arduino IDE ou PlatformIO
- cabo USB do ESP32
- fonte 12 V
- ESP32 montado
- sensor DHT22
- display OLED
- relé
- cooler
- aquecedor
- câmara/isopor
- jumpers extras
- protoboard extra
- multímetro
- cópia do relatório
- backup do código

## 15. Ordem prática recomendada no dia

1. Montar hardware
2. Conferir alimentação
3. Carregar código no ESP32
4. Abrir Serial
5. Testar leitura do sensor
6. Testar display
7. Testar aquecedor
8. Testar cooler
9. Testar emergência
10. Registrar tudo com foto/print

## 16. Próximos arquivos úteis que você pode criar depois

- `Tabela_Resultados_Teste.xlsx`
- `Fotos_Teste/`
- `Capturas_Serial/`
- `Versao_Final_Relatorio.docx`
- `Versao_Final_Relatorio.pdf`
