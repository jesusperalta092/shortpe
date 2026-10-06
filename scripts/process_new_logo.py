import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = r'c:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
SRC = os.path.join(ROOT, 'logo', 'Dramape-logo.jpeg')
WEB_PUBLIC = os.path.join(ROOT, 'web-next', 'public')
WEB_APP = os.path.join(ROOT, 'web-next', 'app')
WEB_IMG = os.path.join(WEB_PUBLIC, 'img')

os.makedirs(WEB_PUBLIC, exist_ok=True)
os.makedirs(WEB_APP, exist_ok=True)
os.makedirs(WEB_IMG, exist_ok=True)

# 1. Cargar imagen original sin ninguna alteración destructiva
src = Image.open(SRC).convert('RGB')
w, h = src.size

# Calcular bounding box del contenido real (máscaras y texto)
import numpy as np
arr = np.array(src)
mask = (arr[:, :, 0] < 240) | (arr[:, :, 1] < 240) | (arr[:, :, 2] < 240)
coords = np.argwhere(mask)
y0, x0 = coords.min(axis=0)
y1, x1 = coords.max(axis=0)

# =========================================================================
# A) LOGO COMPLETO RECORTADO (Máscaras + Texto DramaPe)
# =========================================================================
pad = 24
crop_x0 = max(0, x0 - pad)
crop_y0 = max(0, y0 - pad)
crop_x1 = min(w, x1 + pad)
crop_y1 = min(h, y1 + pad)
full_crop = src.crop((crop_x0, crop_y0, crop_x1, crop_y1))

# Guardar versiones completas de alta fidelidad
full_crop.save(os.path.join(WEB_PUBLIC, 'logo-full.png'), 'PNG')
full_crop.save(os.path.join(ROOT, 'logo-full.png'), 'PNG')
full_crop.save(os.path.join(WEB_PUBLIC, 'logo.png'), 'PNG')
full_crop.save(os.path.join(ROOT, 'logo.png'), 'PNG')
full_crop.save(os.path.join(WEB_APP, 'icon.png'), 'PNG')

# =========================================================================
# B) ISOTIPO / ICONO CUADRADO (Solo las máscaras teatrales DP)
# =========================================================================
mask_icon = (arr[:2070, :, 0] < 240) | (arr[:2070, :, 1] < 240) | (arr[:2070, :, 2] < 240)
icoords = np.argwhere(mask_icon)
iy0, ix0 = icoords.min(axis=0)
iy1, ix1 = icoords.max(axis=0)

iw = ix1 - ix0
ih = iy1 - iy0
side = max(iw, ih)
# Margen elegante del 6% para que el isotipo respire
margin = int(side * 0.06)
cx = (ix0 + ix1) // 2
cy = (iy0 + iy1) // 2
half = (side // 2) + margin

crop_icon_box = (
    max(0, cx - half),
    max(0, cy - half),
    min(w, cx + half),
    min(h, cy + half)
)
icon_crop = src.crop(crop_icon_box)
icon_512 = icon_crop.resize((512, 512), Image.Resampling.LANCZOS)

# Guardar Icono
icon_512.save(os.path.join(WEB_PUBLIC, 'logo-icon.png'), 'PNG')
icon_512.save(os.path.join(ROOT, 'logo-icon.png'), 'PNG')

# =========================================================================
# C) FAVICONS MULTI-RESOLUCIÓN PARA TODAS LAS PESTAÑAS Y NAVEGADORES
# =========================================================================
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
icon_512.save(os.path.join(WEB_PUBLIC, 'favicon.ico'), format='ICO', sizes=ico_sizes)
icon_512.save(os.path.join(ROOT, 'favicon.ico'), format='ICO', sizes=ico_sizes)
icon_512.save(os.path.join(WEB_APP, 'favicon.ico'), format='ICO', sizes=ico_sizes)

fav_32 = icon_512.resize((32, 32), Image.Resampling.LANCZOS)
fav_32.save(os.path.join(WEB_PUBLIC, 'favicon-32x32.png'), 'PNG')

fav_16 = icon_512.resize((16, 16), Image.Resampling.LANCZOS)
fav_16.save(os.path.join(WEB_PUBLIC, 'favicon-16x16.png'), 'PNG')

apple_icon = icon_512.resize((180, 180), Image.Resampling.LANCZOS)
apple_icon.save(os.path.join(WEB_PUBLIC, 'apple-touch-icon.png'), 'PNG')
apple_icon.save(os.path.join(ROOT, 'apple-touch-icon.png'), 'PNG')
apple_icon.save(os.path.join(WEB_APP, 'apple-icon.png'), 'PNG')

icon_192 = icon_512.resize((192, 192), Image.Resampling.LANCZOS)
icon_192.save(os.path.join(WEB_PUBLIC, 'icon-192.png'), 'PNG')

icon_512.save(os.path.join(WEB_PUBLIC, 'icon-512.png'), 'PNG')

# =========================================================================
# D) OPEN GRAPH SOCIAL BANNER PARA WHATSAPP / FACEBOOK / TWITTER (1200 x 630)
# =========================================================================
# Canvas 1200x630 nítido, fondo blanco puro con colores intensos y contraste 100%
og_w, og_h = 1200, 630
og = Image.new('RGB', (og_w, og_h), '#ffffff')

# Escalar el logo completo a un tamaño amplio y balanceado (alto = 490px)
target_h = 490
ratio = target_h / full_crop.height
target_w = int(full_crop.width * ratio)
scaled_logo = full_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)

pos_x = (og_w - target_w) // 2
pos_y = (og_h - target_h) // 2
og.paste(scaled_logo, (pos_x, pos_y))

# Guardar en todas las ubicaciones OpenGraph
og.save(os.path.join(WEB_PUBLIC, 'og-image.jpg'), 'JPEG', quality=98)
og.save(os.path.join(WEB_PUBLIC, 'og-image.png'), 'PNG')
og.save(os.path.join(WEB_IMG, 'og-banner.jpg'), 'JPEG', quality=98)
og.save(os.path.join(WEB_APP, 'opengraph-image.png'), 'PNG')
og.save(os.path.join(ROOT, 'og-image.jpg'), 'JPEG', quality=98)
og.save(os.path.join(ROOT, 'og-image.png'), 'PNG')

print("Generacion impecable de todos los assets completada con exito!")
