import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = r'c:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
SRC_LOGO = os.path.join(ROOT, 'logo', 'Dramape.png')
WEB_PUBLIC = os.path.join(ROOT, 'web-next', 'public')
WEB_APP = os.path.join(ROOT, 'web-next', 'app')
WEB_IMG = os.path.join(WEB_PUBLIC, 'img')

os.makedirs(WEB_PUBLIC, exist_ok=True)
os.makedirs(WEB_APP, exist_ok=True)
os.makedirs(WEB_IMG, exist_ok=True)

# 1. Cargar imagen original
src = Image.open(SRC_LOGO).convert('RGBA')
w, h = src.size

# Square crop
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
square_logo = src.crop((left, top, left + side, top + side))

# 2. Guardar Logo PNG de alta resolucion (512x512 y original)
logo_512 = square_logo.resize((512, 512), Image.Resampling.LANCZOS)
logo_512.save(os.path.join(WEB_PUBLIC, 'logo.png'), 'PNG')
logo_512.save(os.path.join(ROOT, 'logo.png'), 'PNG')
logo_512.save(os.path.join(WEB_APP, 'icon.png'), 'PNG')

# 3. Favicon ICO multi-resolucion (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
square_logo.save(os.path.join(WEB_PUBLIC, 'favicon.ico'), format='ICO', sizes=ico_sizes)
square_logo.save(os.path.join(ROOT, 'favicon.ico'), format='ICO', sizes=ico_sizes)
square_logo.save(os.path.join(WEB_APP, 'favicon.ico'), format='ICO', sizes=ico_sizes)

# 4. Favicon PNGs y Apple Touch Icon
fav_32 = square_logo.resize((32, 32), Image.Resampling.LANCZOS)
fav_32.save(os.path.join(WEB_PUBLIC, 'favicon-32x32.png'), 'PNG')

fav_16 = square_logo.resize((16, 16), Image.Resampling.LANCZOS)
fav_16.save(os.path.join(WEB_PUBLIC, 'favicon-16x16.png'), 'PNG')

apple_icon = square_logo.resize((180, 180), Image.Resampling.LANCZOS)
apple_icon.save(os.path.join(WEB_PUBLIC, 'apple-touch-icon.png'), 'PNG')
apple_icon.save(os.path.join(ROOT, 'apple-touch-icon.png'), 'PNG')
apple_icon.save(os.path.join(WEB_APP, 'apple-icon.png'), 'PNG')

icon_192 = square_logo.resize((192, 192), Image.Resampling.LANCZOS)
icon_192.save(os.path.join(WEB_PUBLIC, 'icon-192.png'), 'PNG')

icon_512 = square_logo.resize((512, 512), Image.Resampling.LANCZOS)
icon_512.save(os.path.join(WEB_PUBLIC, 'icon-512.png'), 'PNG')

# 5. Generar Open Graph Social Banner (1200 x 630) optimizado para WhatsApp / Facebook / Twitter / Telegram
og_w, og_h = 1200, 630
og_bg = Image.new('RGB', (og_w, og_h), '#0a0a0f')
draw = ImageDraw.Draw(og_bg)

for r in range(450, 0, -5):
    alpha = int((1 - (r / 450.0)) * 40)
    draw.ellipse([og_w//2 - r*1.5, og_h//2 - r, og_w//2 + r*1.5, og_h//2 + r], fill=(alpha + 10, alpha // 4, alpha // 4))

# Glow detras del logo
glow = Image.new('RGBA', (og_w, og_h), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow)
glow_draw.ellipse([og_w//2 - 220, og_h//2 - 200, og_w//2 + 220, og_h//2 + 180], fill=(180, 20, 30, 90))
glow = glow.filter(ImageFilter.GaussianBlur(60))
og_bg.paste(glow, (0, 0), glow)

# Logo central
og_logo_size = 380
og_logo = square_logo.resize((og_logo_size, og_logo_size), Image.Resampling.LANCZOS)

# Sombra suave
shadow = Image.new('RGBA', (og_logo_size + 40, og_logo_size + 40), (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_draw.rounded_rectangle([15, 15, og_logo_size + 25, og_logo_size + 25], radius=60, fill=(0, 0, 0, 180))
shadow = shadow.filter(ImageFilter.GaussianBlur(25))

logo_x = (og_w - og_logo_size) // 2
logo_y = (og_h - og_logo_size) // 2 - 20

og_bg.paste(shadow, (logo_x - 20, logo_y - 20), shadow)
og_bg.paste(og_logo, (logo_x, logo_y), og_logo)

# Guardar OG banner
og_bg.save(os.path.join(WEB_PUBLIC, 'og-image.jpg'), 'JPEG', quality=95)
og_bg.save(os.path.join(WEB_PUBLIC, 'og-image.png'), 'PNG')
og_bg.save(os.path.join(WEB_IMG, 'og-banner.jpg'), 'JPEG', quality=95)
og_bg.save(os.path.join(WEB_APP, 'opengraph-image.png'), 'PNG')
og_bg.save(os.path.join(ROOT, 'og-image.jpg'), 'JPEG', quality=95)
og_bg.save(os.path.join(ROOT, 'og-image.png'), 'PNG')

print("Generacion de iconos, logo y banner OpenGraph completada con exito!")
