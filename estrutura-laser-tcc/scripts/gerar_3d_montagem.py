#!/usr/bin/env python3
"""Montagem 3D — frente aberta, encaixes revisados."""

from __future__ import annotations

from pathlib import Path

import cadquery as cq
import numpy as np

L, D, H, T = 260.0, 100.0, 400.0, 3.0
SHELF_TOP = 85.0
POT_HOLE_D = 86.0
HOSE_D = 10.0
HCSR_EYE_D = 16.0
HCSR_EYE_SPACING = 25.4
TAB_W = 14.0
INNER_L = L - 2 * T
INNER_D = D - T
DIV_X = (L - T) / 2

OUT = Path(__file__).resolve().parents[1] / "output"
RENDER_DIR = OUT / "renders"


def box_at(x0, y0, z0, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


def hole_x(x0, cy, cz, r, length):
    return cq.Workplane("YZ").workplane(offset=x0).center(cy, cz).circle(r).extrude(length)


def hole_y(y0, cx, cz, r, length):
    return cq.Workplane("XZ").workplane(offset=y0).center(cx, cz).circle(r).extrude(length)


def hole_z(z0, cx, cy, r, length):
    return cq.Workplane("XY").workplane(offset=z0).center(cx, cy).circle(r).extrude(length)


def back_tab_z_centers():
    zs = []
    for a, b in [(T + 10, SHELF_TOP - T - 10), (SHELF_TOP + 10, H - T - 10)]:
        if b - a < 40:
            continue
        n = 2 if b - a < 140 else 3
        for i in range(n):
            zs.append(a + (i + 1) * (b - a) / (n + 1))
    return zs


def side_panel(x0: float) -> cq.Workplane:
    p = box_at(x0, 0, 0, T, D, H)
    y_tab = INNER_D / 2
    # entalhe base / tampa
    p = p.cut(box_at(x0 - 0.05, y_tab - TAB_W / 2, 0, T + 0.1, TAB_W, T))
    p = p.cut(box_at(x0 - 0.05, y_tab - TAB_W / 2, H - T, T + 0.1, TAB_W, T))
    # entalhes traseira
    for zc in back_tab_z_centers():
        p = p.cut(box_at(x0 - 0.05, D - T, zc - TAB_W / 2, T + 0.1, T, TAB_W))
    # slot prateleira (interno)
    p = p.cut(box_at(x0 - 0.05, y_tab - TAB_W / 2, SHELF_TOP - T, T + 0.1, TAB_W, T))
    p = p.cut(hole_x(x0 - 0.05, D - 22, 28, HOSE_D / 2, T + 0.1))
    return p


def back_panel() -> cq.Workplane:
    p = box_at(T, D - T, 0, INNER_L, T, H)
    for xc in (45.0, INNER_L - 45.0):
        # entalhes base/tampa
        p = p.cut(box_at(T + xc - TAB_W / 2, D - T - 0.05, 0, TAB_W, T + 0.1, T))
        p = p.cut(box_at(T + xc - TAB_W / 2, D - T - 0.05, H - T, TAB_W, T + 0.1, T))
        # slot prateleira
        p = p.cut(box_at(T + xc - TAB_W / 2, D - T - 0.05, SHELF_TOP - T, TAB_W, T + 0.1, T))
    p = p.cut(box_at(DIV_X, D - T - 0.05, T + 3, T, T + 0.1, max(1.0, SHELF_TOP - T - T - 6)))
    p = p.cut(box_at(DIV_X, D - T - 0.05, SHELF_TOP + 3, T, T + 0.1, max(1.0, H - T - SHELF_TOP - 6)))
    for x in (T + INNER_L * 0.25, T + INNER_L * 0.75):
        p = p.cut(hole_y(D - T - 0.05, x, 28, HOSE_D / 2, T + 0.1))
    p = p.cut(box_at(T + 18, D - T - 0.05, T + 6, 96, T + 0.1, 60))
    return p


def pot_centers():
    x_div_local = DIV_X - T
    c1 = T + x_div_local / 2
    c2 = T + x_div_local + T + (INNER_L - x_div_local - T) / 2
    return (c1, INNER_D / 2), (c2, INNER_D / 2)


def horizontal(z0: float, pots=False, sensors=False) -> cq.Workplane:
    p = box_at(T, 0, z0, INNER_L, INNER_D, T)
    p = p.cut(box_at(DIV_X, 10, z0 - 0.05, T, INNER_D - 20, T + 0.1))
    (c1x, cy), (c2x, _) = pot_centers()
    if pots:
        for cx in (c1x, c2x):
            p = p.cut(hole_z(z0 - 0.05, cx, cy, POT_HOLE_D / 2, T + 0.1))
    if sensors:
        for cx in (c1x, c2x):
            for sx in (-HCSR_EYE_SPACING / 2, HCSR_EYE_SPACING / 2):
                p = p.cut(hole_z(z0 - 0.05, cx + sx, cy, HCSR_EYE_D / 2, T + 0.1))
    return p


def divider() -> cq.Workplane:
    p = box_at(DIV_X, 0, T, T, INNER_D, H - 2 * T)
    p = p.cut(box_at(DIV_X - 0.05, 8, SHELF_TOP - T, T + 0.1, INNER_D - 16, T))
    return p


def electronics_panel() -> cq.Workplane:
    w, h = 65.0, 100.0
    return box_at(L, (D - w) / 2, 230 - h / 2, T, w, h)


def reservoir_shelf() -> cq.Workplane:
    w, d = 140.0, 100.0
    return box_at(-w, (D - d) / 2, 40.0, w, d, T)


def pot_placeholder(cx, cy):
    return (
        cq.Workplane("XY")
        .workplane(offset=SHELF_TOP - 70)
        .center(cx, cy)
        .circle(36)
        .workplane(offset=70)
        .circle(42)
        .loft()
    )


def sensor_placeholder(cx, cy):
    return box_at(cx - 22.5, cy - 10, H - T - 8, 45, 20, 8)


def build_assembly() -> cq.Assembly:
    assy = cq.Assembly(name="estrutura_frente_aberta_40cm")
    wood, wood_d = cq.Color(0.82, 0.70, 0.45), cq.Color(0.72, 0.60, 0.38)
    assy.add(side_panel(0), name="lateral_esq", color=wood)
    assy.add(side_panel(L - T), name="lateral_dir", color=wood)
    assy.add(back_panel(), name="traseira", color=wood_d)
    assy.add(horizontal(0), name="base", color=wood_d)
    assy.add(horizontal(SHELF_TOP - T, pots=True), name="prateleira", color=wood)
    assy.add(horizontal(H - T, sensors=True), name="tampa", color=wood)
    assy.add(divider(), name="divisoria", color=wood_d)
    assy.add(electronics_panel(), name="painel_eletronic", color=cq.Color(0.55, 0.55, 0.58))
    assy.add(reservoir_shelf(), name="prat_reservatorio", color=cq.Color(0.65, 0.72, 0.80))
    (c1x, cy), (c2x, _) = pot_centers()
    assy.add(pot_placeholder(c1x, cy), name="vaso_1", color=cq.Color(0.12, 0.12, 0.12))
    assy.add(pot_placeholder(c2x, cy), name="vaso_2", color=cq.Color(0.12, 0.12, 0.12))
    assy.add(sensor_placeholder(c1x, cy), name="hcsr_1", color=cq.Color(0.15, 0.35, 0.75))
    assy.add(sensor_placeholder(c2x, cy), name="hcsr_2", color=cq.Color(0.15, 0.35, 0.75))
    return assy


def assembly_to_compound(assy: cq.Assembly) -> cq.Workplane:
    solids = []
    for _n, part in assy.traverse():
        if part.obj is None:
            continue
        shape = part.obj.val() if hasattr(part.obj, "val") else part.obj
        solids.append(shape.moved(part.loc))
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(solids)])


def export_glb_colored(assy, glb_path: Path):
    import tempfile
    import trimesh

    COLORS = {
        "lateral_esq": (210, 179, 115),
        "lateral_dir": (210, 179, 115),
        "traseira": (185, 155, 98),
        "base": (170, 140, 88),
        "prateleira": (200, 170, 110),
        "tampa": (215, 185, 125),
        "divisoria": (175, 145, 90),
        "painel_eletronic": (140, 140, 148),
        "prat_reservatorio": (160, 185, 205),
        "vaso_1": (30, 30, 30),
        "vaso_2": (30, 30, 30),
        "hcsr_1": (40, 90, 190),
        "hcsr_2": (40, 90, 190),
    }
    scene = trimesh.Scene()
    tmp = Path(tempfile.mkdtemp())
    meshes = []
    for name, part in assy.traverse():
        if part.obj is None:
            continue
        leaf = name.split("/")[-1] if isinstance(name, str) else str(name)
        shape = (part.obj.val() if hasattr(part.obj, "val") else part.obj).moved(part.loc)
        stl = tmp / f"{leaf}.stl"
        cq.exporters.export(cq.Workplane("XY").newObject([shape]), str(stl))
        mesh = trimesh.load_mesh(stl)
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
        rgb = COLORS.get(leaf, (180, 180, 180))
        mesh.visual.face_colors = np.tile(list(rgb) + [255], (len(mesh.faces), 1))
        scene.add_geometry(mesh, node_name=leaf)
        meshes.append((leaf, mesh, rgb))
    scene.export(glb_path)
    return meshes


def render_views(part_meshes):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    views = {
        "isometrico": dict(elev=22, azim=-35),
        "frente": dict(elev=8, azim=-90),
        "lado": dict(elev=8, azim=10),
        "topo": dict(elev=80, azim=-90),
    }
    for vname, ang in views.items():
        fig = plt.figure(figsize=(9, 9), facecolor="white")
        ax = fig.add_subplot(111, projection="3d")
        all_v = []
        for leaf, mesh, rgb in part_meshes:
            m = mesh.simplify_quadric_decimation(12000) if len(mesh.faces) > 12000 else mesh
            coll = Poly3DCollection(m.vertices[m.faces], linewidths=0.02)
            r, g, b = [c / 255 for c in rgb]
            coll.set_facecolor((r, g, b, 0.95))
            coll.set_edgecolor((0.2, 0.15, 0.1, 0.1))
            ax.add_collection3d(coll)
            all_v.append(m.vertices)
        V = np.vstack(all_v)
        ax.auto_scale_xyz(V[:, 0], V[:, 1], V[:, 2])
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Z (mm)")
        ax.view_init(**ang)
        try:
            ax.set_box_aspect((V[:, 0].ptp() or 1, V[:, 1].ptp() or 1, V[:, 2].ptp() or 1))
        except Exception:
            pass
        ax.set_title(f"Frente aberta 260×100×400 — {vname}")
        out = RENDER_DIR / f"montagem_{vname}.png"
        fig.savefig(out, dpi=170, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print("render:", out)


def write_viewer_html():
    (OUT / "viewer_montagem.html").write_text(
        """<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Montagem 3D — Frente aberta</title>
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
<style>html,body{margin:0;height:100%;background:#1a1a1a;color:#eee;font-family:system-ui,sans-serif}
header{padding:12px 16px;background:#111;border-bottom:1px solid #333}
h1{margin:0;font-size:18px}p{margin:4px 0 0;font-size:13px;opacity:.8}
model-viewer{width:100%;height:calc(100% - 64px);background:#222}</style></head><body>
<header><h1>Estrutura irrigação — frente aberta</h1>
<p>260 × 100 × 400 mm · MDF 3 mm · arraste para girar</p></header>
<model-viewer src="montagem_estrutura_40cm.glb" camera-controls auto-rotate
 shadow-intensity="0.6" exposure="1" touch-action="pan-y"></model-viewer>
</body></html>""",
        encoding="utf-8",
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assy = build_assembly()
    compound = assembly_to_compound(assy)
    stl, step, glb = OUT / "montagem_estrutura_40cm.stl", OUT / "montagem_estrutura_40cm.step", OUT / "montagem_estrutura_40cm.glb"
    cq.exporters.export(compound, str(stl))
    cq.exporters.export(compound, str(step))
    try:
        assy.save(str(OUT / "montagem_estrutura_40cm_assembly.step"))
    except Exception as e:
        print("assembly skip", e)
    meshes = export_glb_colored(assy, glb)
    render_views(meshes)
    write_viewer_html()
    print("OK")


if __name__ == "__main__":
    main()
