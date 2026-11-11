#!/usr/bin/env python3
"""
Montagem 3D da estrutura laser Minha Horta (260 x 100 x 400 mm, MDF 3 mm).

Gera STL, STEP, GLB, renders PNG e viewer HTML.
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq

L, D, H, T = 260.0, 100.0, 400.0, 3.0
SHELF_TOP = 85.0
POT_HOLE_D = 90.0
HOSE_D = 10.0
HCSR_EYE_D = 16.2
HCSR_EYE_SPACING = 25.4
TAB_W = 12.0

OUT = Path(__file__).resolve().parents[1] / "output"
RENDER_DIR = OUT / "renders"


def box_at(x0: float, y0: float, z0: float, dx: float, dy: float, dz: float) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


def hole_x(x0: float, cy: float, cz: float, r: float, length: float) -> cq.Workplane:
    """Cilindro ao longo de +X a partir de x0."""
    return (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .center(cy, cz)
        .circle(r)
        .extrude(length)
    )


def hole_y(y0: float, cx: float, cz: float, r: float, length: float) -> cq.Workplane:
    """Cilindro ao longo de +Y a partir de y0."""
    return (
        cq.Workplane("XZ")
        .workplane(offset=y0)
        .center(cx, cz)
        .circle(r)
        .extrude(length)
    )


def hole_z(z0: float, cx: float, cy: float, r: float, length: float) -> cq.Workplane:
    """Cilindro ao longo de +Z a partir de z0."""
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(cx, cy)
        .circle(r)
        .extrude(length)
    )


def cut_wall_slots_front_back(panel: cq.Workplane, y0: float) -> cq.Workplane:
    for z in (0.0, SHELF_TOP - T, H - T):
        for x in (40.0, L - 40.0 - TAB_W):
            panel = panel.cut(box_at(x, y0 - 0.05, z, TAB_W, T + 0.1, T))
    x_div = (L - T) / 2
    h1 = max(1.0, SHELF_TOP - T - (T + 1) - 1)
    h2 = max(1.0, (H - T) - (SHELF_TOP + 1) - 1)
    panel = panel.cut(box_at(x_div, y0 - 0.05, T + 1, T, T + 0.1, h1))
    panel = panel.cut(box_at(x_div, y0 - 0.05, SHELF_TOP + 1, T, T + 0.1, h2))
    return panel


def front_panel() -> cq.Workplane:
    p = box_at(0, 0, 0, L, T, H)
    p = cut_wall_slots_front_back(p, 0)
    for x in (L * 0.25, L * 0.75):
        p = p.cut(hole_y(-0.05, x, 25.0, HOSE_D / 2, T + 0.1))
    return p


def back_panel() -> cq.Workplane:
    y0 = D - T
    p = box_at(0, y0, 0, L, T, H)
    p = cut_wall_slots_front_back(p, y0)
    for x in (L * 0.25, L * 0.75):
        p = p.cut(hole_y(y0 - 0.05, x, 25.0, HOSE_D / 2, T + 0.1))
    p = p.cut(box_at(20, y0 - 0.05, T + 2, 110, T + 0.1, 70))
    return p


def side_panel(x0: float) -> cq.Workplane:
    p = box_at(x0, T, 0, T, D - 2 * T, H)
    for z in (0.0, SHELF_TOP - T, H - T):
        p = p.cut(box_at(x0 - 0.05, T + (D - 2 * T - TAB_W) / 2, z, T + 0.1, TAB_W, T))
    cy = T + (D - 2 * T) / 2
    p = p.cut(hole_x(x0 - 0.05, cy, 25.0, HOSE_D / 2, T + 0.1))
    return p


def pot_centers() -> tuple[tuple[float, float], tuple[float, float]]:
    dx = L - 2 * T
    c1 = T + (dx / 2 - T / 2) / 2
    c2 = T + dx / 2 + T / 2 + (dx / 2 - T / 2) / 2
    cy = T + (D - 2 * T) / 2
    return (c1, cy), (c2, cy)


def horizontal_panel(z0: float, pots: bool = False, sensors: bool = False) -> cq.Workplane:
    x0, y0 = T, T
    dx, dy = L - 2 * T, D - 2 * T
    p = box_at(x0, y0, z0, dx, dy, T)
    p = p.cut(box_at(x0 + (dx - T) / 2, y0 + 8, z0 - 0.05, T, dy - 16, T + 0.1))
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
    p = box_at((L - T) / 2, T, T, T, D - 2 * T, H - 2 * T)
    p = p.cut(box_at((L - T) / 2 - 0.05, T + 4, SHELF_TOP - T, T + 0.1, D - 2 * T - 8, T))
    return p


def electronics_panel() -> cq.Workplane:
    w, h = 70.0, 110.0
    y0 = T + (D - 2 * T - w) / 2
    z0 = 220.0 - h / 2
    p = box_at(L, y0, z0, T, w, h)
    for i in range(5):
        p = p.cut(box_at(L - 0.05, y0 + 12, z0 + 20 + i * 14, T + 0.1, w - 24, 3))
    return p


def reservoir_shelf() -> cq.Workplane:
    w, d = 150.0, 120.0
    return box_at(-w, (D - d) / 2, 40.0, w, d, T)


def pot_placeholder(cx: float, cy: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=SHELF_TOP - 70)
        .center(cx, cy)
        .circle(38)
        .workplane(offset=70)
        .circle(44)
        .loft()
    )


def sensor_placeholder(cx: float, cy: float) -> cq.Workplane:
    return box_at(cx - 22.5, cy - 10, H - T - 8, 45, 20, 8)


def build_assembly() -> cq.Assembly:
    assy = cq.Assembly(name="estrutura_irrigacao_40cm")
    wood = cq.Color(0.82, 0.70, 0.45)
    wood_d = cq.Color(0.72, 0.60, 0.38)
    assy.add(front_panel(), name="frente", color=wood)
    assy.add(back_panel(), name="traseira", color=wood_d)
    assy.add(side_panel(0), name="lateral_esq", color=wood)
    assy.add(side_panel(L - T), name="lateral_dir", color=wood)
    assy.add(horizontal_panel(0), name="base", color=wood_d)
    assy.add(horizontal_panel(SHELF_TOP - T, pots=True), name="prateleira", color=wood)
    assy.add(horizontal_panel(H - T, sensors=True), name="tampa", color=wood)
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
    for _name, part in assy.traverse():
        if part.obj is None:
            continue
        shape = part.obj.val() if hasattr(part.obj, "val") else part.obj
        solids.append(shape.moved(part.loc))
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(solids)])


def export_glb(stl_path: Path, glb_path: Path) -> None:
    import trimesh

    mesh = trimesh.load_mesh(stl_path)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    mesh.export(glb_path)


def render_from_stl(stl_path: Path) -> None:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import trimesh

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load_mesh(stl_path)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if len(mesh.faces) > 35000:
        mesh = mesh.simplify_quadric_decimation(35000)

    verts = mesh.vertices
    tris = verts[mesh.faces]
    views = {
        "isometrico": dict(elev=25, azim=-55),
        "frente": dict(elev=8, azim=-90),
        "lado": dict(elev=8, azim=0),
        "topo": dict(elev=85, azim=-90),
    }
    for name, ang in views.items():
        fig = plt.figure(figsize=(8, 8), facecolor="white")
        ax = fig.add_subplot(111, projection="3d")
        coll = Poly3DCollection(tris, alpha=0.93, linewidths=0.04)
        coll.set_facecolor((0.83, 0.71, 0.48, 0.96))
        coll.set_edgecolor((0.35, 0.28, 0.18, 0.2))
        ax.add_collection3d(coll)
        ax.auto_scale_xyz(verts[:, 0], verts[:, 1], verts[:, 2])
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Z (mm)")
        ax.view_init(**ang)
        try:
            ax.set_box_aspect((verts[:, 0].ptp() or 1, verts[:, 1].ptp() or 1, verts[:, 2].ptp() or 1))
        except Exception:
            pass
        ax.set_title(f"Montagem 260×100×400 mm — {name}")
        out = RENDER_DIR / f"montagem_{name}.png"
        fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print("render:", out)


def write_viewer_html() -> None:
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Montagem 3D — Estrutura 40 cm</title>
  <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
  <style>
    html, body { margin:0; height:100%; background:#1a1a1a; color:#eee; font-family: system-ui, sans-serif; }
    header { padding:12px 16px; background:#111; border-bottom:1px solid #333; }
    h1 { margin:0; font-size:18px; font-weight:600; }
    p { margin:4px 0 0; font-size:13px; opacity:.8; }
    model-viewer { width:100%; height:calc(100% - 64px); background:#222; }
  </style>
</head>
<body>
  <header>
    <h1>Estrutura irrigação — montagem 3D</h1>
    <p>260 × 100 × 400 mm · MDF 3 mm · arraste para girar · scroll para zoom</p>
  </header>
  <model-viewer
    src="montagem_estrutura_40cm.glb"
    alt="Montagem da estrutura laser"
    camera-controls
    touch-action="pan-y"
    auto-rotate
    shadow-intensity="0.6"
    exposure="1.0"
  ></model-viewer>
</body>
</html>
"""
    path = OUT / "viewer_montagem.html"
    path.write_text(html, encoding="utf-8")
    print("viewer:", path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("Construindo montagem…")
    assy = build_assembly()
    compound = assembly_to_compound(assy)

    stl_path = OUT / "montagem_estrutura_40cm.stl"
    step_path = OUT / "montagem_estrutura_40cm.step"
    glb_path = OUT / "montagem_estrutura_40cm.glb"

    print("Exportando STL / STEP…")
    cq.exporters.export(compound, str(stl_path))
    cq.exporters.export(compound, str(step_path))
    try:
        assy.save(str(OUT / "montagem_estrutura_40cm_assembly.step"))
    except Exception as exc:
        print("assembly STEP skip:", exc)

    print("Exportando GLB…")
    export_glb(stl_path, glb_path)
    print("Renders…")
    render_from_stl(stl_path)
    write_viewer_html()

    print("OK")
    for p in (stl_path, step_path, glb_path):
        print(f"  {p.name}: {p.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
