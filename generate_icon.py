import os
from PIL import Image, ImageDraw

def create_app_icon():
    os.makedirs("assets", exist_ok=True)
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded rect
    draw.rounded_rectangle([12, 12, 244, 244], radius=48, fill=(18, 24, 38, 255), outline=(46, 117, 246, 220), width=6)
    
    # Inner accent border
    draw.rounded_rectangle([20, 20, 236, 236], radius=40, outline=(15, 60, 130, 160), width=3)

    # Stylized Ethernet / RJ45 Port + Shield icon
    shield_pts = [
        (128, 48),  # top center
        (190, 75),  # top right
        (185, 145), # mid right
        (128, 208), # bottom point
        (71, 145),  # mid left
        (66, 75),   # top left
    ]
    draw.polygon(shield_pts, fill=(24, 38, 64, 240), outline=(56, 189, 248, 255))
    
    # Port / plug opening in center
    draw.rectangle([96, 105, 160, 160], fill=(10, 15, 26, 255), outline=(56, 189, 248, 200), width=3)
    # Notch at the bottom
    draw.rectangle([112, 152, 144, 165], fill=(56, 189, 248, 255))
    
    # 4 pin contacts inside port
    pin_colors = [(52, 211, 153), (56, 189, 248), (96, 165, 250), (167, 139, 250)]
    for i, x in enumerate([104, 118, 134, 148]):
        draw.line([(x, 112), (x, 126)], fill=pin_colors[i], width=3)
        
    # Activity indicator dot (green glowing LED)
    draw.ellipse([122, 68, 134, 80], fill=(52, 211, 153, 255), outline=(16, 185, 129, 255), width=2)

    # Save PNG
    png_path = os.path.join("assets", "icon.png")
    img.save(png_path, format="PNG")

    # Save multi-size ICO
    ico_path = os.path.join("assets", "icon.ico")
    img.save(ico_path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Icons generated: {png_path}, {ico_path}")

if __name__ == "__main__":
    create_app_icon()
