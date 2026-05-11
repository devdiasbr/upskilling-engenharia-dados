#!/usr/bin/env python3
"""Gera os 4 assets PNG da identidade visual NTT DATA UNIVERSITY."""

from pathlib import Path
from PIL import Image, ImageDraw

ORANGE = (245, 129, 31, 255)
WHITE  = (255, 255, 255, 230)
DARK   = (50, 60, 80, 220)

ASSETS_DIR = Path(__file__).parent.parent / "assets" / "ntt-template"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def make_bookmark_small(filename="bookmark_small.png", w=50, h=120, color=ORANGE):
    """Marcador pequeno laranja com entalhe V no fundo."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    notch_depth = int(h * 0.18)
    d.polygon([
        (0, 0), (w, 0), (w, h), (w // 2, h - notch_depth), (0, h)
    ], fill=color)
    img.save(ASSETS_DIR / filename)
    print(f"Salvo: {ASSETS_DIR / filename}")


def make_bookmark_large_outline(filename="bookmark_large_outline.png",
                                 w=400, h=680, color=ORANGE, line_w=10):
    """U fechado no topo (reta horizontal) com bandeirinha pequena no meio.

    Estrutura:
    - Outer: forma de "U" fechada — topo horizontal reto, dois lados verticais,
      fundo semicircular (capsula/U).
    - Inner: bandeirinha (pennant) pequena centralizada no terco superior,
      com entalhe em V no fundo.
    """
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    margin = line_w
    top = margin
    bottom = h - margin

    # ─── OUTER: U fechado ────────────────────────────────────────────────────
    # Onde a parte reta termina e o arco do U comeca (raio do arco = w/2)
    arc_diam = w - 2 * margin
    arc_radius = arc_diam // 2
    straight_bottom = bottom - arc_radius
    # Top horizontal
    d.line([(margin, top), (w - margin, top)], fill=color, width=line_w)
    # Left vertical
    d.line([(margin, top), (margin, straight_bottom)], fill=color, width=line_w)
    # Right vertical
    d.line([(w - margin, top), (w - margin, straight_bottom)], fill=color, width=line_w)
    # Semicirculo do fundo (180° arc)
    d.arc(
        [(margin, straight_bottom - arc_radius),
         (w - margin, straight_bottom + arc_radius)],
        start=0, end=180, fill=color, width=line_w,
    )

    # ─── INNER: bandeirinha centralizada ─────────────────────────────────────
    inner_w = int(w * 0.36)
    inner_x = (w - inner_w) // 2
    inner_top = top + int(h * 0.07)
    inner_h = int(h * 0.50)
    inner_notch_top = inner_top + int(inner_h * 0.78)
    inner_bottom = inner_top + inner_h
    cx = w // 2
    inner_right = inner_x + inner_w
    # Topo horizontal da bandeirinha
    d.line([(inner_x, inner_top), (inner_right, inner_top)], fill=color, width=line_w)
    # Lado esquerdo
    d.line([(inner_x, inner_top), (inner_x, inner_notch_top)], fill=color, width=line_w)
    # Lado direito
    d.line([(inner_right, inner_top), (inner_right, inner_notch_top)], fill=color, width=line_w)
    # V notch no fundo da bandeirinha
    d.line([(inner_x, inner_notch_top), (cx, inner_bottom)], fill=color, width=line_w)
    d.line([(cx, inner_bottom), (inner_right, inner_notch_top)], fill=color, width=line_w)

    img.save(ASSETS_DIR / filename)
    print(f"Salvo: {ASSETS_DIR / filename}")


def make_brandmark(filename, color, line_w=2, size=400):
    """Marca geometrica: grade 3x3 + arco no canto superior-esquerdo + curva N + diagonal."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    third = size // 3

    # Grade 3x3 (linhas externas e internas)
    for i in range(4):
        v = i * third if i < 3 else size - 1
        # linhas verticais
        d.line([(v, 0), (v, size - 1)], fill=color, width=line_w)
        # linhas horizontais
        d.line([(0, v), (size - 1, v)], fill=color, width=line_w)

    # Arco no canto superior-esquerdo (semicirculo de 180 a 270 na celula superior-esquerda x 2)
    # arco de 180 a 270 = quarto de circulo do canto superior-esquerdo ate o topo-meio
    # bbox: celula 2x2 superior-esquerda
    d.arc([(0, 0), (third * 2, third * 2)], start=180, end=270, fill=color, width=line_w)

    # Curva "N" - do topo da coluna do meio descendo, abrindo para o canto inferior-direito
    # bbox: amplo, criando uma curva que vai do topo-meio ate o bottom-direito
    d.arc([(third, -third), (size + third, size + third)],
          start=180, end=90, fill=color, width=line_w)

    # Diagonal do canto superior-direito ate a metade inferior-meio
    d.line([(size - 1, 0), (third * 2, size - 1)], fill=color, width=line_w)

    img.save(ASSETS_DIR / filename)
    print(f"Salvo: {ASSETS_DIR / filename}")


if __name__ == "__main__":
    make_bookmark_small()
    make_bookmark_large_outline()
    # NOTA: brandmark_white.png e brandmark_dark.png sao extraidos diretamente
    # do PDF do template via scripts/extrair_brandmarks_pdf.py — nao regerar
    # aqui para nao sobrescrever os assets fieis ao template oficial.
    print("\nAssets gerados em:", ASSETS_DIR.absolute())
