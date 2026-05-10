#!/usr/bin/env python3
"""
Publication-grade OVITO renders of the cached MACE-MH-1 relaxed structures.

Loads the .traj files from phase_diagrams/mace_cache/ and renders each as a
high-resolution PNG via OVITO's Tachyon ray-tracer. Produces:

  figures/presentation/ovito/
    bcc_R1_HfNbTaTiZr.png         relaxed BCC supercell, R1
    bcc_R2_MoNbTaTiV.png          relaxed BCC supercell, R2
    bcc_R3_ISRU_blend.png         relaxed BCC supercell, R3
    isru_phases_BCC_FCC_HCP.png   ISRU blend across phases (3-up composite)
    isru_md_T0_vs_T2000.png       ISRU blend before vs after MD (composite)

Element colours match slide_07/08/09 of the matplotlib renders so the
two sets stay visually consistent.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PIL import Image  # Pillow comes with matplotlib; used for compositing

import ovito
from ovito.io import import_file
from ovito.vis import Viewport, TachyonRenderer
from ovito.modifiers import ColorCodingModifier  # noqa: F401  (kept for ref)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "phase_diagrams" / "mace_cache"
OUT = ROOT / "figures" / "presentation" / "ovito"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Element colours (RGB 0–1, must match slides 07/08/09)
# ---------------------------------------------------------------------------
ELEMENT_COLORS = {
    "Fe": (232/255, 112/255, 42/255),   # warm orange
    "Ti": (191/255, 194/255, 199/255),  # light grey
    "Al": (191/255, 166/255, 160/255),  # tan
    "Nb": (114/255, 194/255, 201/255),  # teal
    "Ta": (77/255,  166/255, 224/255),  # sky blue
    "Mo": (84/255,  178/255, 84/255),   # green
    "V":  (166/255, 166/255, 166/255),  # neutral grey
    "Hf": (77/255,  182/255, 241/255),  # azure
    "Zr": (148/255, 224/255, 224/255),  # pale teal
}

# Atomic radii in Angstroms (slightly enlarged for visual clarity)
RADII = {
    "Fe": 1.10, "Ti": 1.30, "Al": 1.20, "Nb": 1.40, "Ta": 1.40,
    "Mo": 1.35, "V":  1.20, "Hf": 1.50, "Zr": 1.50,
}


# ---------------------------------------------------------------------------
# Render one structure
# ---------------------------------------------------------------------------
def render(traj: Path, out_png: Path, *, size=(1600, 1200), tile=(1, 1, 2),
           camera_dir=(2, -3, 1), look_at=None, scale=1.0) -> Path:
    """Render a relaxed .traj as a PNG via OVITO Tachyon (ray-traced)."""
    pipeline = import_file(str(traj))

    # Replicate the cell so the supercell looks more bulk-like
    if tile != (1, 1, 1):
        from ovito.modifiers import ReplicateModifier
        pipeline.modifiers.append(ReplicateModifier(num_x=tile[0],
                                                     num_y=tile[1],
                                                     num_z=tile[2]))

    pipeline.add_to_scene()
    data = pipeline.compute()

    # Per-particle colours and radii by chemical symbol.
    # OVITO 3.x requires the trailing-underscore (mutable) accessor.
    types = data.particles_.particle_types_
    for pt in types.types_:
        sym = pt.name
        if sym in ELEMENT_COLORS:
            pt.color = ELEMENT_COLORS[sym]
        if sym in RADII:
            pt.radius = RADII[sym]

    # Camera framing
    cell = data.cell.matrix  # 3x4 matrix; 4th column = origin
    a, b, c = cell[:, 0], cell[:, 1], cell[:, 2]
    centre = 0.5 * (a + b + c) + cell[:, 3]
    if look_at is None:
        look_at = tuple(centre.tolist())

    # Pull the camera back proportional to the cell diagonal
    diag = float(np.linalg.norm(a + b + c))
    cam_pos = tuple(np.array(look_at) +
                    np.array(camera_dir) / np.linalg.norm(camera_dir) * diag * 1.5)

    vp = Viewport(type=Viewport.Type.Perspective,
                  camera_pos=cam_pos,
                  camera_dir=tuple(-np.array(camera_dir) /
                                    np.linalg.norm(camera_dir)),
                  fov=np.deg2rad(35) * scale)
    vp.zoom_all()

    renderer = TachyonRenderer(
        ambient_occlusion=True,
        ambient_occlusion_brightness=0.8,
        antialiasing_samples=12,
        direct_light_intensity=0.95,
        shadows=True,
    )
    vp.render_image(size=size, filename=str(out_png), renderer=renderer,
                    background=(1.0, 1.0, 1.0), alpha=False)
    pipeline.remove_from_scene()
    print(f"  ✓ {out_png.relative_to(ROOT)}")
    return out_png


# ---------------------------------------------------------------------------
# Composites
# ---------------------------------------------------------------------------
def composite_horizontal(panels: list[Path], out_png: Path,
                          titles: list[str] | None = None,
                          gap: int = 24, top_margin: int = 80,
                          font_size: int = 36) -> Path:
    """Stitch images horizontally with optional titles above each panel."""
    from PIL import ImageDraw, ImageFont

    images = [Image.open(p) for p in panels]
    h = max(im.height for im in images)
    w = sum(im.width for im in images) + gap * (len(images) - 1)
    canvas = Image.new("RGB", (w, h + top_margin), "white")

    x = 0
    for i, im in enumerate(images):
        canvas.paste(im, (x, top_margin))
        if titles:
            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",
                                          font_size)
            except OSError:
                font = ImageFont.load_default()
            title = titles[i]
            bbox = draw.textbbox((0, 0), title, font=font)
            text_w = bbox[2] - bbox[0]
            draw.text((x + (im.width - text_w) // 2, 20), title,
                      fill="black", font=font)
        x += im.width + gap

    canvas.save(out_png)
    print(f"  ✓ {out_png.relative_to(ROOT)} (composite)")
    return out_png


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print(f"OVITO {ovito.version}  rendering to {OUT.relative_to(ROOT)}/")

    # ---- Per-composition BCC supercells ----
    panels_bcc = []
    for short, comp_name in [("R1", "R1_HfNbTaTiZr"),
                              ("R2", "R2_MoNbTaTiV"),
                              ("R3", "R3_ISRU_blend")]:
        traj = CACHE / f"relaxed_bcc_{comp_name}.traj"
        out = OUT / f"bcc_{comp_name}.png"
        render(traj, out, size=(1400, 1400), tile=(1, 1, 2))
        panels_bcc.append(out)
    composite_horizontal(
        panels_bcc, OUT / "bcc_all_three.png",
        titles=["R1 – HfNbTaTiZr", "R2 – MoNbTaTiV", "R3 – ISRU blend"],
    )

    # ---- ISRU blend across BCC / FCC / HCP ----
    panels_phases = []
    tile_per_phase = {"bcc": (1, 1, 2), "fcc": (1, 1, 3), "hcp": (1, 1, 2)}
    for ph in ("bcc", "fcc", "hcp"):
        traj = CACHE / f"relaxed_{ph}_R3_ISRU_blend.traj"
        out = OUT / f"isru_{ph}.png"
        render(traj, out, size=(1400, 1400), tile=tile_per_phase[ph])
        panels_phases.append(out)
    composite_horizontal(
        panels_phases, OUT / "isru_phases_BCC_FCC_HCP.png",
        titles=["BCC", "FCC", "HCP"],
    )

    # ---- ISRU blend: T = 0 K vs T = 2000 K MD ----
    md_hot = CACHE / "md_T2000.traj"
    if md_hot.exists():
        relax = OUT / "isru_T0_relaxed.png"
        hot = OUT / "isru_T2000_md.png"
        render(CACHE / "relaxed_bcc_R3_ISRU_blend.traj", relax,
               size=(1400, 1400), tile=(1, 1, 2))
        render(md_hot, hot, size=(1400, 1400), tile=(1, 1, 2))
        composite_horizontal(
            [relax, hot], OUT / "isru_md_T0_vs_T2000.png",
            titles=["T = 0 K (relaxed)", "T = 2000 K (final MD)"],
        )

    print("\nAll OVITO renders written to:", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
