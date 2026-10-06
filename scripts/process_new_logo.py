import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT = r'c:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
SRC = os.path.join(ROOT, 'logo', 'Dramape-logo.jpeg')
WEB_PUBLIC = os.path.join(ROOT, 'web-next', 'public')
WEB_APP = os.path.join(ROOT, 'web-next', 'app')
WEB_IMG = os.path.join(WEB_PUBLIC, 'img')

os.makedirs(WEB_PUBLIC, exist_ok=True)
os.makedirs(WEB_APP, exist_ok=True)
os.makedirs(WEB_IMG, exist_ok=True)

# 1. Cargar imagen original con OpenCV
bgr = cv2.imread(SRC)
h, w = bgr.shape[:2]

# Segmentación precisa del fondo exterior (FloodFill desde esquinas)
flood_mask = np.zeros((h + 2, w + 2), np.uint8)
flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY
# Tolerancia de 18 para limpiar artefactos JPEG del blanco
cv2.floodFill(bgr, flood_mask, (0, 0), (0, 0, 0), (18, 18, 18), (18, 18, 18), flags)
# También probar las otras 3 esquinas por si hay alguna desconexión
cv2.floodFill(bgr, flood_mask, (w-1, 0), (0, 0, 0), (18, 18, 18), (18, 18, 18), flags)
cv2.floodFill(bgr, flood_mask, (0, h-1), (0, 0, 0), (18, 18, 18), (18, 18, 18), flags)
cv2.floodFill(bgr, flood_mask, (w-1, h-1), (0, 0, 0), (18, 18, 18), (18, 18, 18), flags)

bg_mask = flood_mask[1:-1, 1:-1]
# fg_mask: 255 para el logo, 0 para el fondo blanco exterior
fg_mask = (bg_mask == 0).astype(np.uint8) * 255

# Suavizado de bordes anti-aliasing
alpha_matte = cv2.GaussianBlur(fg_mask, (3, 3), 0)

# Convertir BGR a RGBA con alpha_matte
rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
rgba = np.dstack((rgb, alpha_matte))
pil_full_transparent = Image.fromarray(rgba)

# 2. Bounding Boxes de los componentes
coords = np.argwhere(fg_mask > 0)
y0, x0 = coords.min(axis=0)
y1, x1 = coords.max(axis=0)

# A) LOGO COMPLETO RECORTADO (Máscaras + Texto DramaPe)
pad = 20
crop_x0 = max(0, x0 - pad)
crop_y0 = max(0, y0 - pad)
crop_x1 = min(w, x1 + pad)
crop_y1 = min(h, y1 + pad)
cropped_full = pil_full_transparent.crop((crop_x0, crop_y0, crop_x1, crop_y1))

# Guardar versiones del logo completo
cropped_full.save(os.path.join(WEB_PUBLIC, 'logo-full.png'), 'PNG')
cropped_full.save(os.path.join(ROOT, 'logo-full.png'), 'PNG')
cropped_full.save(os.path.join(WEB_PUBLIC, 'logo.png'), 'PNG')
cropped_full.save(os.path.join(ROOT, 'logo.png'), 'PNG')
cropped_full.save(os.path.join(WEB_APP, 'icon.png'), 'PNG')

# B) ICONO SOLAMENTE (Máscaras DP teatrales, arriba del texto)
# El texto empieza alrededor de y = 2070
icon_coords = np.argwhere(fg_mask[:2070, :] > 0)
iy0, ix0 = icon_coords.min(axis=0)
iy1, ix1 = icon_coords.max(axis=0)

# Hacer crop cuadrado centrado con margen equilibrado (8%)
iw = ix1 - ix0
ih = iy1 - iy0
iside = max(iw, ih)
icenter_x = (ix0 + ix1) // 2
icenter_y = (iy0 + iy1) // 2

# Añadir 10% de padding para que respire en favicons
margin = int(iside * 0.08)
box_half = (iside // 2) + margin

crop_icon_box = (
    max(0, icenter_x - box_half),
    max(0, icenter_y - box_half),
    min(w, icenter_x + box_half),
    min(h, icenter_y + box_half)
)
cropped_icon = pil_full_transparent.crop(crop_icon_box)
cropped_icon_sq = cropped_icon.resize((512, 512), Image.Resampling.LANCZOS)

# Guardar Icono transparente
cropped_icon_sq.save(os.path.join(WEB_PUBLIC, 'logo-icon.png'), 'PNG')
cropped_icon_sq.save(os.path.join(ROOT, 'logo-icon.png'), 'PNG')

# 3. FAVICONS MULTI-RESOLUCIÓN PARA LA PESTAÑA DEL NAVEGADOR
# Generar favicon.ico con múltiples capas
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
cropped_icon_sq.save(os.path.join(WEB_PUBLIC, 'favicon.ico'), format='ICO', sizes=ico_sizes)
cropped_icon_sq.save(os.path.join(ROOT, 'favicon.ico'), format='ICO', sizes=ico_sizes)
cropped_icon_sq.save(os.path.join(WEB_APP, 'favicon.ico'), format='ICO', sizes=ico_sizes)

fav_32 = cropped_icon_sq.resize((32, 32), Image.Resampling.LANCZOS)
fav_32.save(os.path.join(WEB_PUBLIC, 'favicon-32x32.png'), 'PNG')

fav_16 = cropped_icon_sq.resize((16, 16), Image.Resampling.LANCZOS)
fav_16.save(os.path.join(WEB_PUBLIC, 'favicon-16x16.png'), 'PNG')

apple_icon = cropped_icon_sq.resize((180, 180), Image.Resampling.LANCZOS)
apple_icon.save(os.path.join(WEB_PUBLIC, 'apple-touch-icon.png'), 'PNG')
apple_icon.save(os.path.join(ROOT, 'apple-touch-icon.png'), 'PNG')
apple_icon.save(os.path.join(WEB_APP, 'apple-icon.png'), 'PNG')

icon_192 = cropped_icon_sq.resize((192, 192), Image.Resampling.LANCZOS)
icon_192.save(os.path.join(WEB_PUBLIC, 'icon-192.png'), 'PNG')

icon_512 = cropped_icon_sq.resize((512, 512), Image.Resampling.LANCZOS)
icon_512.save(os.path.join(WEB_PUBLIC, 'icon-512.png'), 'PNG')

# 4. LOGO PARA EL HEADER (Píldora / Contenedor ovalado refinado)
# Crear una versión con contenedor ovalado/curvo suave
badge_w, badge_h = 320, 110
badge_img = Image.new('RGBA', (badge_w, badge_h), (0, 0, 0, 0))
b_draw = ImageDraw.Draw(badge_img)

# Fondo ovalado suave con gradiente sutil blanco/luz
b_draw.rounded_rectangle([2, 2, badge_w-3, badge_h-3], radius=26, fill=(255, 255, 255, 245), outline=(230, 230, 235, 255), width=2)

# Insertar el logo completo dentro del badge
target_h = badge_h - 20
ratio = target_h / cropped_full.height
target_w = int(cropped_full.width * ratio)
scaled_logo = cropped_full.resize((target_w, target_h), Image.Resampling.LANCZOS)
bx = (badge_w - target_w) // 2
by = (badge_h - target_h) // 2
badge_img.paste(scaled_logo, (bx, by), scaled_logo)
badge_img.save(os.path.join(WEB_PUBLIC, 'logo-badge.png'), 'PNG')
badge_img.save(os.path.join(ROOT, 'logo-badge.png'), 'PNG')

# 5. OPEN GRAPH SOCIAL BANNER PARA WHATSAPP / FACEBOOK / TWITTER (1200 x 630)
# Queremos que en WhatsApp salga extensa, limpia, nítida y perfectamente proporcionada
og_w, og_h = 1200, 630

# Versión 1: Clean White Minimalist & Cinematic Framing (la que el usuario diseñó)
og_canvas = Image.new('RGB', (og_w, og_h), '#ffffff')
og_draw = ImageDraw.Draw(og_canvas)

# Marco sutil / viñeta elegante en los bordes
for r in range(12, 0, -2):
    og_draw.rectangle([r, r, og_w - r, og_h - r], outline=(245 + r//2, 245 + r//2, 248 + r//2))

# Redimensionar el logo completo para que ocupe una proporción áurea central (~440px de alto)
target_og_h = 430
og_ratio = target_og_h / cropped_full.height
target_og_w = int(cropped_full.width * og_ratio)
og_logo_scaled = cropped_full.resize((target_og_w, target_og_h), Image.Resampling.LANCZOS)

og_x = (og_w - target_og_w) // 2
og_y = (og_h - target_og_h) // 2

# Pegar en el centro del canvas 1200x630
og_canvas.paste(og_logo_scaled, (og_x, og_y), og_logo_scaled)

# Guardar OG banner en todas las ubicaciones
og_canvas.save(os.path.join(WEB_PUBLIC, 'og-image.jpg'), 'JPEG', quality=96)
og_canvas.save(os.path.join(WEB_PUBLIC, 'og-image.png'), 'PNG')
og_canvas.save(os.path.join(WEB_IMG, 'og-banner.jpg'), 'JPEG', quality=96)
og_canvas.save(os.path.join(WEB_APP, 'opengraph-image.png'), 'PNG')
og_canvas.save(os.path.join(ROOT, 'og-image.jpg'), 'JPEG', quality=96)
og_canvas.save(os.path.join(ROOT, 'og-image.png'), 'PNG')

print("Generacion y recorte de todos los assets completados con exito!")
