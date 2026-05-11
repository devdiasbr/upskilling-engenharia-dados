#!/usr/bin/env python3
"""Extrai os brandmarks (canto inferior-direito) das páginas 6 e 12 do PDF
do template NTT DATA UNIVERSITY e salva como PNGs com fundo transparente."""

from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "docs" / "template" / "NTT DATA UNIVERSITY template dark and light.pdf"
ASSETS_DIR = ROOT / "assets" / "ntt-template"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Páginas (0-indexed)
PAGE_DARK_CLOSING = 5    # página 6 → closing dark
PAGE_LIGHT_CLOSING = 11  # página 12 → closing light

# Render scale
SCALE = 4  # 4x DPI para alta qualidade


def render_page(pdf_path: Path, page_idx: int, scale: float = 4) -> Image.Image:
    doc = fitz.open(str(pdf_path))
    page = doc[page_idx]
    matrix = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def crop_brandmark(img: Image.Image) -> Image.Image:
    """Recorta o canto inferior-direito onde fica o brandmark.
    Slide é ~16:9. Brandmark ocupa o canto inferior-direito.
    Proporções verificadas visualmente na página 6 e 12 do PDF.
    x: de 63% até 100% (evita o texto 'NTT DATA UNIVERSITY' centralizado)
    y: de 53% até 100% (abaixo da linha de base do texto)"""
    w, h = img.size
    left   = int(w * 0.63)
    top    = int(h * 0.53)
    right  = w
    bottom = h
    return img.crop((left, top, right, bottom))


def make_transparent_dark_bg(img: Image.Image) -> Image.Image:
    """Converte fundo navy escuro em transparente e mantém pixels claros (brancos).
    Para uso no brandmark da página dark (outline branco em fundo navy)."""
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Calcular luminância
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < 80:
                # Pixel escuro (navy) → transparente
                pixels[x, y] = (255, 255, 255, 0)
            else:
                # Pixel claro (branco do outline) → branco opaco com alpha
                # baseado na luminância (anti-aliasing preservado)
                alpha = min(255, int((lum - 80) * 255 / 175))
                pixels[x, y] = (255, 255, 255, alpha)
    return img


def make_transparent_light_bg(img: Image.Image) -> Image.Image:
    """Converte fundo branco em transparente e mantém pixels escuros (outline).
    Para uso no brandmark da página light (outline preto em fundo branco)."""
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > 220:
                # Pixel claro (branco) → transparente
                pixels[x, y] = (0, 0, 0, 0)
            else:
                # Pixel escuro (outline) → preto opaco com alpha proporcional
                alpha = min(255, int((220 - lum) * 255 / 220))
                # Cor de outline: dark slate (50, 60, 80) para combinar com texto navy
                pixels[x, y] = (50, 60, 80, alpha)
    return img


def main():
    print(f"PDF: {PDF_PATH}")
    print(f"Existe? {PDF_PATH.exists()}")
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF não encontrado: {PDF_PATH}")

    # === Brandmark WHITE (de página 6 — closing dark) ===
    print("\n[1/2] Extraindo brandmark white (página 6, fundo dark)...")
    page_dark = render_page(PDF_PATH, PAGE_DARK_CLOSING, SCALE)
    print(f"  Página renderizada: {page_dark.size}")
    crop_dark = crop_brandmark(page_dark)
    print(f"  Recorte: {crop_dark.size}")
    bm_white = make_transparent_dark_bg(crop_dark)
    bm_white_path = ASSETS_DIR / "brandmark_white.png"
    bm_white.save(bm_white_path)
    print(f"  Salvo: {bm_white_path} ({bm_white_path.stat().st_size} bytes)")

    # === Brandmark DARK (de página 12 — closing light) ===
    print("\n[2/2] Extraindo brandmark dark (página 12, fundo light)...")
    page_light = render_page(PDF_PATH, PAGE_LIGHT_CLOSING, SCALE)
    print(f"  Página renderizada: {page_light.size}")
    crop_light = crop_brandmark(page_light)
    print(f"  Recorte: {crop_light.size}")
    bm_dark = make_transparent_light_bg(crop_light)
    bm_dark_path = ASSETS_DIR / "brandmark_dark.png"
    bm_dark.save(bm_dark_path)
    print(f"  Salvo: {bm_dark_path} ({bm_dark_path.stat().st_size} bytes)")

    print("\nPronto. Os brandmarks foram extraídos do template oficial.")


if __name__ == "__main__":
    main()
