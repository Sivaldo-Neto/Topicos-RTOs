# Estrutura laser — protótipo Minha Horta (40 cm)

Arquivo de corte a laser da caixa do TCC de irrigação automatizada, redimensionada para **altura total 40 cm**.

## Arquivos

| Arquivo | Uso |
|---|---|
| `output/estrutura_irrigacao_40cm_mdf3mm.dxf` | Cortar na laser (unidade: **mm**) |
| `output/preview_pecas.png` | Vista das peças no nesting |
| `scripts/gerar_dxf_estrutura.py` | Regenerar o DXF se mudar algum parâmetro |

## Medidas adotadas

| Parâmetro | Valor |
|---|---|
| Comprimento externo | 260 mm |
| Profundidade externa | 100 mm |
| Altura total externa | **400 mm** |
| Material | MDF **3 mm** |
| Vasos | 2 × furo Ø **90 mm** |
| Prateleira dos vasos (topo) | 85 mm a partir da base |
| Distância HC-SR04 → substrato | **≈ 312 mm** |
| Mangueira | furos Ø **10 mm** |
| Kerf compensado no CAD | 0.12 mm |
| Mesa | peças cabem em ~1050 × 860 mm (sua mesa 1300 × 1900 mm) |

## Peças no DXF

1. **FRENTE** — finger joints + slots + 2 furos de mangueira  
2. **TRASEIRA** — igual à frente + **nicho** 110×70 mm para acoplar o reservatório  
3. **LATERAL ESQ** — furos M3 para a prateleira do reservatório  
4. **LATERAL DIR** — furos M3 para o painel da eletrônica  
5. **BASE**  
6. **TAMPA** — 2× HC-SR04 (olhos Ø16,2 mm + furos M3) alinhados aos vasos  
7. **PRATELEIRA VASOS** — 2 furos Ø90 mm  
8. **DIVISÓRIA CENTRAL**  
9. **PAINEL ELETRONICA** — ventilação + furo de cabos (fixado na lateral direita)  
10. **PRATELEIRA RESERVATORIO** + **ABA** — apoio externo do galão/caixa d’água  

## Camadas

- `CORTE` → cortar  
- `TEXTO` / `INFO` → **não cortar** (só referência; pode apagar no LightBurn)

## Montagem sugerida

1. Encaixar **BASE** nos slots inferiores das 4 paredes + divisória.  
2. Encaixar **PRATELEIRA VASOS** na altura dos slots intermediários.  
3. Encaixar **TAMPA** no topo (sensores olhando para baixo).  
4. Cola + grampos nos finger joints (cola de madeira / PVA).  
5. Parafusar o **painel da eletrônica** na lateral direita (ESP32/protoboard).  
6. Parafusar a **prateleira do reservatório** na lateral esquerda; o nicho da traseira ajuda a “atracar” o recipiente.  
7. Passar mangueira de aquário pelos furos Ø10 e posicionar a bomba no reservatório (continua fora da caixa).

## Firmware

Atualizar a altura de referência do HC-SR04 de **12,8 cm** para **≈ 31,2 cm** (312 mm), medindo de novo com trena após montar:

```text
altura_planta = 31.2 - distancia_medida_cm
```

## Ajustes rápidos

Edite o topo de `scripts/gerar_dxf_estrutura.py` e rode:

```bash
python3 estrutura-laser-tcc/scripts/gerar_dxf_estrutura.py
```

Parâmetros úteis: `SHELF_TOP`, `POT_HOLE_D`, `HOSE_D`, `KERF`, `H`.

### Observações

- Com profundidade interna 94 mm e furo Ø90, sobram ~2 mm de borda na frente/trás da prateleira (igual à lógica do protótipo 10 cm). Se o vaso cair ou a borda ficar frágil, regenere com `POT_HOLE_D = 86` ou `88`.  
- Calibre o **kerf** da sua máquina com um quadrado de teste; se o encaixe ficar folgado/apertado, ajuste `KERF` (0.08–0.20 mm é o intervalo usual em MDF 3 mm).  
- O reservatório de 5 L permanece externo; o nicho + prateleira só organizam o acoplamento e a mangueira.
