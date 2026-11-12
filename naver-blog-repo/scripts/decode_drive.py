"""Drive download_file_content 결과(JSON, base64)를 HEIC로 풀고 JPG로 변환한다.
사용법: python3 decode_drive.py <tool-results 폴더> <출력 폴더>"""
import base64, json, sys
from pathlib import Path
from PIL import Image, ImageOps
import pillow_heif
pillow_heif.register_heif_opener()
src, out = Path(sys.argv[1]), Path(sys.argv[2])
(out / "heic").mkdir(parents=True, exist_ok=True); (out / "jpg").mkdir(exist_ok=True)
for f in src.glob("mcp-Google_Drive-download_file_content-*.txt"):
    try:
        d = json.loads(f.read_text())
    except Exception as e:
        print("skip", f.name, e); continue
    if not d.get("mimeType", "image/").startswith("image/"):
        v = out / "video" / d["title"]; v.parent.mkdir(exist_ok=True)
        if not v.exists():
            v.write_bytes(base64.b64decode(d["content"]))
        continue
    h = out / "heic" / d["title"]
    if not h.exists():
        h.write_bytes(base64.b64decode(d["content"]))
    j = out / "jpg" / (h.stem + ".jpg")
    if not j.exists():
        ImageOps.exif_transpose(Image.open(h)).convert("RGB").save(j, quality=90)
print(sorted(p.stem for p in (out / "jpg").glob("*.jpg")))
