from PIL import Image

img_path = r"C:\Users\virei\.gemini\antigravity-ide\brain\4316859f-d16b-4703-bdef-6e5eb5bd9a86\sctt_icon_1790458110447.jpg"
img = Image.open(img_path)

# Resize to icon sizes
icon_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
img.save(r"C:\Users\virei\OneDrive\Documentos\Games\icon.ico", format="ICO", sizes=icon_sizes)
print("Icon created successfully.")
