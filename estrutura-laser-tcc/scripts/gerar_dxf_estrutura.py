#!/usr/bin/env python3
"""
DXF 1:1 (mm) — estrutura FRENTE ABERTA.

260 x 100 x 400 mm | MDF 3 mm | 2 vasos | 2x HC-SR04
Encaixes tab-and-slot com entalhes de borda (sem slots “fantasma” na aresta).
"""

from __future__ import annotations

import math
from pathlib import Path

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

# --- parâmetros ---
L, D, H, T = 260.0, 100.0, 400.0, 3.0
SHELF_TOP = 85.0
POT_HOLE_D = 86.0          # vaso Ø9 cm prende pela borda
HOSE_D = 10.0
HCSR_EYE_D = 16.0
HCSR_EYE_SPACING = 25.4
HCSR_MOUNT = 2.5
TAB_W = 14.0
KERF = 0.10

INNER_L = L - 2 * T        # 254
INNER_D = D - T            # 97
DIV_X = (L - T) / 2        # início X divisória

SHEET_MARGIN, GAP = 12.0, 10.0
OUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUT_DXF = OUT_DIR / "estrutura_irrigacao_40cm_mdf3mm.dxf"
OUT_SVG = OUT_DIR / "estrutura_irrigacao_40cm_mdf3mm.svg"


def add_poly(msp, pts, closed=True, layer="CORTE"):
    clean = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-7:
            clean.append(p)
    msp.add_lwpolyline(clean, close=closed, dxfattribs={"layer": layer})


def add_rect(msp, x, y, w, h, layer="CORTE"):
    x, y = x + KERF / 2, y + KERF / 2
    w, h = max(0.2, w - KERF), max(0.2, h - KERF)
    add_poly(msp, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True, layer)


def add_circle(msp, cx, cy, d, layer="CORTE"):
    msp.add_circle((cx, cy), max(0.15, (d - KERF) / 2), dxfattribs={"layer": layer})


def add_label(msp, x, y, text, h=3.0):
    msp.add_text(text, height=h, dxfattribs={"layer": "TEXTO", "insert": (x, y)}).set_placement(
        (x, y), align=TextEntityAlignment.LEFT
    )


def back_tab_z_centers() -> list[float]:
    """Centros Z dos tabs laterais da traseira (evitam base/prateleira/tampa)."""
    zs = []
    for a, b in [(T + 10, SHELF_TOP - T - 10), (SHELF_TOP + 10, H - T - 10)]:
        if b - a < 40:
            continue
        n = 2 if b - a < 140 else 3
        for i in range(n):
            zs.append(a + (i + 1) * (b - a) / (n + 1))
    return zs


def horiz_y_tab() -> float:
    return INNER_D / 2


def back_x_tabs() -> list[float]:
    return [45.0, INNER_L - 45.0]


# ---------- contornos ----------
def side_outline() -> list[tuple[float, float]]:
    """
    Lateral D x H.
    Entalhes: base (baixo), tampa (cima), traseira (direita = fundo).
    """
    w, h = D, H
    y_tab = horiz_y_tab()
    pts: list[tuple[float, float]] = []

    # bottom edge L→R with notch for base tab
    pts.append((0, 0))
    a, b = y_tab - TAB_W / 2, y_tab + TAB_W / 2
    pts += [(a, 0), (a, T), (b, T), (b, 0)]
    pts.append((w, 0))

    # rear edge B→T with notches for back tabs
    for zc in sorted(back_tab_z_centers()):
        za, zb = zc - TAB_W / 2, zc + TAB_W / 2
        pts += [(w, za), (w - T, za), (w - T, zb), (w, zb)]
    pts.append((w, h))

    # top edge R→L with notch for top tab
    pts += [(b, h), (b, h - T), (a, h - T), (a, h)]
    pts.append((0, h))

    # front edge T→B (reta — frente aberta)
    pts.append((0, 0))
    return pts


def back_outline() -> list[tuple[float, float]]:
    """
    Traseira INNER_L x H.
    Tabs L/R para laterais; entalhes baixo/cima para base/tampa.
    """
    w, h = INNER_L, H
    xs = back_x_tabs()
    pts: list[tuple[float, float]] = []

    # bottom L→R with notches for base
    pts.append((0, 0))
    for xc in sorted(xs):
        a, b = xc - TAB_W / 2, xc + TAB_W / 2
        pts += [(a, 0), (a, T), (b, T), (b, 0)]
    pts.append((w, 0))

    # right B→T with tabs out
    for zc in sorted(back_tab_z_centers()):
        za, zb = zc - TAB_W / 2, zc + TAB_W / 2
        pts += [(w, za), (w + T, za), (w + T, zb), (w, zb)]
    pts.append((w, h))

    # top R→L with notches for top
    for xc in sorted(xs, reverse=True):
        a, b = xc - TAB_W / 2, xc + TAB_W / 2
        pts += [(b, h), (b, h - T), (a, h - T), (a, h)]
    pts.append((0, h))

    # left T→B with tabs out
    for zc in sorted(back_tab_z_centers(), reverse=True):
        za, zb = zc - TAB_W / 2, zc + TAB_W / 2
        pts += [(0, zb), (-T, zb), (-T, za), (0, za)]
    pts.append((0, 0))
    return pts


def horizontal_outline() -> list[tuple[float, float]]:
    """Painel INNER_L x INNER_D com tabs L/R/traseira; frente reta."""
    w, d = INNER_L, INNER_D
    y_tab = horiz_y_tab()
    pts = [(0, 0), (w, 0)]

    # right with one tab
    a, b = y_tab - TAB_W / 2, y_tab + TAB_W / 2
    pts += [(w, a), (w + T, a), (w + T, b), (w, b), (w, d)]

    # back with two tabs R→L
    for xc in sorted(back_x_tabs(), reverse=True):
        xa, xb = xc - TAB_W / 2, xc + TAB_W / 2
        pts += [(xb, d), (xb, d + T), (xa, d + T), (xa, d)]
    pts.append((0, d))

    # left with one tab T→B
    pts += [(0, b), (-T, b), (-T, a), (0, a), (0, 0)]
    return pts


# ---------- peças ----------
def draw_side(msp, ox, oy, name: str, electronics: bool):
    add_poly(msp, [(ox + x, oy + y) for x, y in side_outline()])

    # único slot interno: prateleira dos vasos
    sx = horiz_y_tab() - TAB_W / 2
    add_rect(msp, ox + sx, oy + (SHELF_TOP - T), TAB_W, T)

    add_circle(msp, ox + D - 22, oy + 28, HOSE_D)

    if electronics:
        cx, cy = ox + D / 2, oy + 230
        for dx in (-25, 25):
            for dy in (-35, 35):
                add_circle(msp, cx + dx, cy + dy, 3.2)
        add_label(msp, ox + 3, oy + H - 6, f"{name} — eletrônica")
    else:
        cx, cy = ox + 28, oy + 55
        for dx in (0, 40):
            for dy in (0, 35):
                add_circle(msp, cx + dx, cy + dy, 3.2)
        add_label(msp, ox + 3, oy + H - 6, f"{name} — reservatório")


def draw_back(msp, ox, oy):
    add_poly(msp, [(ox + x, oy + y) for x, y in back_outline()])

    # slot interno só da prateleira
    for xc in back_x_tabs():
        add_rect(msp, ox + xc - TAB_W / 2, oy + (SHELF_TOP - T), TAB_W, T)

    # slots da divisória (2 segmentos)
    x_div = DIV_X - T
    add_rect(msp, ox + x_div, oy + T + 3, T, max(1.0, (SHELF_TOP - T) - (T + 3) - 3))
    add_rect(msp, ox + x_div, oy + SHELF_TOP + 3, T, max(1.0, (H - T) - (SHELF_TOP + 3) - 3))

    add_circle(msp, ox + INNER_L * 0.25, oy + 28, HOSE_D)
    add_circle(msp, ox + INNER_L * 0.75, oy + 28, HOSE_D)

    # nicho reservatório (recorte interno fechado)
    add_rect(msp, ox + 18, oy + T + 6, 96, 60)

    add_label(msp, ox + 4, oy + H - 6, "TRASEIRA")


def draw_horizontal(msp, ox, oy, kind: str):
    add_poly(msp, [(ox + x, oy + y) for x, y in horizontal_outline()])

    x_div = DIV_X - T
    add_rect(msp, ox + x_div, oy + 10, T, INNER_D - 20)

    label = kind.upper()
    c1 = x_div / 2
    c2 = x_div + T + (INNER_L - x_div - T) / 2
    cy = INNER_D / 2

    if kind == "prateleira":
        add_circle(msp, ox + c1, oy + cy, POT_HOLE_D)
        add_circle(msp, ox + c2, oy + cy, POT_HOLE_D)
        label = f"PRATELEIRA VASOS Ø{POT_HOLE_D:.0f}"
    elif kind == "tampa":
        for cx in (c1, c2):
            # 2 olhos
            add_circle(msp, ox + cx - HCSR_EYE_SPACING / 2, oy + cy, HCSR_EYE_D)
            add_circle(msp, ox + cx + HCSR_EYE_SPACING / 2, oy + cy, HCSR_EYE_D)
            # 4 furos placa 45x20
            for sx in (-20.0, 20.0):
                for sy in (-7.5, 7.5):
                    add_circle(msp, ox + cx + sx, oy + cy + sy, HCSR_MOUNT)
        label = "TAMPA + 2x HC-SR04"

    add_label(msp, ox + 4, oy + 4, label if kind != "base" else "BASE")


def draw_divider(msp, ox, oy):
    w, h = INNER_D, H - 2 * T
    shelf_lo = SHELF_TOP - 2 * T
    shelf_hi = SHELF_TOP - T

    # tabs traseiros nos meios dos segmentos
    tabs = []
    if shelf_lo - 4 > TAB_W:
        tabs.append((2 + (shelf_lo - 2)) / 2)
    span = h - 2 - (shelf_hi + 2)
    if span > TAB_W + 4:
        if span > 160:
            tabs += [shelf_hi + 2 + span / 3, shelf_hi + 2 + 2 * span / 3]
        else:
            tabs.append(shelf_hi + 2 + span / 2)

    pts = [(0, 0), (w, 0)]
    for zc in sorted(tabs):
        a, b = zc - TAB_W / 2, zc + TAB_W / 2
        pts += [(w, a), (w + T, a), (w + T, b), (w, b)]
    pts += [(w, h), (0, h), (0, 0)]
    add_poly(msp, [(ox + x, oy + y) for x, y in pts])

    # notch da prateleira
    add_rect(msp, ox + 8, oy + shelf_lo, w - 16, T)
    add_label(msp, ox + 4, oy + h - 6, "DIVISÓRIA")


def draw_electronics_panel(msp, ox, oy):
    w, h = 65.0, 100.0
    add_poly(msp, [(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)])
    cx, cy = ox + w / 2, oy + h / 2
    for dx in (-25, 25):
        for dy in (-35, 35):
            add_circle(msp, cx + dx, cy + dy, 3.2)
    for i in range(4):
        add_rect(msp, ox + 10, oy + 22 + i * 16, w - 20, 3)
    add_circle(msp, ox + w / 2, oy + 10, 8)
    add_label(msp, ox + 3, oy + h - 5, "PAINEL ELETRÔNICA")


def draw_reservoir_shelf(msp, ox, oy):
    w, d = 140.0, 100.0
    add_poly(msp, [(ox, oy), (ox + w, oy), (ox + w, oy + d), (ox, oy + d)])
    for sx in (18, 58):
        for sy in (18, 53):
            add_circle(msp, ox + sx, oy + sy, 3.2)
    add_circle(msp, ox + w - 22, oy + d / 2, HOSE_D)
    add_label(msp, ox + 3, oy + 3, "PRATELEIRA RESERVATÓRIO")


def export_svg(doc):
    from ezdxf import bbox as bb

    msp = doc.modelspace()
    ext = bb.extents(msp)
    minx, miny, maxx, maxy = ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y
    pad = 8
    W, Hgt = maxx - minx + 2 * pad, maxy - miny + 2 * pad

    def tx(x, y):
        return x - minx + pad, (maxy - y) + pad

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{Hgt}mm" viewBox="0 0 {W} {Hgt}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for e in msp:
        if e.dxf.layer != "CORTE":
            continue
        if e.dxftype() == "CIRCLE":
            x, y = tx(e.dxf.center.x, e.dxf.center.y)
            parts.append(
                f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{e.dxf.radius:.3f}" fill="none" stroke="#c00" stroke-width="0.25"/>'
            )
        elif e.dxftype() == "LWPOLYLINE":
            pts = list(e.get_points("xy"))
            xs = [f"{tx(p[0], p[1])[0]:.3f},{tx(p[0], p[1])[1]:.3f}" for p in pts]
            if e.closed and xs:
                xs.append(xs[0])
            parts.append(
                f'<polyline points="{" ".join(xs)}" fill="none" stroke="#c00" stroke-width="0.25"/>'
            )
    parts.append("</svg>")
    OUT_SVG.write_text("\n".join(parts), encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    msp = doc.modelspace()
    doc.layers.add("CORTE", color=1)
    doc.layers.add("TEXTO", color=3)
    doc.layers.add("INFO", color=5)

    x = y = SHEET_MARGIN
    row_h = 0.0

    def place(fn, bw, bh, *args):
        nonlocal x, y, row_h
        if x + bw + SHEET_MARGIN > 1300:
            x = SHEET_MARGIN
            y += row_h + GAP
            row_h = 0.0
        fn(msp, x, y, *args) if args else fn(msp, x, y)
        x += bw + GAP
        row_h = max(row_h, bh)

    place(draw_side, D + 4, H + 4, "LATERAL ESQ", False)
    place(draw_side, D + 4, H + 4, "LATERAL DIR", True)
    place(draw_back, INNER_L + 2 * T + 8, H + 4)
    place(lambda m, a, b: draw_horizontal(m, a, b, "base"), INNER_L + 2 * T + 8, INNER_D + 2 * T + 8)
    place(lambda m, a, b: draw_horizontal(m, a, b, "prateleira"), INNER_L + 2 * T + 8, INNER_D + 2 * T + 8)
    place(lambda m, a, b: draw_horizontal(m, a, b, "tampa"), INNER_L + 2 * T + 8, INNER_D + 2 * T + 8)
    place(draw_divider, INNER_D + 2 * T + 8, H - 2 * T + 8)
    place(draw_electronics_panel, 70, 105)
    place(draw_reservoir_shelf, 145, 105)

    info_y = y + row_h + 26
    for i, line in enumerate(
        [
            "Frente ABERTA | 260x100x400 mm | MDF 3 mm | tab-and-slot",
            f"Vaso Ø{POT_HOLE_D:.0f} (folga {(INNER_D-POT_HOLE_D)/2:.1f} mm) | HC-SR04→substrato ≈ {H-T-SHELF_TOP:.0f} mm",
            f"Kerf {KERF} mm | CORTE=cortar | TEXTO/INFO=ignorar",
        ]
    ):
        msp.add_text(
            line, height=3.6, dxfattribs={"layer": "INFO", "insert": (SHEET_MARGIN, info_y - i * 7)}
        ).set_placement((SHEET_MARGIN, info_y - i * 7), align=TextEntityAlignment.LEFT)

    doc.saveas(OUT_DXF)
    export_svg(doc)
    print("DXF", OUT_DXF)
    print("SVG", OUT_SVG)
    print("back tabs Z", [round(z, 1) for z in back_tab_z_centers()])
    print(f"folga vaso {(INNER_D-POT_HOLE_D)/2:.1f} mm")


if __name__ == "__main__":
    main()
