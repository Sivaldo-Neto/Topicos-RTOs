# Estrutura laser — protótipo Minha Horta (40 cm)

Arquivo de corte a laser da caixa do TCC de irrigação automatizada, redimensionada para **altura total 40 cm**, com **frente aberta** (sem painel frontal).

## Arquivos

| Arquivo | Uso |
|---|---|
| `output/estrutura_irrigacao_40cm_mdf3mm.dxf` | Cortar na laser (unidade: **mm**) |
| `output/preview_pecas.png` | Vista das peças no nesting |
| `output/montagem_estrutura_40cm.stl` | Modelo 3D da montagem (STL) |
| `output/montagem_estrutura_40cm.step` | Modelo 3D (STEP / CAD) |
| `output/montagem_estrutura_40cm.glb` | Modelo 3D colorido (visualização) |
| `output/viewer_montagem.html` | Viewer interativo (abrir junto com o `.glb`) |
| `output/renders/` | Renders PNG da montagem |
| `scripts/gerar_dxf_estrutura.py` | Regenerar o DXF |
| `scripts/gerar_3d_montagem.py` | Regenerar o 3D / renders |

## Medidas adotadas

| Parâmetro | Valor |
|---|---|
| Comprimento externo | 260 mm |
| Profundidade externa | 100 mm |
| Altura total externa | **400 mm** |
| Material | MDF **3 mm** |
| Vasos | 2 × furo Ø **86 mm** (prende pela borda do vaso 9 cm) |
| Prateleira dos vasos (topo) | 85 mm a partir da base |
| Distância HC-SR04 → substrato | **≈ 312 mm** |
| Mangueira | furos Ø **10 mm** |
| Kerf compensado no CAD | 0.10 mm |
| Frente | **aberta** (sem peça frontal) |

## Peças no DXF

1. **LATERAL ESQ** — entalhes + furos do reservatório  
2. **LATERAL DIR** — entalhes + furos da eletrônica  
3. **TRASEIRA** — tabs laterais + nicho do reservatório  
4. **BASE** / **PRATELEIRA VASOS** (Ø86) / **TAMPA** (2× HC-SR04)  
5. **DIVISÓRIA CENTRAL**  
6. **PAINEL ELETRÔNICA**  
7. **PRATELEIRA RESERVATÓRIO**

## Camadas

- `CORTE` → cortar  
- `TEXTO` / `INFO` → **não cortar** (só referência; pode apagar no LightBurn)

## Montagem sugerida

1. Encaixar **BASE** nos entalhes inferiores das laterais + traseira.  
2. Encaixar **DIVISÓRIA** nos slots da traseira / fendas dos painéis.  
3. Encaixar **PRATELEIRA VASOS** nos slots intermediários.  
4. Encaixar **TAMPA** nos entalhes superiores (HC-SR04 para baixo).  
5. Cola PVA nos tabs + grampos até secar.  
6. Parafusar o **painel da eletrônica** na lateral direita.  
7. Parafusar a **prateleira do reservatório** na lateral esquerda.  
8. Passar mangueira Ø10 e deixar o reservatório fora (nicho na traseira).

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

- Furo Ø86 com profundidade interna 97 mm → ~5,5 mm de borda em cada lado. Se o vaso não assentar, ajuste `POT_HOLE_D` (84–88).  
- Calibre o **kerf** com um quadrado de teste; intervalo usual em MDF 3 mm: 0.08–0.20 mm.  
- Reservatório de 5 L continua externo; nicho + prateleira só organizam o acoplamento.
