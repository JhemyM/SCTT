from PIL import Image

img_path = r"C:\Users\virei\.gemini\antigravity-ide\brain\4316859f-d16b-4703-bdef-6e5eb5bd9a86\sctt_icon_1790458110447.jpg"
out_path = r"C:\Users\virei\OneDrive\Documentos\Games\SCTT_Cover.png"

img = Image.open(img_path)
img.save(out_path, format="PNG")
print(f"Cover exported successfully to {out_path}")
