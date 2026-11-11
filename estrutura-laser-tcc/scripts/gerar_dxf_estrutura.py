#!/usr/bin/env python3
"""
Gera DXF 1:1 (mm) da estrutura do protótipo Minha Horta / TCC irrigação.

Caixa externa: 260 x 100 x 400 mm | MDF 3 mm | 2 vasos | 2x HC-SR04
Saída: output/estrutura_irrigacao_40cm_mdf3mm.dxf
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment


# ---------------------------------------------------------------------------
# Parâmetros do projeto (edite aqui se precisar ajustar)
# ---------------------------------------------------------------------------
L = 260.0  # comprimento externo (eixo dos 2 vasos), mm
D = 100.0  # profundidade externa, mm
H = 400.0  # altura total externa, mm
T = 3.0  # espessura MDF, mm

SHELF_TOP = 85.0  # face superior da prateleira dos vasos (a partir da base)
POT_HOLE_D = 90.0  # diâmetro do furo do vaso (manter como no protótipo)
HOSE_D = 10.0  # mangueira de aquário (folha ~Ø10 mm)

# HC-SR04: dois transdutores Ø16 mm, centro a centro ~25.4 mm
HCSR_EYE_D = 16.2
HCSR_EYE_SPACING = 25.4
HCSR_MOUNT_DX = 42.0 / 2
HCSR_MOUNT_DY = 17.0 / 2
HCSR_MOUNT_HOLE = 3.2  # M3

FINGER_W = 10.0  # largura alvo do dedo (ajustada para caber inteiros)
TAB_W = 12.0  # largura dos tabs da prateleira/tampa/base
KERF = 0.12  # compensação de kerf (mm); 0 desliga

# Layout na mesa (mm)
SHEET_MARGIN = 10.0
GAP = 8.0

OUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUT_DXF = OUT_DIR / "estrutura_irrigacao_40cm_mdf3mm.dxf"


@dataclass
class Part:
    name: str
    width: float
    height: float
    draw: callable


def kerf_out(delta: float = KERF) -> float:
    return delta


def round_to_odd_fingers(length: float, target: float = FINGER_W) -> tuple[int, float]:
    """Número ímpar de dedos (>=3) para cantos macho/fêmea encaixarem."""
    n = max(3, int(round(length / target)))
    if n % 2 == 0:
        n += 1
    return n, length / n


def finger_polyline(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    depth: float,
    start_male: bool,
    outward: bool,
) -> list[tuple[float, float]]:
    """
    Gera polyline de junta em dedo ao longo do segmento (x0,y0)->(x1,y1).
    depth: penetração do dedo (= T).
    start_male: se True, o primeiro intervalo é saliente (material).
    outward: direção do saliente em relação ao sentido do segmento (normal à esquerda se True).
    """
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return [(x0, y0)]
    ux, uy = dx / length, dy / length
    # normal esquerda
    nx, ny = (-uy, ux) if outward else (uy, -ux)
    n, fw = round_to_odd_fingers(length)
    pts: list[tuple[float, float]] = []
    male = start_male
    for i in range(n):
        a = i * fw
        b = (i + 1) * fw
        ax, ay = x0 + ux * a, y0 + uy * a
        bx, by = x0 + ux * b, y0 + uy * b
        if male:
            # saliente: avança na normal
            pts += [
                (ax + nx * depth, ay + ny * depth),
                (bx + nx * depth, by + ny * depth),
            ]
        else:
            pts += [(ax, ay), (bx, by)]
        male = not male
    return pts


def rect_with_side_fingers(
    w: float,
    h: float,
    left_male: bool,
    right_male: bool,
    top_flat: bool = True,
    bottom_flat: bool = True,
) -> list[tuple[float, float]]:
    """
    Retângulo w x h com finger joints nas bordas verticais (x=0 e x=w).
    Origem no canto inferior esquerdo do retângulo 'corpo' (sem contar salientes).
    Dedos saem para FORA (left x negativo, right x>w).
    """
    # Percorre CCW: bottom -> right -> top -> left
    pts: list[tuple[float, float]] = []

    # Bottom edge L->R
    if bottom_flat:
        pts += [(0, 0), (w, 0)]
    else:
        pts += finger_polyline(0, 0, w, 0, T, start_male=True, outward=False)

    # Right edge B->T (outward = +X)
    pts_r = finger_polyline(w, 0, w, h, T, start_male=right_male, outward=True)
    pts += pts_r

    # Top edge R->L
    if top_flat:
        pts += [(w, h), (0, h)]
    else:
        pts += finger_polyline(w, h, 0, h, T, start_male=True, outward=False)

    # Left edge T->B (outward = -X). Percorrendo de cima para baixo.
    # Para manter CCW, normal "outward" com sentido T->B: outward True dá normal esquerda = -X. OK.
    pts_l = finger_polyline(0, h, 0, 0, T, start_male=left_male, outward=True)
    pts += pts_l

    return pts


def add_lwpoly(msp, points: list[tuple[float, float]], closed: bool = True, layer: str = "CORTE"):
    if len(points) < 2:
        return
    # remove consecutivos duplicados
    clean = [points[0]]
    for p in points[1:]:
        if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-6:
            clean.append(p)
    if closed and clean and math.hypot(clean[0][0] - clean[-1][0], clean[0][1] - clean[-1][1]) < 1e-6:
        clean = clean[:-1]
    msp.add_lwpolyline(clean, close=closed, dxfattribs={"layer": layer})


def add_circle(msp, cx: float, cy: float, diameter: float, layer: str = "CORTE"):
    r = diameter / 2
    if KERF:
        r -= KERF / 2  # furo um pouco menor; laser abre
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})


def add_slot_rect(msp, x: float, y: float, w: float, h: float, layer: str = "CORTE"):
    """Retângulo de encaixe (furo). Kerf: abre um pouco o furo (menor material removido no CAD = laser acerta)."""
    if KERF:
        x += KERF / 2
        y += KERF / 2
        w -= KERF
        h -= KERF
    add_lwpoly(msp, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True, layer)


def add_hcsr04(msp, cx: float, cy: float, along_x: bool = True):
    """Dois olhos + 4 furos M3 centrados em (cx, cy)."""
    if along_x:
        add_circle(msp, cx - HCSR_EYE_SPACING / 2, cy, HCSR_EYE_D)
        add_circle(msp, cx + HCSR_EYE_SPACING / 2, cy, HCSR_EYE_D)
        for sx in (-1, 1):
            for sy in (-1, 1):
                add_circle(msp, cx + sx * HCSR_MOUNT_DX, cy + sy * HCSR_MOUNT_DY, HCSR_MOUNT_HOLE)
    else:
        add_circle(msp, cx, cy - HCSR_EYE_SPACING / 2, HCSR_EYE_D)
        add_circle(msp, cx, cy + HCSR_EYE_SPACING / 2, HCSR_EYE_D)
        for sx in (-1, 1):
            for sy in (-1, 1):
                add_circle(msp, cx + sx * HCSR_MOUNT_DY, cy + sy * HCSR_MOUNT_DX, HCSR_MOUNT_HOLE)


def add_label(msp, x: float, y: float, text: str):
    msp.add_text(
        text,
        height=3.5,
        dxfattribs={"layer": "TEXTO", "insert": (x, y)},
    ).set_placement((x, y), align=TextEntityAlignment.LEFT)


def wall_slots_for_horizontals(msp, is_front_back: bool, width: float):
    """Furos/slots para base, prateleira, tampa e divisória."""
    # Slots horizontais (tabs das prateleiras)
    # Base: face superior em y=T → painel ocupa [0, T] se encostado na base.
    # Usamos base com topo em y=T (painel 0..T).
    def hslot(y_panel_bottom: float):
        # slot atravessa espessura T na parede, centrado na altura do painel
        add_slot_rect(msp, (width - TAB_W) / 2 - 40, y_panel_bottom, TAB_W, T)
        add_slot_rect(msp, (width + 40 - TAB_W) / 2 + 40, y_panel_bottom, TAB_W, T)

    # Para front/back (largura L=260): dois slots por nível + slot vertical da divisória
    if is_front_back:
        # base
        add_slot_rect(msp, 40, 0, TAB_W, T)
        add_slot_rect(msp, width - 40 - TAB_W, 0, TAB_W, T)
        # prateleira
        y_shelf = SHELF_TOP - T
        add_slot_rect(msp, 40, y_shelf, TAB_W, T)
        add_slot_rect(msp, width - 40 - TAB_W, y_shelf, TAB_W, T)
        # tampa (topo do painel flush com H)
        add_slot_rect(msp, 40, H - T, TAB_W, T)
        add_slot_rect(msp, width - 40 - TAB_W, H - T, TAB_W, T)
        # divisória central (slot vertical contínuo com interrupções nas prateleiras)
        x_div = (width - T) / 2
        # três segmentos: abaixo da prateleira, entre prateleira e tampa, evitando sobrepor slots
        add_slot_rect(msp, x_div, T + 1, T, y_shelf - (T + 1) - 1)
        add_slot_rect(msp, x_div, y_shelf + T + 1, T, (H - T) - (y_shelf + T + 1) - 1)
    else:
        # laterais (profundidade interna = D-2T)
        add_slot_rect(msp, (width - TAB_W) / 2, 0, TAB_W, T)
        add_slot_rect(msp, (width - TAB_W) / 2, SHELF_TOP - T, TAB_W, T)
        add_slot_rect(msp, (width - TAB_W) / 2, H - T, TAB_W, T)


def draw_front(msp, ox: float, oy: float):
    w, h = L, H
    # laterais: front é fêmea no topo dos dedos das laterais → start male False nas verticais
    # Convenção: LEFT side male no front edge → FRONT left edge fêmea (start_male False se contagem de baixo)
    pts = rect_with_side_fingers(w, h, left_male=False, right_male=False)
    pts = [(ox + x, oy + y) for x, y in pts]
    add_lwpoly(msp, pts)
    # slots em coordenadas locais
    # temporariamente desenhar slots com offset
    # reimplementar slots com offset:
    def slot(x, y, sw, sh):
        add_slot_rect(msp, ox + x, oy + y, sw, sh)

    y_shelf = SHELF_TOP - T
    slot(40, 0, TAB_W, T)
    slot(w - 40 - TAB_W, 0, TAB_W, T)
    slot(40, y_shelf, TAB_W, T)
    slot(w - 40 - TAB_W, y_shelf, TAB_W, T)
    slot(40, H - T, TAB_W, T)
    slot(w - 40 - TAB_W, H - T, TAB_W, T)
    x_div = (w - T) / 2
    slot(x_div, T + 1, T, y_shelf - T - 2)
    slot(x_div, y_shelf + T + 1, T, H - T - (y_shelf + T + 1) - 1)
    # mangueiras (um furo por compartimento, perto da base)
    add_circle(msp, ox + L * 0.25, oy + 25, HOSE_D)
    add_circle(msp, ox + L * 0.75, oy + 25, HOSE_D)
    # janela inferior leve (ventilação / acesso) — opcional semicorte visual
    add_label(msp, ox + 4, oy + H - 8, "FRENTE")


def draw_back(msp, ox: float, oy: float):
    w, h = L, H
    pts = rect_with_side_fingers(w, h, left_male=False, right_male=False)
    pts = [(ox + x, oy + y) for x, y in pts]
    add_lwpoly(msp, pts)

    def slot(x, y, sw, sh):
        add_slot_rect(msp, ox + x, oy + y, sw, sh)

    y_shelf = SHELF_TOP - T
    slot(40, 0, TAB_W, T)
    slot(w - 40 - TAB_W, 0, TAB_W, T)
    slot(40, y_shelf, TAB_W, T)
    slot(w - 40 - TAB_W, y_shelf, TAB_W, T)
    slot(40, H - T, TAB_W, T)
    slot(w - 40 - TAB_W, H - T, TAB_W, T)
    x_div = (w - T) / 2
    slot(x_div, T + 1, T, y_shelf - T - 2)
    slot(x_div, y_shelf + T + 1, T, H - T - (y_shelf + T + 1) - 1)

    # mangueiras
    add_circle(msp, ox + L * 0.25, oy + 25, HOSE_D)
    add_circle(msp, ox + L * 0.75, oy + 25, HOSE_D)

    # Nicho do reservatório (recorte inferior central-esquerdo para acoplar galão/caixa)
    # Recorte em U: largura 110 mm, altura 70 mm, a partir da base (acima da base panel)
    niche_w, niche_h = 110.0, 70.0
    nx0 = ox + 20
    ny0 = oy + T + 2
    add_lwpoly(
        msp,
        [
            (nx0, ny0),
            (nx0 + niche_w, ny0),
            (nx0 + niche_w, ny0 + niche_h),
            (nx0, ny0 + niche_h),
        ],
        True,
    )
    add_label(msp, ox + 4, oy + H - 8, "TRASEIRA (nicho reservatorio)")


def draw_side(msp, ox: float, oy: float, name: str, electronics: bool):
    w, h = D - 2 * T, H  # 94 x 400
    # Laterais: macho nas bordas front/back para entrar na frente/traseira
    # No desenho 2D, x=0 é borda "frente", x=w é borda "traseira"
    pts = rect_with_side_fingers(w, h, left_male=True, right_male=True)
    pts = [(ox + x, oy + y) for x, y in pts]
    add_lwpoly(msp, pts)

    def slot(x, y, sw, sh):
        add_slot_rect(msp, ox + x, oy + y, sw, sh)

    slot((w - TAB_W) / 2, 0, TAB_W, T)
    slot((w - TAB_W) / 2, SHELF_TOP - T, TAB_W, T)
    slot((w - TAB_W) / 2, H - T, TAB_W, T)

    # passagem mangueira
    add_circle(msp, ox + w / 2, oy + 25, HOSE_D)

    if electronics:
        # padrão de furação para painel da protoboard (M3)
        cx, cy = ox + w / 2, oy + 220
        for sx in (-28, 28):
            for sy in (-40, 40):
                add_circle(msp, cx + sx, cy + sy, 3.2)
        add_label(msp, ox + 2, oy + H - 8, f"{name} (furos eletronica)")
    else:
        # furos para suporte/nicho do reservatório
        cx, cy = ox + w / 2, oy + 50
        for sx in (-25, 25):
            for sy in (0, 40):
                add_circle(msp, cx + sx, cy + sy, 3.2)
        add_label(msp, ox + 2, oy + H - 8, f"{name} (furos suporte reservatorio)")


def panel_with_tabs(w: float, d: float, tabs_long: bool = True, tabs_short: bool = True) -> list[tuple[float, float]]:
    """Painel horizontal w x d com tabs centrados em cada lado."""
    # Começa sem tabs e adiciona salientes de tamanho TAB_W x T
    # Percorre CCW
    pts: list[tuple[float, float]] = []
    # bottom
    if tabs_short:
        mid = w / 2
        pts += [(0, 0), (mid - TAB_W / 2, 0), (mid - TAB_W / 2, -T), (mid + TAB_W / 2, -T), (mid + TAB_W / 2, 0), (w, 0)]
    else:
        pts += [(0, 0), (w, 0)]
    # right
    if tabs_long:
        mid = d / 2
        pts += [(w, mid - TAB_W / 2), (w + T, mid - TAB_W / 2), (w + T, mid + TAB_W / 2), (w, mid + TAB_W / 2), (w, d)]
    else:
        pts += [(w, d)]
    # top
    if tabs_short:
        mid = w / 2
        pts += [(mid + TAB_W / 2, d), (mid + TAB_W / 2, d + T), (mid - TAB_W / 2, d + T), (mid - TAB_W / 2, d), (0, d)]
    else:
        pts += [(0, d)]
    # left
    if tabs_long:
        mid = d / 2
        pts += [(0, mid + TAB_W / 2), (-T, mid + TAB_W / 2), (-T, mid - TAB_W / 2), (0, mid - TAB_W / 2), (0, 0)]
    else:
        pts += [(0, 0)]
    return pts


def draw_bottom(msp, ox: float, oy: float):
    w, d = L - 2 * T, D - 2 * T  # 254 x 94
    # tabs: 2 no comprimento (front/back) e 1 em cada lateral — combinar com slots
    # Front/back walls têm 2 slots; laterais 1 slot. Então:
    pts = []
    # bottom edge (frente): dois tabs
    pts += [(0, 0)]
    for tx in (40 - T, (w) - 40 - T):  # alinhar com slots das paredes em coords internas
        # slots nas paredes front em x=40 e x=w_wall-40-TAB; parede interna começa em T
        pass
    # Melhor: tabs nas posições que batem com slots das paredes.
    # Frente (y negativo): tabs em x local = 40-T e L-40-TAB_W-T relative to outer... 
    # Parede front slot em x_outer=40 → x_inner no painel = 40 - T
    x1 = 40 - T
    x2 = L - 40 - TAB_W - T
    y1 = (d - TAB_W) / 2  # para laterais

    pts = [
        (0, 0),
        (x1, 0),
        (x1, -T),
        (x1 + TAB_W, -T),
        (x1 + TAB_W, 0),
        (x2, 0),
        (x2, -T),
        (x2 + TAB_W, -T),
        (x2 + TAB_W, 0),
        (w, 0),
        # right side tab
        (w, y1),
        (w + T, y1),
        (w + T, y1 + TAB_W),
        (w, y1 + TAB_W),
        (w, d),
        # top (back) two tabs
        (x2 + TAB_W, d),
        (x2 + TAB_W, d + T),
        (x2, d + T),
        (x2, d),
        (x1 + TAB_W, d),
        (x1 + TAB_W, d + T),
        (x1, d + T),
        (x1, d),
        (0, d),
        # left side tab
        (0, y1 + TAB_W),
        (-T, y1 + TAB_W),
        (-T, y1),
        (0, y1),
        (0, 0),
    ]
    add_lwpoly(msp, [(ox + x, oy + y) for x, y in pts])
    # fenda da divisória
    add_slot_rect(msp, ox + (w - T) / 2, oy + 8, T, d - 16)
    add_label(msp, ox + 4, oy + d / 2, "BASE")


def draw_top(msp, ox: float, oy: float):
    w, d = L - 2 * T, D - 2 * T
    x1 = 40 - T
    x2 = L - 40 - TAB_W - T
    y1 = (d - TAB_W) / 2
    pts = [
        (0, 0),
        (x1, 0),
        (x1, -T),
        (x1 + TAB_W, -T),
        (x1 + TAB_W, 0),
        (x2, 0),
        (x2, -T),
        (x2 + TAB_W, -T),
        (x2 + TAB_W, 0),
        (w, 0),
        (w, y1),
        (w + T, y1),
        (w + T, y1 + TAB_W),
        (w, y1 + TAB_W),
        (w, d),
        (x2 + TAB_W, d),
        (x2 + TAB_W, d + T),
        (x2, d + T),
        (x2, d),
        (x1 + TAB_W, d),
        (x1 + TAB_W, d + T),
        (x1, d + T),
        (x1, d),
        (0, d),
        (0, y1 + TAB_W),
        (-T, y1 + TAB_W),
        (-T, y1),
        (0, y1),
        (0, 0),
    ]
    add_lwpoly(msp, [(ox + x, oy + y) for x, y in pts])
    add_slot_rect(msp, ox + (w - T) / 2, oy + 8, T, d - 16)

    # centros dos vasos / sensores (meio de cada compartimento)
    # compartimentos internos: 0..w/2-T/2 e w/2+T/2..w
    c1 = (w / 2 - T / 2) / 2
    c2 = w / 2 + T / 2 + (w / 2 - T / 2) / 2
    cy = d / 2
    add_hcsr04(msp, ox + c1, oy + cy, along_x=True)
    add_hcsr04(msp, ox + c2, oy + cy, along_x=True)
    add_label(msp, ox + 4, oy + d - 6, "TAMPA + 2x HC-SR04")


def draw_shelf(msp, ox: float, oy: float):
    w, d = L - 2 * T, D - 2 * T
    x1 = 40 - T
    x2 = L - 40 - TAB_W - T
    y1 = (d - TAB_W) / 2
    pts = [
        (0, 0),
        (x1, 0),
        (x1, -T),
        (x1 + TAB_W, -T),
        (x1 + TAB_W, 0),
        (x2, 0),
        (x2, -T),
        (x2 + TAB_W, -T),
        (x2 + TAB_W, 0),
        (w, 0),
        (w, y1),
        (w + T, y1),
        (w + T, y1 + TAB_W),
        (w, y1 + TAB_W),
        (w, d),
        (x2 + TAB_W, d),
        (x2 + TAB_W, d + T),
        (x2, d + T),
        (x2, d),
        (x1 + TAB_W, d),
        (x1 + TAB_W, d + T),
        (x1, d + T),
        (x1, d),
        (0, d),
        (0, y1 + TAB_W),
        (-T, y1 + TAB_W),
        (-T, y1),
        (0, y1),
        (0, 0),
    ]
    add_lwpoly(msp, [(ox + x, oy + y) for x, y in pts])
    # fenda divisória
    add_slot_rect(msp, ox + (w - T) / 2, oy + 8, T, d - 16)
    # furos dos vasos
    c1 = (w / 2 - T / 2) / 2
    c2 = w / 2 + T / 2 + (w / 2 - T / 2) / 2
    cy = d / 2
    add_circle(msp, ox + c1, oy + cy, POT_HOLE_D)
    add_circle(msp, ox + c2, oy + cy, POT_HOLE_D)
    add_label(msp, ox + 4, oy + 4, "PRATELEIRA VASOS Ø90")


def draw_divider(msp, ox: float, oy: float):
    # altura útil entre base e tampa: H - 2T, profundidade interna D-2T
    # com tabs para entrar nos slots front/back
    h = H - 2 * T
    d = D - 2 * T
    # corpo d x h; tabs na frente/tras (eixo x do desenho = profundidade)
    # desenhar com largura = d, altura = h
    # tabs em y baixos/altos? Na montagem a divisória é vertical: altura H-2T, profundidade D-2T
    # Tabs saem nas bordas front e back (profundidade ends) para slots das paredes front/back.
    tab_h = 20.0
    # dois tabs por lado (evitar prateleira)
    # posições y a partir da base do divisor (que começa em y=T no mundo)
    # slots front: de T+1 até shelf-1 e de shelf+T+1 até H-T-1
    # Em coords do divisor (0 = topo da base):
    y_shelf_local = SHELF_TOP - T - T  # bottom of shelf relative to top of base panel = SHELF_TOP - 2T? 
    # Base panel occupies 0..T in wall coords; divider sits on top of base → divider local 0 = wall y T
    # Shelf bottom at wall SHELF_TOP-T → local = SHELF_TOP - T - T = SHELF_TOP - 2T
    shelf_bottom_local = SHELF_TOP - 2 * T
    shelf_top_local = SHELF_TOP - T
    # tabs lower segment
    mid1 = shelf_bottom_local / 2
    # tabs upper segment
    mid2 = shelf_top_local + (h - shelf_top_local) / 2

    def side_tabs(x_body: float, sign: float):
        # returns points along one vertical side bottom->top or top->bottom
        pass

    pts = []
    # bottom edge
    pts += [(0, 0), (d, 0)]
    # right side (back) bottom->top with tabs
    def append_side(x, y0, y1, outward_x):
        # split around shelf gap (no tab through shelf slot region)
        regions = [(y0, shelf_bottom_local - 1), (shelf_top_local + 1, y1)]
        first = True
        for a, b in regions:
            if b - a < tab_h + 4:
                continue
            mid = (a + b) / 2
            if first:
                pts.append((x, a))
                first = False
            else:
                pts.append((x, a))
            pts += [
                (x, mid - tab_h / 2),
                (x + outward_x * T, mid - tab_h / 2),
                (x + outward_x * T, mid + tab_h / 2),
                (x, mid + tab_h / 2),
                (x, b),
            ]

    # right edge
    pts = [(0, 0), (d, 0)]
    # right
    x = d
    for a, b in [(0, shelf_bottom_local - 1), (shelf_top_local + 1, h)]:
        if b <= a:
            continue
        mid = (a + b) / 2
        pts += [
            (x, a),
            (x, mid - tab_h / 2),
            (x + T, mid - tab_h / 2),
            (x + T, mid + tab_h / 2),
            (x, mid + tab_h / 2),
            (x, b),
        ]
    pts.append((0, h))
    # left edge top->bottom
    x = 0
    for a, b in [(h, shelf_top_local + 1), (shelf_bottom_local - 1, 0)]:
        # going downward: a > b
        hi, lo = a, b
        if hi <= lo:
            continue
        mid = (hi + lo) / 2
        pts += [
            (x, hi),
            (x, mid + tab_h / 2),
            (x - T, mid + tab_h / 2),
            (x - T, mid - tab_h / 2),
            (x, mid - tab_h / 2),
            (x, lo),
        ]

    add_lwpoly(msp, [(ox + x, oy + y) for x, y in pts])
    # notch for shelf (slot open) — half-lap: cut T deep into divider where shelf crosses
    # shelf passes through: cut a slot from front to back of depth? Actually shelf has slot for divider,
    # divider needs matching notch of height T at shelf height.
    add_slot_rect(msp, ox + 4, oy + shelf_bottom_local, d - 8, T)
    add_label(msp, ox + 4, oy + h - 8, "DIVISORIA CENTRAL")


def draw_electronics_panel(msp, ox: float, oy: float):
    w, h = 70.0, 110.0
    add_lwpoly(msp, [(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)], True)
    # furos M3 (mesmo padrão da lateral direita)
    cx, cy = ox + w / 2, oy + h / 2
    for sx in (-28, 28):
        for sy in (-40, 40):
            add_circle(msp, cx + sx, cy + sy, 3.2)
    # slots de ventilação
    for i in range(5):
        add_slot_rect(msp, ox + 12, oy + 20 + i * 14, w - 24, 3)
    # passagem de cabos
    add_circle(msp, ox + w / 2, oy + 10, 8)
    add_label(msp, ox + 4, oy + h - 6, "PAINEL ELETRONICA")


def draw_reservoir_shelf(msp, ox: float, oy: float):
    """Prateleira externa simples para apoiar o reservatório ao lado."""
    w, d = 150.0, 120.0
    add_lwpoly(msp, [(ox, oy), (ox + w, oy), (ox + w, oy + d), (ox, oy + d)], True)
    # furos de fixação na lateral esquerda (casam com furos da lateral)
    for sx in (20, 70):
        for sy in (20, 60):
            add_circle(msp, ox + sx, oy + sy, 3.2)
    # furo mangueira
    add_circle(msp, ox + w - 25, oy + d / 2, HOSE_D)
    # borda antirrespingo (fenda para aba opcional)
    add_slot_rect(msp, ox + 10, oy + d - 8, w - 20, T)
    add_label(msp, ox + 4, oy + 4, "PRATELEIRA RESERVATORIO")


def draw_reservoir_riser(msp, ox: float, oy: float):
    """Aba frontal da prateleira do reservatório."""
    w, h = 150.0 - 20.0, 25.0
    # tab central para encaixar no slot da prateleira
    pts = [
        (0, 0),
        (w, 0),
        (w, h),
        (w / 2 + TAB_W / 2, h),
        (w / 2 + TAB_W / 2, h + T),
        (w / 2 - TAB_W / 2, h + T),
        (w / 2 - TAB_W / 2, h),
        (0, h),
        (0, 0),
    ]
    add_lwpoly(msp, [(ox + x, oy + y) for x, y in pts])
    add_label(msp, ox + 4, oy + 4, "ABA RESERVATORIO")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    msp = doc.modelspace()

    # layers
    doc.layers.add("CORTE", color=1)  # red = cut
    doc.layers.add("TEXTO", color=3)  # green = ignore / engrave optional
    doc.layers.add("INFO", color=5)

    # Empacotamento simples em fileiras
    cursor_x = SHEET_MARGIN
    cursor_y = SHEET_MARGIN
    row_h = 0.0
    max_x = 0.0

    def place(draw_fn, bbox_w, bbox_h, *args):
        nonlocal cursor_x, cursor_y, row_h, max_x
        # se não cabe na largura razoável da mesa (1300), quebra linha
        if cursor_x + bbox_w + SHEET_MARGIN > 1300:
            cursor_x = SHEET_MARGIN
            cursor_y += row_h + GAP
            row_h = 0.0
        draw_fn(msp, cursor_x, cursor_y, *args) if args else draw_fn(msp, cursor_x, cursor_y)
        cursor_x += bbox_w + GAP
        row_h = max(row_h, bbox_h)
        max_x = max(max_x, cursor_x)

    # margens extras pelos fingers/tabs (~T)
    place(draw_front, L + 2 * T + 4, H + 4)
    place(draw_back, L + 2 * T + 4, H + 4)
    place(draw_side, (D - 2 * T) + 2 * T + 4, H + 4, "LATERAL ESQ", False)
    place(draw_side, (D - 2 * T) + 2 * T + 4, H + 4, "LATERAL DIR", True)

    place(draw_bottom, (L - 2 * T) + 2 * T + 8, (D - 2 * T) + 2 * T + 8)
    place(draw_top, (L - 2 * T) + 2 * T + 8, (D - 2 * T) + 2 * T + 8)
    place(draw_shelf, (L - 2 * T) + 2 * T + 8, (D - 2 * T) + 2 * T + 8)
    place(draw_divider, (D - 2 * T) + 2 * T + 8, (H - 2 * T) + 8)

    place(draw_electronics_panel, 74, 114)
    place(draw_reservoir_shelf, 154, 124)
    place(draw_reservoir_riser, 140, 35)

    # bloco de informações (não cortar)
    info_x, info_y = SHEET_MARGIN, cursor_y + row_h + 30
    lines = [
        "Estrutura irrigacao TCC - 260 x 100 x 400 mm | MDF 3 mm",
        f"Prateleira vasos @ {SHELF_TOP:.0f} mm | furo Ø{POT_HOLE_D:.0f} mm | mangueira Ø{HOSE_D:.0f} mm",
        f"HC-SR04: distancia sensor->substrato ≈ {H - T - SHELF_TOP:.0f} mm (atualizar firmware)",
        f"Kerf compensado: {KERF} mm | Camada CORTE=cortar | TEXTO=ignorar/gravar",
        "Mesa: pecas cabem em 1300 x 1900 mm",
    ]
    for i, line in enumerate(lines):
        msp.add_text(
            line,
            height=4,
            dxfattribs={"layer": "INFO", "insert": (info_x, info_y - i * 8)},
        ).set_placement((info_x, info_y - i * 8), align=TextEntityAlignment.LEFT)

    doc.saveas(OUT_DXF)
    print(f"DXF salvo em: {OUT_DXF}")
    print(f"Envelope aprox. X: {max_x:.0f} mm | Y: {info_y + 20:.0f} mm")
    print(f"Sensor->substrato: {H - T - SHELF_TOP:.1f} mm")


if __name__ == "__main__":
    main()
