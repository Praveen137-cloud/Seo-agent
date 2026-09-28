import os
from PIL import Image, ImageDraw, ImageFont

def draw_seo_icon(size):
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Scale factor based on 128px design
    s = size / 128.0
    
    # 1. Rounded Rectangle background
    pad = int(4 * s)
    radius = int(28 * s)
    bg_box = [pad, pad, size - pad, size - pad]
    
    # Gradient/Solid dark slate background with red accent border
    bg_color = (15, 23, 42, 255) # Dark slate #0F172A
    border_color = (220, 38, 38, 255) # Red #DC2626
    
    draw.rounded_rectangle(bg_box, radius=radius, fill=bg_color, outline=border_color, width=max(1, int(3 * s)))
    
    # 2. Draw SEO Growth Bars inside
    # Bar 1
    draw.rounded_rectangle([int(32 * s), int(72 * s), int(42 * s), int(94 * s)], radius=int(2*s), fill=(239, 68, 68, 255))
    # Bar 2
    draw.rounded_rectangle([int(48 * s), int(56 * s), int(58 * s), int(94 * s)], radius=int(2*s), fill=(245, 158, 11, 255))
    # Bar 3
    draw.rounded_rectangle([int(64 * s), int(38 * s), int(74 * s), int(94 * s)], radius=int(2*s), fill=(16, 185, 129, 255))
    
    # 3. Magnifying Glass Lens
    center_x, center_y = int(76 * s), int(46 * s)
    r = int(22 * s)
    lens_box = [center_x - r, center_y - r, center_x + r, center_y + r]
    draw.ellipse(lens_box, outline=(255, 255, 255, 255), width=max(1, int(4.5 * s)))
    
    # Handle
    hx1, hy1 = center_x - int(15 * s), center_y + int(15 * s)
    hx2, hy2 = hx1 - int(14 * s), hy1 + int(14 * s)
    draw.line([hx1, hy1, hx2, hy2], fill=(255, 255, 255, 255), width=max(1, int(5 * s)))
    
    return img

os.makedirs('chrome-extension', exist_ok=True)

for sz in [16, 48, 128]:
    icon = draw_seo_icon(sz)
    icon.save(f'chrome-extension/icon{sz}.png')
    print(f"Generated chrome-extension/icon{sz}.png ({sz}x{sz})")

print("All icons successfully updated!")
