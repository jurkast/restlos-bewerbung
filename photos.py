from io import BytesIO
from PIL import Image, ImageOps, ImageDraw
from storage import resolve


def _mask(size, shape, radius):
    """Anti-aliased alpha mask (drawn 4x larger, then scaled down)."""
    w, h = size
    big = Image.new('L', (w * 4, h * 4), 0)
    draw = ImageDraw.Draw(big)
    if shape == 'round':
        draw.ellipse((0, 0, w * 4 - 1, h * 4 - 1), fill=255)
    else:
        draw.rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), radius=int(min(w, h) * radius * 4), fill=255)
    return big.resize(size, Image.Resampling.LANCZOS)


def cropped(profile, rounded=0):
    """Cropped application photo as PNG. ``rounded`` (0–0.5) rounds the corners of
    portrait/square photos; used by the PDF templates, Word keeps square corners."""
    path = resolve(profile['photo'])
    with Image.open(path) as source:
        source.load()
        im = ImageOps.exif_transpose(source).convert('RGB')
    settings = profile.get('photoSettings', {})
    shape = settings.get('shape', 'portrait')
    ratio = 0.8 if shape == 'portrait' else 1
    w, h = im.size
    zoom = float(settings.get('zoom', 1))
    cw = min(w, h * ratio) / zoom
    ch = cw / ratio
    left = (w - cw) * float(settings.get('x', .5))
    top = (h - ch) * float(settings.get('y', .5))
    im = im.crop((round(left), round(top), round(left + cw), round(top + ch)))
    im = im.resize((640, 800) if shape == 'portrait' else (640, 640), Image.Resampling.LANCZOS)
    if shape == 'round' or rounded:
        im = im.convert('RGBA')
        im.putalpha(_mask(im.size, shape, rounded))
    data = BytesIO()
    im.save(data, format='PNG')
    data.seek(0)
    return data
